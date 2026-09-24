"""Build galago ``Command`` and ``Config`` messages from plain dicts.

A Rhylthyme step names an instrument command the way galago's protos do::

    {"tool": "shaker", "command": "start_shake",
     "params": {"speed": 1000, "duration": 300}}

``build_command("bioshake", "start_shake", {...})`` turns that into the
``ToolDriver`` request. Names are the proto field names (snake_case).
"""

from typing import Any, Dict, Mapping, Optional, Tuple

from google.protobuf import json_format

from ._gen.tools.grpc_interfaces import tool_base_pb2


class CommandError(ValueError):
    """A command or config that cannot be built for the given tool type."""


def _oneof_fields(message_type, oneof: str) -> Tuple[str, ...]:
    return tuple(f.name for f in message_type.DESCRIPTOR.oneofs_by_name[oneof].fields)


#: Every galago tool type this package can talk to, e.g. ``"bioshake"``.
TOOL_TYPES: Tuple[str, ...] = _oneof_fields(tool_base_pb2.Command, "tool_command")


def _check_tool_type(tool_type: str) -> None:
    if tool_type not in TOOL_TYPES:
        raise CommandError(
            f"Unknown galago tool type {tool_type!r}; "
            f"expected one of: {', '.join(sorted(TOOL_TYPES))}"
        )


def build_command(
    tool_type: str, command: str, params: Optional[Mapping[str, Any]] = None
) -> tool_base_pb2.Command:
    """Return the ``Command`` for ``command`` on a ``tool_type`` tool."""
    _check_tool_type(tool_type)
    tool_message = getattr(tool_base_pb2.Command(), tool_type)
    commands = _oneof_fields(type(tool_message), "command")
    if command not in commands:
        raise CommandError(
            f"{tool_type} has no command {command!r}; "
            f"expected one of: {', '.join(commands)}"
        )
    try:
        return json_format.ParseDict(
            {tool_type: {command: dict(params or {})}}, tool_base_pb2.Command()
        )
    except json_format.ParseError as e:
        raise CommandError(f"{tool_type}.{command}: {e}") from e


def build_config(
    tool_type: str,
    config: Optional[Mapping[str, Any]] = None,
    *,
    simulated: bool,
    tool_id: str = "",
) -> tool_base_pb2.Config:
    """Return the ``Config`` that ``Configure`` sends to a ``tool_type`` tool."""
    _check_tool_type(tool_type)
    try:
        return json_format.ParseDict(
            {"simulated": simulated, "toolId": tool_id, tool_type: dict(config or {})},
            tool_base_pb2.Config(),
        )
    except json_format.ParseError as e:
        raise CommandError(f"{tool_type} config: {e}") from e


def describe_command(command: tool_base_pb2.Command) -> Dict[str, str]:
    """Return ``{"toolType": ..., "command": ...}`` for a built command."""
    tool_type = command.WhichOneof("tool_command") or ""
    name = getattr(command, tool_type).WhichOneof("command") if tool_type else None
    return {"toolType": tool_type, "command": name or ""}
