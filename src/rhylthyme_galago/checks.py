"""Check a program's instrument steps before a run.

``check_program(program)`` works offline from each step's ``toolType``;
``check_program(program, workcell)`` resolves tool types through the lab's
workcell and also reports tools the workcell does not have. Every message
names the step, the tool, the command and the offending field.
"""

from dataclasses import dataclass
from typing import Any, Iterator, List, Mapping, Optional, Tuple

from .commands import TOOL_TYPES, validate_command
from .workcell import Workcell

UNKNOWN_TOOL = "instrument_unknown_tool"
UNKNOWN_TOOL_TYPE = "instrument_unknown_tool_type"
TOOL_TYPE_MISMATCH = "instrument_tool_type_mismatch"
INVALID_COMMAND = "instrument_invalid_command"
UNCHECKED = "instrument_unchecked"


@dataclass(frozen=True)
class Issue:
    code: str
    step_id: str
    message: str
    severity: str = "error"  # "error" | "warning"


def _instrument_steps(program: Mapping[str, Any]) -> Iterator[Tuple[str, Mapping]]:
    for group in ("tracks", "trackTemplates"):
        for track in program.get(group) or []:
            for step in track.get("steps") or []:
                instrument = step.get("instrument")
                if isinstance(instrument, Mapping):
                    yield str(step.get("stepId", "?")), instrument


def check_program(
    program: Mapping[str, Any], workcell: Optional[Workcell] = None
) -> List[Issue]:
    issues: List[Issue] = []
    for step_id, instrument in _instrument_steps(program):
        tool = instrument.get("tool")
        command = instrument.get("command")
        declared = instrument.get("toolType")
        prefix = f"Step '{step_id}'"

        tool_type = declared
        if workcell is not None:
            binding = workcell.tools.get(tool)
            if binding is None:
                known = ", ".join(sorted(workcell.tools))
                issues.append(
                    Issue(
                        UNKNOWN_TOOL,
                        step_id,
                        f"{prefix}: workcell {workcell.id!r} has no tool "
                        f"{tool!r} (tools: {known})",
                    )
                )
                continue
            if declared and declared != binding.type:
                issues.append(
                    Issue(
                        TOOL_TYPE_MISMATCH,
                        step_id,
                        f"{prefix}: toolType {declared!r} but workcell tool "
                        f"{tool!r} is a {binding.type}",
                    )
                )
                continue
            tool_type = binding.type

        if not tool_type:
            issues.append(
                Issue(
                    UNCHECKED,
                    step_id,
                    f"{prefix}: {tool}.{command} not checked; add toolType "
                    "or validate with --workcell",
                    severity="warning",
                )
            )
            continue
        if tool_type not in TOOL_TYPES:
            issues.append(
                Issue(
                    UNKNOWN_TOOL_TYPE,
                    step_id,
                    f"{prefix}: unknown galago toolType {tool_type!r}",
                )
            )
            continue
        for problem in validate_command(tool_type, command, instrument.get("params")):
            issues.append(
                Issue(
                    INVALID_COMMAND,
                    step_id,
                    f"{prefix}: {tool} ({tool_type}) {command}: {problem}",
                )
            )
    return issues
