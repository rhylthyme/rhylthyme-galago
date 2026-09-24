import json

import pytest

from rhylthyme_galago import WorkcellError, load_workcell

SHAKER = {"name": "shaker", "type": "bioshake", "host": "10.0.0.12", "port": 50010}


def test_load_from_dict():
    workcell = load_workcell({"id": "bench", "tools": [dict(SHAKER, config={"com_port": "COM3"})]})
    shaker = workcell.tool("shaker")
    assert workcell.id == "bench"
    assert shaker.type == "bioshake"
    assert shaker.address == "10.0.0.12:50010"
    assert shaker.config == {"com_port": "COM3"}


def test_load_from_file(tmp_path):
    path = tmp_path / "lab.json"
    path.write_text(json.dumps({"name": "Lab", "tools": [SHAKER]}))
    assert load_workcell(path).id == "Lab"


def test_missing_file(tmp_path):
    with pytest.raises(WorkcellError, match="No such workcell file"):
        load_workcell(tmp_path / "nope.json")


def test_invalid_json(tmp_path):
    path = tmp_path / "lab.json"
    path.write_text("{")
    with pytest.raises(WorkcellError, match="not valid JSON"):
        load_workcell(path)


def test_unknown_tool_name_lists_tools():
    workcell = load_workcell({"tools": [SHAKER]})
    with pytest.raises(WorkcellError, match="no tool named 'reader' \\(tools: shaker\\)"):
        workcell.tool("reader")


@pytest.mark.parametrize(
    "tools, message",
    [
        ([], "non-empty 'tools'"),
        ([{"name": "shaker", "type": "bioshake"}], "missing host, port"),
        ([dict(SHAKER, type="blender")], "unknown galago type 'blender'"),
        ([dict(SHAKER, port=70000)], "port must be 1-65535"),
        ([dict(SHAKER, port="50010")], "port must be 1-65535"),
        ([SHAKER, SHAKER], "Duplicate tool name 'shaker'"),
        ([dict(SHAKER, config=[1])], "config must be an object"),
    ],
)
def test_malformed_workcells(tools, message):
    with pytest.raises(WorkcellError, match=message):
        load_workcell({"tools": tools})
