"""Build galago ``Command`` and ``Config`` messages from plain dicts.

A Rhylthyme step names an instrument command the way galago's protos do::

    {"tool": "shaker", "command": "start_shake",
     "params": {"speed": 1000, "duration": 300}}

``build_command("bioshake", "start_shake", {...})`` turns that into the
``ToolDriver`` request. Names are the proto field names (snake_case).
"""

from typing import Any, Dict, List, Mapping, Optional, Tuple

from google.protobuf import json_format
from google.protobuf.descriptor import Descriptor, FieldDescriptor

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


def commands_for(tool_type: str) -> Tuple[str, ...]:
    """The command names a ``tool_type`` tool accepts, in proto order."""
    _check_tool_type(tool_type)
    return _oneof_fields(type(getattr(tool_base_pb2.Command(), tool_type)), "command")


def _command_descriptor(tool_type: str, command: str) -> Descriptor:
    tool_message = getattr(tool_base_pb2.Command(), tool_type)
    return tool_message.DESCRIPTOR.fields_by_name[command].message_type


_ANY_JSON = {"google.protobuf.Struct", "google.protobuf.Value", "google.protobuf.ListValue"}
_INT_RANGES = {
    FieldDescriptor.TYPE_INT32: (-(2**31), 2**31 - 1),
    FieldDescriptor.TYPE_SINT32: (-(2**31), 2**31 - 1),
    FieldDescriptor.TYPE_SFIXED32: (-(2**31), 2**31 - 1),
    FieldDescriptor.TYPE_UINT32: (0, 2**32 - 1),
    FieldDescriptor.TYPE_FIXED32: (0, 2**32 - 1),
    FieldDescriptor.TYPE_INT64: (-(2**63), 2**63 - 1),
    FieldDescriptor.TYPE_SINT64: (-(2**63), 2**63 - 1),
    FieldDescriptor.TYPE_SFIXED64: (-(2**63), 2**63 - 1),
    FieldDescriptor.TYPE_UINT64: (0, 2**64 - 1),
    FieldDescriptor.TYPE_FIXED64: (0, 2**64 - 1),
}
_FLOATS = {FieldDescriptor.TYPE_FLOAT, FieldDescriptor.TYPE_DOUBLE}


def _type_name(field: FieldDescriptor) -> str:
    if field.type in _INT_RANGES:
        return "an integer"
    if field.type in _FLOATS:
        return "a number"
    if field.type == FieldDescriptor.TYPE_BOOL:
        return "true or false"
    if field.type == FieldDescriptor.TYPE_STRING:
        return "a string"
    if field.type == FieldDescriptor.TYPE_ENUM:
        return "one of " + ", ".join(v.name for v in field.enum_type.values)
    return "an object"


def _is_repeated(field: FieldDescriptor) -> bool:
    return field.is_repeated


def _scalar_ok(field: FieldDescriptor, value: Any) -> bool:
    if field.type in _INT_RANGES:
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        low, high = _INT_RANGES[field.type]
        return low <= value <= high
    if field.type in _FLOATS:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if field.type == FieldDescriptor.TYPE_BOOL:
        return isinstance(value, bool)
    if field.type == FieldDescriptor.TYPE_STRING:
        return isinstance(value, str)
    if field.type == FieldDescriptor.TYPE_ENUM:
        names = {v.name for v in field.enum_type.values}
        numbers = {v.number for v in field.enum_type.values}
        return value in names or (
            isinstance(value, int) and not isinstance(value, bool) and value in numbers
        )
    return True  # bytes: left to the protobuf parser


def _check_message(
    descriptor: Descriptor, values: Any, path: str, problems: List[str]
) -> None:
    if not isinstance(values, Mapping):
        problems.append(f"'{path}' must be an object, got {values!r}")
        return
    for key, value in values.items():
        field = descriptor.fields_by_name.get(key) or next(
            (f for f in descriptor.fields if f.json_name == key), None
        )
        where = f"{path}.{key}" if path else key
        if field is None:
            known = ", ".join(f.name for f in descriptor.fields) or "no params"
            problems.append(f"unknown param '{where}' (takes {known})")
            continue
        items = value if _is_repeated(field) else [value]
        if _is_repeated(field) and not isinstance(value, list):
            problems.append(f"param '{where}' must be a list, got {value!r}")
            continue
        for item in items:
            if field.type == FieldDescriptor.TYPE_MESSAGE:
                if field.message_type.full_name in _ANY_JSON:
                    continue
                _check_message(field.message_type, item, where, problems)
            elif not _scalar_ok(field, item):
                problems.append(
                    f"param '{where}' must be {_type_name(field)}, got {item!r}"
                )


def validate_command(
    tool_type: str, command: str, params: Optional[Mapping[str, Any]] = None
) -> List[str]:
    """
    Problems with ``command`` and ``params`` for a ``tool_type`` tool, each a
    sentence naming the offending command or field; empty when it would build.
    """
    if tool_type not in TOOL_TYPES:
        return [
            f"unknown galago tool type {tool_type!r} "
            f"(expected one of: {', '.join(sorted(TOOL_TYPES))})"
        ]
    commands = commands_for(tool_type)
    if command not in commands:
        return [
            f"{tool_type} has no command {command!r} "
            f"(expected one of: {', '.join(commands)})"
        ]
    problems: List[str] = []
    _check_message(_command_descriptor(tool_type, command), params or {}, "", problems)
    return problems


def build_command(
    tool_type: str, command: str, params: Optional[Mapping[str, Any]] = None
) -> tool_base_pb2.Command:
    """Return the ``Command`` for ``command`` on a ``tool_type`` tool."""
    _check_tool_type(tool_type)
    problems = validate_command(tool_type, command, params)
    if problems:
        raise CommandError(f"{tool_type}.{command}: " + "; ".join(problems))
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
