#!/usr/bin/env python
"""Export galago's command catalog (and message parity cases) as JSON.

    python scripts/export_catalog.py OUT_DIR

Writes ``OUT_DIR/galago-commands.json``: every tool type's commands and their
params, read from the vendored protos, for validators that cannot load
protobuf descriptors (the Rhylthyme MCP server's JavaScript). Also writes
``OUT_DIR/galago-command-cases.json``: inputs with the problems
``validate_command`` reports for them, so the JavaScript port can be checked
word for word against this package.
"""

import json
import sys
from pathlib import Path

from google.protobuf.descriptor import FieldDescriptor

from rhylthyme_galago import GALAGO_TOOLS_COMMIT, GALAGO_TOOLS_VERSION, TOOL_TYPES
from rhylthyme_galago.commands import (
    _ANY_JSON,
    _FLOATS,
    _INT_RANGES,
    _command_descriptor,
    commands_for,
    validate_command,
)


def _field(field: FieldDescriptor) -> dict:
    out: dict = {}
    if field.type in _INT_RANGES:
        low, high = _INT_RANGES[field.type]
        out = {"type": "int", "min": low, "max": high}
    elif field.type in _FLOATS:
        out = {"type": "number"}
    elif field.type == FieldDescriptor.TYPE_BOOL:
        out = {"type": "bool"}
    elif field.type == FieldDescriptor.TYPE_STRING:
        out = {"type": "string"}
    elif field.type == FieldDescriptor.TYPE_ENUM:
        out = {
            "type": "enum",
            "values": {v.name: v.number for v in field.enum_type.values},
        }
    elif field.type == FieldDescriptor.TYPE_MESSAGE:
        if field.message_type.full_name in _ANY_JSON:
            out = {"type": "any"}
        else:
            out = {"type": "message", "fields": _fields(field.message_type)}
    else:
        out = {"type": "bytes"}
    if field.json_name != field.name:
        out["jsonName"] = field.json_name
    if field.is_repeated:
        out["repeated"] = True
    return out


def _fields(descriptor) -> dict:
    # Insertion order is proto order, which the "(takes ...)" hint relies on.
    return {f.name: _field(f) for f in descriptor.fields}


def catalog() -> dict:
    return {
        "galagoToolsVersion": GALAGO_TOOLS_VERSION,
        "galagoToolsCommit": GALAGO_TOOLS_COMMIT,
        "tools": {
            tool_type: {
                command: _fields(_command_descriptor(tool_type, command))
                for command in commands_for(tool_type)
            }
            for tool_type in TOOL_TYPES
        },
    }


CASES = [
    ("bioshake", "start_shake", {"speed": 1000, "acceleration": 5, "duration": 300}),
    ("bioshake", "start_shake", {"speed": 1000.0}),
    ("bioshake", "spin", {}),
    ("bioshake", "start_shake", {"rpm": 5}),
    ("bioshake", "start_shake", {"speed": "fast"}),
    ("bioshake", "start_shake", {"speed": 10.5}),
    ("bioshake", "start_shake", {"speed": True}),
    ("bioshake", "start_shake", {"speed": 2**40}),
    ("bioshake", "start_shake", {"speed": None}),
    ("bioshake", "start_shake", {"rpm": 1, "speed": "x"}),
    ("bioshake", "home", None),
    ("liconic", "fetch_plate", {"cassette": 1, "level": 4}),
    ("liconic", "raw_command", {"cmd": 7}),
    ("pf400", "move", {"location": "hotel-1", "approachHeight": 10}),
    ("pf400", "move", {"approach_height": [1]}),
    ("opentrons2", "run_program", {"script_content": "p.py", "variables": {"n": [1, {"a": None}]}}),
    ("opentrons2", "run_program", {"variables": {"a": 1}, "extra": 1}),
    ("cytation", "start_read", {"well_addresses": ["A1", "B2"]}),
    ("cytation", "start_read", {"well_addresses": "A1"}),
    ("cytation", "start_read", {"well_addresses": ["A1", 2]}),
    ("blender", "whirr", {}),
]


def cases() -> list:
    return [
        {
            "toolType": tool_type,
            "command": command,
            "params": params,
            "problems": validate_command(tool_type, command, params),
        }
        for tool_type, command, params in CASES
    ]


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "galago-commands.json").write_text(
        json.dumps(catalog(), indent=1, sort_keys=False) + "\n"
    )
    (out / "galago-command-cases.json").write_text(json.dumps(cases(), indent=1) + "\n")
    print(f"Wrote galago-commands.json and galago-command-cases.json to {out}")


if __name__ == "__main__":
    main()
