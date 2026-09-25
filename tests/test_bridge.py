"""The web bridge publisher, against a fake PostgREST."""

import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

import pytest

from rhylthyme_galago import load_workcell
from rhylthyme_galago.bridge import (
    BridgeError,
    Publisher,
    SupabaseRest,
    bridge_id_for,
    run_status,
    scrubber,
    snapshot,
    user_id_from_token,
)

WORKCELL = load_workcell(
    {
        "id": "bench",
        "name": "Bench 1",
        "tools": [
            {"name": "shaker", "type": "bioshake", "host": "10.20.30.40", "port": 50710,
             "config": {"com_port": "COM7"}},
        ],
    }
)


def token(sub="user-123"):
    body = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).decode().rstrip("=")
    return f"h.{body}.s"


class FakeRest:
    def __init__(self, status=204):
        self.requests = []
        self.status = status
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _handle(self):
                length = int(self.headers.get("Content-Length") or 0)
                outer.requests.append(
                    {"method": self.command, "path": self.path,
                     "headers": {k.lower(): v for k, v in self.headers.items()}, "body": json.loads(self.rfile.read(length) or b"null")}
                )
                self.send_response(outer.status)
                self.end_headers()
                if outer.status >= 400:
                    self.wfile.write(b'{"message":"relation \\"bridges\\" does not exist"}')

            do_POST = do_PATCH = _handle

            def log_message(self, *a):
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()


@pytest.fixture
def fake():
    f = FakeRest()
    yield f
    f.close()


def step(step_id, status="PENDING", tool=None, failure=None, start=None, end=None):
    return SimpleNamespace(
        step_id=step_id, name=step_id.title(), track_id="bench",
        status=SimpleNamespace(value=status),
        instrument={"tool": tool, "command": "start_shake"} if tool else None,
        failure=failure, start_time=start, end_time=end, abort_reason=None,
    )


def runner(*steps, **kw):
    base = dict(steps={s.step_id: s for s in steps}, program_start_time=1000.0,
                current_time=1012.5, is_running=True, is_paused=False,
                failed_steps=[], program_abort_reason=None)
    base.update(kw)
    return SimpleNamespace(**base)


def test_user_id_from_token():
    assert user_id_from_token(token("abc")) == "abc"
    with pytest.raises(BridgeError, match="rhylthyme login"):
        user_id_from_token("not-a-jwt")


def test_bridge_id_is_stable_per_workcell(tmp_path):
    path = tmp_path / "bridges.json"
    first = bridge_id_for(WORKCELL, path)
    assert bridge_id_for(WORKCELL, path) == first
    other = load_workcell({"id": "bench-2", "tools": [{"name": "s", "type": "bioshake", "host": "h", "port": 1}]})
    assert bridge_id_for(other, path) != first


def test_scrubber_removes_addresses_and_config():
    scrub = scrubber(WORKCELL)
    text = "UNAVAILABLE: failed to connect to 10.20.30.40:50710 (10.20.30.40) via COM7"
    assert scrub(text) == "UNAVAILABLE: failed to connect to shaker (shaker) via <config>"


def test_snapshot_is_an_allowlist():
    failure = {"code": "UNREACHABLE", "errorMessage": "connect 10.20.30.40:50710 refused"}
    r = runner(
        step("load", "COMPLETED", start=1000.0, end=1003.0),
        step("shake", "RUNNING", tool="shaker", start=1003.0),
        step("home", "FAILED", tool="shaker", failure=failure),
        failed_steps=["home"],
    )
    snap = snapshot(r, scrubber(WORKCELL))
    by_id = {s["stepId"]: s for s in snap["steps"]}
    assert snap["clock"] == 12.5
    assert (by_id["load"]["start"], by_id["load"]["end"]) == (0.0, 3.0)
    assert by_id["shake"]["waitingOn"] == "shaker"
    assert by_id["home"]["failure"] == {"code": "UNREACHABLE", "errorMessage": "connect shaker refused"}
    assert run_status(r) == "failed"


def test_run_status():
    assert run_status(runner(step("a", "COMPLETED"))) == "completed"
    assert run_status(runner(step("a"), is_paused=True)) == "paused"
    assert run_status(runner(step("a"), program_abort_reason="x")) == "aborted"
    assert run_status(runner(step("a"), is_running=False)) == "idle"
    assert run_status(runner(step("a"))) == "running"


def publisher(fake, r, **kw):
    rest = SupabaseRest(fake.url, "anon-key", lambda: token())
    args = dict(rest=rest, bridge_id="b-1", user_id="user-123", workcell=WORKCELL,
                tools=[{"name": "shaker", "type": "bioshake", "status": "SIMULATED"}],
                program={"programId": "p", "name": "Shake"}, mode="simulated",
                allows_live=False, version="0.1.0a1")
    args.update(kw)
    return Publisher(r, **args)


def test_publishes_bridge_and_state_as_the_user(fake):
    r = runner(step("shake", "RUNNING", tool="shaker", start=1000.0))
    p = publisher(fake, r)
    p.publish_once(force=True)
    bridges, state = fake.requests
    assert (bridges["method"], bridges["path"]) == ("POST", "/rest/v1/bridges?on_conflict=id")
    assert state["path"] == "/rest/v1/bridge_state?on_conflict=bridge_id"
    for req in fake.requests:
        assert req["headers"]["authorization"] == f"Bearer {token()}"
        assert req["headers"]["apikey"] == "anon-key"
        assert "merge-duplicates" in req["headers"]["prefer"]
    assert bridges["body"]["user_id"] == "user-123"
    assert bridges["body"]["tools"] == [{"name": "shaker", "type": "bioshake", "status": "SIMULATED"}]
    assert state["body"]["status"] == "running"
    assert state["body"]["state"]["program"]["name"] == "Shake"
    everything = json.dumps(fake.requests)
    assert "10.20.30.40" not in everything and "50710" not in everything and "COM7" not in everything


def test_state_is_only_rewritten_when_it_changes(fake):
    r = runner(step("shake", "RUNNING", tool="shaker", start=1000.0))
    p = publisher(fake, r)
    p.publish_once(force=True)
    p.publish_once()
    assert len(fake.requests) == 2  # no heartbeat due, state unchanged
    r.steps["shake"].status = SimpleNamespace(value="COMPLETED")
    p.publish_once()
    assert fake.requests[-1]["body"]["state"]["steps"][0]["status"] == "COMPLETED"


def test_start_fails_fast_when_the_tables_are_missing():
    bad = FakeRest(status=404)
    try:
        p = publisher(bad, runner(step("a")))
        with pytest.raises(BridgeError, match="HTTP 404"):
            p.start()
    finally:
        bad.close()


def test_background_errors_are_reported_once(fake):
    errors = []
    p = publisher(fake, runner(step("a")), on_error=errors.append)
    p.start()
    fake.status = 500
    p.runner.steps["a"].status = SimpleNamespace(value="RUNNING")
    import time
    time.sleep(2.5)
    p._stop.set()
    assert len(errors) == 1 and "HTTP 500" in errors[0]
