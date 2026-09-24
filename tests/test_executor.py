import threading

import pytest

from rhylthyme_galago import (
    NOT_SENT,
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
    assert shaker.executed == [{"command": "start_shake", "timeout": 30}]
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
