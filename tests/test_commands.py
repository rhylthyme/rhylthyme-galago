import pytest

from rhylthyme_galago import TOOL_TYPES, CommandError, build_command, build_config
from rhylthyme_galago.commands import describe_command


def test_tool_types_cover_galago_tools():
    assert {"bioshake", "liconic", "opentrons2", "pf400"} <= set(TOOL_TYPES)


def test_build_command_sets_params_by_proto_field_name():
    command = build_command("bioshake", "start_shake", {"speed": 1000, "duration": 5})
    assert describe_command(command) == {"toolType": "bioshake", "command": "start_shake"}
    assert command.bioshake.start_shake.speed == 1000
    assert command.bioshake.start_shake.duration == 5


def test_build_command_without_params():
    assert describe_command(build_command("bioshake", "home"))["command"] == "home"


def test_unknown_tool_type():
    with pytest.raises(CommandError, match="Unknown galago tool type 'shaker'"):
        build_command("shaker", "start_shake")


def test_unknown_command_lists_valid_ones():
    with pytest.raises(CommandError, match="bioshake has no command 'spin'.*start_shake"):
        build_command("bioshake", "spin")


def test_unknown_param():
    with pytest.raises(CommandError, match="bioshake.start_shake"):
        build_command("bioshake", "start_shake", {"rpm": 1000})


def test_wrongly_typed_param():
    with pytest.raises(CommandError, match="bioshake.start_shake"):
        build_command("bioshake", "start_shake", {"speed": "fast"})


def test_build_config_carries_simulated_and_tool_config():
    config = build_config("bioshake", {"com_port": "COM3"}, simulated=True, tool_id="shaker")
    assert config.simulated is True
    assert config.toolId == "shaker"
    assert config.bioshake.com_port == "COM3"


def test_build_config_rejects_unknown_config_field():
    with pytest.raises(CommandError, match="bioshake config"):
        build_config("bioshake", {"baud": 9600}, simulated=False)


def test_exported_catalog_is_fresh():
    """catalog/ is what the MCP server vendors; regenerate it with
    `python scripts/export_catalog.py catalog` after changing the protos or
    validate_command's messages."""
    import importlib.util
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location("export_catalog", root / "scripts" / "export_catalog.py")
    export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export)
    assert json.loads((root / "catalog" / "galago-commands.json").read_text()) == export.catalog()
    assert json.loads((root / "catalog" / "galago-command-cases.json").read_text()) == export.cases()
