"""End to end against real galago-tools servers in simulated mode.

Needs ``galago-serve`` from a galago-tools install (Python 3.9): set
GALAGO_SERVE to its path, or create ``.venv-galago`` in this repo::

    python3.9 -m venv .venv-galago && .venv-galago/bin/pip install galago-tools

Skipped when neither is available.
"""

import json
import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path

import pytest

from rhylthyme_galago import GrpcToolClient, build_command

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def _galago_serve():
    candidates = [os.environ.get("GALAGO_SERVE"), ROOT / ".venv-galago" / "bin" / "galago-serve"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return shutil.which("galago-serve")


def _free_port():
    with socket.socket() as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


@pytest.fixture
def bioshake_server(tmp_path):
    serve = _galago_serve()
    if not serve:
        pytest.skip("galago-serve not found (set GALAGO_SERVE or create .venv-galago)")
    port = _free_port()
    log = open(tmp_path / "galago-serve.log", "w")
    # galago-serve hands the server to a child process and may exit, so it
    # gets its own process group and the whole group is stopped afterwards.
    proc = subprocess.Popen(
        [serve, "--port", str(port), "--tool", "bioshake"],
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    client = GrpcToolClient(f"localhost:{port}", connect_timeout=1.0)
    try:
        deadline = time.time() + 30
        while client.status().status == "OFFLINE":
            if time.time() > deadline:
                pytest.fail(f"galago-serve did not start; see {log.name}")
            time.sleep(0.2)
        yield port
    finally:
        client.close()
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(5)
        except ProcessLookupError:
            pass
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
        log.close()


def test_simulated_bioshake_replies(bioshake_server):
    from rhylthyme_galago import InstrumentExecutor, load_workcell

    workcell = load_workcell(
        {"tools": [{"name": "shaker", "type": "bioshake", "host": "localhost",
                    "port": bioshake_server, "config": {"com_port": "COM3"}}]}
    )
    executor = InstrumentExecutor(workcell)
    try:
        [check] = executor.prepare(["shaker"])
        assert check.ready and check.status.status == "SIMULATED"
        client = executor.client("shaker")
        command = build_command("bioshake", "start_shake", {"speed": 1000, "duration": 1})
        assert client.estimate(command)[0] == 1
        started = time.time()
        assert client.execute(command).ok
        assert time.time() - started >= 0.9  # simulated tools sleep the estimate
    finally:
        executor.shutdown()


def test_example_program_runs_to_completion(bioshake_server, tmp_path):
    runner_mod = pytest.importorskip("rhylthyme_cli_runner.program_runner")
    from rhylthyme_cli_runner.instruments import attach_instruments

    workcell = json.loads((EXAMPLES / "workcell-simulated.json").read_text())
    workcell["tools"][0]["port"] = bioshake_server
    program = json.loads((EXAMPLES / "shake-plate.json").read_text())

    runner = runner_mod.ProgramRunner(program, time_scale=10.0)
    ended_by = {}
    runner.add_event_listener(
        lambda kind, data: ended_by.update({data["step_id"]: data["ended_by"]})
        if kind == "step_completed"
        else None
    )
    session = attach_instruments(runner, workcell)
    try:
        runner.start()
        runner.command_queue.put("start_program")
        deadline = time.time() + 30
        while runner.is_running or not runner.program_started:
            runner.update()
            assert time.time() < deadline, {s: st.status for s, st in runner.steps.items()}
            time.sleep(0.02)
    finally:
        session.shutdown()

    Completed = runner_mod.StepStatus.COMPLETED
    assert all(step.status == Completed for step in runner.steps.values())
    assert ended_by["shake"] == "instrument"
    shake = runner.steps["shake"]
    # The Bioshake was asked for 5 s; at 10x that is ~50 s on the program clock.
    assert shake.end_time - shake.start_time >= 40


def _shaker(port):
    from rhylthyme_galago import InstrumentExecutor, load_workcell

    workcell = load_workcell(
        {"tools": [{"name": "shaker", "type": "bioshake", "host": "localhost",
                    "port": port, "config": {"com_port": "COM3"}}]}
    )
    executor = InstrumentExecutor(workcell)
    assert executor.prepare(["shaker"])[0].ready
    return executor


def test_timeout_against_a_real_tool(bioshake_server):
    import threading

    executor = _shaker(bioshake_server)
    replies = []
    done = threading.Event()
    try:
        executor.submit(
            "shake",
            {"tool": "shaker", "command": "start_shake",
             "params": {"speed": 500, "duration": 20}, "timeoutSeconds": 1},
            lambda key, reply: (replies.append(reply), done.set()),
        )
        assert done.wait(5)
        assert replies[0].code == "TIMEOUT"
    finally:
        executor.shutdown()


def test_shutdown_mid_command_leaves_no_worker_threads(bioshake_server):
    import threading

    executor = _shaker(bioshake_server)
    executor.submit(
        "shake",
        {"tool": "shaker", "command": "start_shake", "params": {"speed": 500, "duration": 30}},
        lambda key, reply: None,
    )
    time.sleep(0.5)
    assert executor.shutdown() == ["shake"]
    deadline = time.time() + 3
    while any(t.name.startswith("rhylthyme-galago") for t in threading.enumerate()):
        assert time.time() < deadline, "worker thread still blocked in the gRPC call"
        time.sleep(0.05)


def test_fill_durations_asks_the_real_tool(bioshake_server):
    from rhylthyme_galago import fill_durations, load_workcell

    workcell = load_workcell(
        {"tools": [{"name": "shaker", "type": "bioshake", "host": "localhost",
                    "port": bioshake_server}]}
    )
    program = json.loads((EXAMPLES / "shake-plate.json").read_text())

    # galago answers NOT_READY until a tool is configured; planning never
    # configures tools (that could flip a live tool to simulated), so it
    # falls back to the command's params.
    _, [estimate] = fill_durations(program, workcell)
    assert (estimate.source, estimate.seconds) == ("params", 5.0)

    _shaker(bioshake_server).shutdown()  # configured (simulated), as in a run
    _, [estimate] = fill_durations(program, workcell)
    assert (estimate.step_id, estimate.source, estimate.seconds) == ("shake", "tool", 5.0)
