"""Workcell files: which galago tools a lab has and where they listen.

A workcell is a local JSON file, never part of a shared program::

    {"id": "bench-1", "name": "Bench 1",
     "tools": [{"name": "shaker", "type": "bioshake",
                "host": "10.0.0.12", "port": 50010,
                "config": {"com_port": "COM3"}}]}

Programs refer to tools only by ``name``.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Union

from .commands import TOOL_TYPES


class WorkcellError(ValueError):
    """A workcell file that cannot be used."""


@dataclass(frozen=True)
class ToolBinding:
    name: str
    type: str
    host: str
    port: int
    config: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass(frozen=True)
class Workcell:
    id: str
    name: str
    tools: Mapping[str, ToolBinding]

    def tool(self, name: str) -> ToolBinding:
        try:
            return self.tools[name]
        except KeyError:
            known = ", ".join(sorted(self.tools)) or "none"
            raise WorkcellError(
                f"Workcell {self.id!r} has no tool named {name!r} (tools: {known})"
            ) from None


def _binding(index: int, raw: Any) -> ToolBinding:
    where = f"tools[{index}]"
    if not isinstance(raw, dict):
        raise WorkcellError(f"{where} must be an object")
    missing = [k for k in ("name", "type", "host", "port") if raw.get(k) in (None, "")]
    if missing:
        raise WorkcellError(f"{where} is missing {', '.join(missing)}")
    if raw["type"] not in TOOL_TYPES:
        raise WorkcellError(
            f"{where} ({raw['name']!r}) has unknown galago type {raw['type']!r}"
        )
    port = raw["port"]
    if isinstance(port, bool) or not isinstance(port, int) or not 0 < port < 65536:
        raise WorkcellError(f"{where} ({raw['name']!r}) port must be 1-65535")
    config = raw.get("config") or {}
    if not isinstance(config, dict):
        raise WorkcellError(f"{where} ({raw['name']!r}) config must be an object")
    return ToolBinding(
        name=str(raw["name"]),
        type=raw["type"],
        host=str(raw["host"]),
        port=port,
        config=config,
        description=str(raw.get("description", "")),
    )


def parse_workcell(data: Mapping[str, Any]) -> Workcell:
    if not isinstance(data, dict):
        raise WorkcellError("A workcell must be a JSON object")
    raw_tools = data.get("tools")
    if not isinstance(raw_tools, list) or not raw_tools:
        raise WorkcellError("A workcell needs a non-empty 'tools' list")
    tools: Dict[str, ToolBinding] = {}
    for i, raw in enumerate(raw_tools):
        binding = _binding(i, raw)
        if binding.name in tools:
            raise WorkcellError(f"Duplicate tool name {binding.name!r}")
        tools[binding.name] = binding
    workcell_id = str(data.get("id") or data.get("name") or "workcell")
    return Workcell(id=workcell_id, name=str(data.get("name", workcell_id)), tools=tools)


def load_workcell(source: Union[str, Path, Mapping[str, Any]]) -> Workcell:
    """Load a workcell from a path or an already-parsed dict."""
    if isinstance(source, Mapping):
        return parse_workcell(source)
    path = Path(source)
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise WorkcellError(f"No such workcell file: {path}") from None
    except json.JSONDecodeError as e:
        raise WorkcellError(f"{path} is not valid JSON: {e}") from None
    return parse_workcell(data)
