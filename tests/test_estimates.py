from rhylthyme_galago import DEFAULT_SECONDS, FakeToolClient, ToolReply, fill_durations, load_workcell
from rhylthyme_galago.estimates import describe

WORKCELL = load_workcell(
    {"id": "bench", "tools": [
        {"name": "shaker", "type": "bioshake", "host": "h", "port": 1},
        {"name": "incubator", "type": "liconic", "host": "h", "port": 2},
    ]}
)


def program(*steps):
    return {"tracks": [{"trackId": "t", "steps": list(steps)}]}


def step(step_id, **instrument):
    return {"stepId": step_id, "instrument": instrument}


SHAKE = dict(tool="shaker", command="start_shake", params={"speed": 1000, "duration": 300})


def by_id(filled):
    return {s["stepId"]: s for s in filled["tracks"][0]["steps"]}


def test_tool_estimate_wins():
    tool = FakeToolClient(estimates={"start_shake": 310})
    filled, estimates = fill_durations(program(step("shake", **SHAKE)), WORKCELL, lambda b: tool)
    shake = by_id(filled)["shake"]
    assert shake["duration"] == {"type": "fixed", "seconds": 310.0}
    assert shake["metadata"]["durationEstimate"] == {"source": "tool", "seconds": 310.0}
    assert estimates[0].detail == "shaker EstimateDuration"
    assert tool.closed


def test_params_fallback_without_workcell():
    filled, [estimate] = fill_durations(program(step("shake", **SHAKE)))
    assert by_id(filled)["shake"]["duration"]["seconds"] == 300.0
    assert (estimate.source, estimate.detail) == ("params", "params.duration")


def test_params_fallback_when_the_tool_cannot_estimate():
    tool = FakeToolClient()  # answers UNRECOGNIZED_COMMAND
    _, [estimate] = fill_durations(program(step("shake", **SHAKE)), WORKCELL, lambda b: tool)
    assert estimate.source == "params"


def test_unreachable_tool_falls_back():
    class Down(FakeToolClient):
        def estimate(self, command):
            raise ConnectionError("refused")

    _, [estimate] = fill_durations(program(step("shake", **SHAKE)), WORKCELL, lambda b: Down())
    assert estimate.source == "params"


def test_timeout_param_and_default():
    wait = step("wait", tool="shaker", command="wait_for_shake_to_finish", params={"timeout": 90})
    fetch = step("fetch", tool="incubator", command="fetch_plate", params={"cassette": 1})
    filled, estimates = fill_durations(program(wait, fetch))
    assert [(e.step_id, e.seconds, e.source) for e in estimates] == [
        ("wait", 90.0, "params"),
        ("fetch", float(DEFAULT_SECONDS), "default"),
    ]
    assert describe(estimates) == [
        "  wait: 90 s (from params.timeout)",
        "  fetch: 60 s (default, no estimate available)",
    ]


def test_authored_durations_and_hand_steps_are_untouched():
    authored = dict(step("shake", **SHAKE), duration={"type": "fixed", "seconds": 5})
    hand = {"stepId": "look", "name": "Look at it"}
    original = program(authored, hand)
    filled, estimates = fill_durations(original)
    assert estimates == []
    assert filled == original
    assert "metadata" not in by_id(filled)["shake"]


def test_same_command_is_asked_once_and_input_not_mutated():
    tool = FakeToolClient(estimates={"start_shake": 42})
    calls = []
    real = tool.estimate
    tool.estimate = lambda command: calls.append(1) or real(command)
    original = program(step("a", **SHAKE), step("b", **SHAKE))
    filled, estimates = fill_durations(original, WORKCELL, lambda b: tool)
    assert [e.seconds for e in estimates] == [42.0, 42.0]
    assert len(calls) == 1
    assert "duration" not in original["tracks"][0]["steps"][0]


def test_zero_or_failed_estimate_is_not_used():
    class Zero(FakeToolClient):
        def estimate(self, command):
            return 0, ToolReply("SUCCESS")

    _, [estimate] = fill_durations(program(step("shake", **SHAKE)), WORKCELL, lambda b: Zero())
    assert estimate.source == "params"
