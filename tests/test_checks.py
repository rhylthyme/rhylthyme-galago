import pytest

from rhylthyme_galago import check_program, load_workcell, validate_command

WORKCELL = load_workcell(
    {
        "id": "bench",
        "tools": [
            {"name": "shaker", "type": "bioshake", "host": "h", "port": 1},
            {"name": "incubator", "type": "liconic", "host": "h", "port": 2},
            {"name": "ot2", "type": "opentrons2", "host": "h", "port": 3},
            {"name": "arm", "type": "pf400", "host": "h", "port": 4},
        ],
    }
)


@pytest.mark.parametrize(
    "tool_type, command, params",
    [
        ("bioshake", "start_shake", {"speed": 1000, "acceleration": 5, "duration": 300}),
        ("bioshake", "set_temperature", {"temperature": 37}),
        ("liconic", "fetch_plate", {"cassette": 1, "level": 4}),
        ("opentrons2", "run_program", {"script_content": "p.py", "variables": {"n": 3, "x": [1]}}),
        ("opentrons2", "pause", None),
        ("pf400", "move", {"location": "hotel-1", "approach_height": 10}),
        ("pf400", "transfer", {"source_nest": "a", "destination_nest": "b"}),
        ("bioshake", "start_shake", {"speed": 1000.0}),  # JSON floats that are whole
        ("pf400", "move", {"location": "hotel-1", "approachHeight": 10}),  # JSON name
    ],
)
def test_valid_commands(tool_type, command, params):
    assert validate_command(tool_type, command, params) == []


@pytest.mark.parametrize(
    "tool_type, command, params, expected",
    [
        ("bioshake", "spin", {}, "bioshake has no command 'spin' (expected one of: grip,"),
        ("bioshake", "start_shake", {"rpm": 5}, "unknown param 'rpm' (takes speed, acceleration, duration)"),
        ("bioshake", "start_shake", {"speed": "fast"}, "param 'speed' must be an integer, got 'fast'"),
        ("bioshake", "start_shake", {"speed": 10.5}, "param 'speed' must be an integer, got 10.5"),
        ("bioshake", "start_shake", {"speed": True}, "param 'speed' must be an integer, got True"),
        ("bioshake", "start_shake", {"speed": 2**40}, "must be an integer"),
        ("liconic", "raw_command", {"cmd": 7}, "param 'cmd' must be a string, got 7"),
        ("pf400", "move", {"approach_height": [1]}, "param 'approach_height' must be an integer"),
        ("opentrons2", "run_program", {"variables": {"a": 1}, "extra": 1}, "unknown param 'extra'"),
        ("blender", "whirr", {}, "unknown galago tool type 'blender'"),
    ],
)
def test_invalid_commands(tool_type, command, params, expected):
    problems = validate_command(tool_type, command, params)
    assert len(problems) == 1
    assert expected in problems[0]


def test_every_problem_is_reported():
    problems = validate_command("bioshake", "start_shake", {"rpm": 1, "speed": "x"})
    assert len(problems) == 2


def test_repeated_fields():
    assert validate_command("cytation", "start_read", {"well_addresses": ["A1", "B2"]}) == []
    [problem] = validate_command("cytation", "start_read", {"well_addresses": "A1"})
    assert "'well_addresses' must be a list of a string" in problem


def program(*instruments):
    return {
        "tracks": [
            {
                "trackId": "t",
                "steps": [
                    {"stepId": f"s{i}", "instrument": inst}
                    for i, inst in enumerate(instruments)
                ],
            }
        ]
    }


SHAKE = {"tool": "shaker", "command": "start_shake", "params": {"speed": 1000}}


def test_offline_check_uses_tool_type():
    [issue] = check_program(program(dict(SHAKE, toolType="bioshake", params={"rpm": 1})))
    assert issue.code == "instrument_invalid_command"
    assert issue.step_id == "s0"
    assert issue.message == (
        "Step 's0': shaker (bioshake) start_shake: unknown param 'rpm' "
        "(takes speed, acceleration, duration)"
    )


def test_offline_without_tool_type_warns_unchecked():
    [issue] = check_program(program(SHAKE))
    assert (issue.code, issue.severity) == ("instrument_unchecked", "warning")
    assert "add toolType or validate with --workcell" in issue.message


def test_offline_unknown_tool_type():
    [issue] = check_program(program(dict(SHAKE, toolType="blender")))
    assert issue.code == "instrument_unknown_tool_type"


def test_workcell_resolves_type_without_tool_type():
    assert check_program(program(SHAKE), WORKCELL) == []
    [issue] = check_program(program(dict(SHAKE, command="spin")), WORKCELL)
    assert issue.message.startswith("Step 's0': shaker (bioshake) spin: bioshake has no command")


def test_workcell_unknown_tool():
    [issue] = check_program(program(dict(SHAKE, tool="reader")), WORKCELL)
    assert issue.code == "instrument_unknown_tool"
    assert "workcell 'bench' has no tool 'reader' (tools: arm, incubator, ot2, shaker)" in issue.message


def test_workcell_tool_type_mismatch():
    [issue] = check_program(program(dict(SHAKE, toolType="liconic")), WORKCELL)
    assert issue.code == "instrument_tool_type_mismatch"
    assert issue.message == (
        "Step 's0': toolType 'liconic' but workcell tool 'shaker' is a bioshake"
    )


def test_steps_without_instruments_are_ignored():
    assert check_program({"tracks": [{"steps": [{"stepId": "a", "name": "by hand"}]}]}) == []
