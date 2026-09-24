import threading
import time

import pytest

from rhylthyme_galago import (
    NOT_SENT,
    TIMEOUT,
    FakeToolClient,
    InstrumentExecutor,
    ToolReply,
    instrument_tools,
    load_workcell,
)

WORKCELL = load_workcell(
    {
        "id": "bench",
        "tools": [
            {"name": "shaker", "type": "bioshake", "host": "h", "port": 1,
             "config": {"com_port": "COM3"}},
            {"name": "incubator", "type": "liconic", "host": "h", "port": 2},
        ],
    }
)
SHAKE = {"tool": "shaker", "command": "start_shake", "params": {"speed": 1000, "duration": 5}}


def make(clients, **kwargs):
    return InstrumentExecutor(WORKCELL, lambda binding: clients[binding.name], **kwargs)


def collect():
    replies = {}
    done = threading.Event()

    def on_reply(key, reply):
        replies[key] = reply
        done.set()

    return replies, done, on_reply


def test_prepare_configures_simulated_and_reports_ready():
    shaker = FakeToolClient()
    checks = make({"shaker": shaker}).prepare(["shaker"])
    assert [c.ready for c in checks] == [True]
    assert shaker.configured[0].simulated is True
    assert shaker.configured[0].bioshake.com_port == "COM3"


def test_live_mode_needs_ready_not_simulated():
    shaker = FakeToolClient(status="NOT_CONFIGURED")
    [check] = make({"shaker": shaker}, simulated=False).prepare(["shaker"])
    assert shaker.configured[0].simulated is False
    assert not check.ready


def test_submit_replies_from_the_tool():
    shaker = FakeToolClient(gate=threading.Event())
    executor = make({"shaker": shaker})
    replies, done, on_reply = collect()
    executor.submit("shake", dict(SHAKE, timeoutSeconds=30), on_reply)
    assert executor.in_flight() == ["shake"]
    assert not done.wait(0.1)  # still waiting on the instrument
    shaker.gate.set()
    assert done.wait(2)
    assert replies["shake"].ok
    # The gRPC deadline allows a grace period past timeoutSeconds
    assert shaker.executed == [{"command": "start_shake", "timeout": 35.0}]
    assert executor.in_flight() == []


def test_error_reply_is_passed_through():
    shaker = FakeToolClient({"start_shake": ToolReply("DRIVER_ERROR", "lid open")})
    replies, done, on_reply = collect()
    make({"shaker": shaker}).submit("shake", SHAKE, on_reply)
    assert done.wait(2)
    assert (replies["shake"].code, replies["shake"].error_message) == ("DRIVER_ERROR", "lid open")


@pytest.mark.parametrize(
    "instrument, message",
    [
        (dict(SHAKE, tool="reader"), "no tool named 'reader'"),
        (dict(SHAKE, command="spin"), "no command 'spin'"),
        (dict(SHAKE, params={"rpm": 5}), "bioshake.start_shake"),
    ],
)
def test_unsendable_commands_reply_not_sent(instrument, message):
    replies, done, on_reply = collect()
    make({"shaker": FakeToolClient()}).submit("shake", instrument, on_reply)
    assert done.is_set()
    assert replies["shake"].code == NOT_SENT
    assert message in replies["shake"].error_message


def test_client_exception_still_replies():
    def boom(command):
        raise ConnectionError("socket closed")

    replies, done, on_reply = collect()
    make({"shaker": FakeToolClient({"start_shake": boom})}).submit("shake", SHAKE, on_reply)
    assert done.wait(2)
    assert replies["shake"].code == NOT_SENT
    assert "socket closed" in replies["shake"].error_message


def test_shutdown_reports_in_flight_and_closes_clients():
    shaker = FakeToolClient(gate=threading.Event())
    executor = make({"shaker": shaker})
    executor.submit("shake", SHAKE, lambda key, reply: None)
    assert executor.shutdown() == ["shake"]
    assert shaker.closed
    shaker.gate.set()


def test_instrument_tools():
    program = {
        "tracks": [
            {"steps": [{"instrument": SHAKE}, {"name": "by hand"}]},
            {"steps": [{"instrument": {"tool": "incubator", "command": "fetch_plate"}}]},
        ]
    }
    assert instrument_tools(program) == ["incubator", "shaker"]


def test_timeout_reports_once_and_drops_the_late_reply():
    shaker = FakeToolClient(gate=threading.Event())
    executor = make({"shaker": shaker})
    calls = []
    done = threading.Event()

    def on_reply(key, reply):
        calls.append(reply)
        done.set()

    executor.submit("shake", dict(SHAKE, timeoutSeconds=0.2), on_reply)
    assert done.wait(2)
    assert calls[0].code == TIMEOUT and "no reply after 0.2 s" in calls[0].error_message
    assert executor.in_flight() == []
    shaker.gate.set()  # the instrument answers after all
    time.sleep(0.2)
    assert len(calls) == 1


def test_retry_after_timeout_gets_its_own_reply():
    gate = threading.Event()
    shaker = FakeToolClient(gate=gate)
    executor = make({"shaker": shaker})
    calls = []
    executor.submit("shake", dict(SHAKE, timeoutSeconds=0.1), lambda k, r: calls.append(r))
    time.sleep(0.3)
    assert [r.code for r in calls] == [TIMEOUT]
    shaker.gate = None  # the retried command is answered straight away
    executor.submit("shake", SHAKE, lambda k, r: calls.append(r))
    gate.set()
    time.sleep(0.2)
    assert [r.code for r in calls] == [TIMEOUT, "SUCCESS"]


def test_reply_before_timeout_cancels_the_timer():
    executor = make({"shaker": FakeToolClient()})
    calls = []
    executor.submit("shake", dict(SHAKE, timeoutSeconds=0.2), lambda k, r: calls.append(r))
    time.sleep(0.4)
    assert [r.code for r in calls] == ["SUCCESS"]


def test_shutdown_cancels_pending_timeouts():
    shaker = FakeToolClient(gate=threading.Event())
    executor = make({"shaker": shaker})
    calls = []
    executor.submit("shake", dict(SHAKE, timeoutSeconds=0.1), lambda k, r: calls.append(r))
    assert executor.shutdown() == ["shake"]
    time.sleep(0.3)
    shaker.gate.set()
    time.sleep(0.1)
    assert calls == []
