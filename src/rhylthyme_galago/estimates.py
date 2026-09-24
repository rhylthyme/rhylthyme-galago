"""Fill in durations that instrument steps leave out, for planning.

An instrument step may omit ``duration``: at run time it ends when the tool
replies. Planners still need a number, so ``fill_durations`` supplies one, in
this order:

1. ``tool``: the tool's own ``EstimateDuration`` (needs a workcell and a
   reachable galago server whose tool is already configured, READY or
   SIMULATED; galago answers NOT_READY otherwise, and planning never
   configures a tool, since that could flip a live one to simulated),
2. ``params``: a duration-like command parameter (``duration``, ``timeout``...),
3. ``default``: ``DEFAULT_SECONDS``.

Each filled step becomes ``{"type": "fixed", "seconds": N}`` and is flagged in
``metadata.durationEstimate`` (``{"source", "seconds"}``) so timelines can show
it as an estimate. Steps with an authored duration are never touched.
"""

import copy
import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Mapping, Optional, Tuple

from .client import GrpcToolClient, ToolClient
from .commands import CommandError, build_command
from .workcell import ToolBinding, Workcell

DEFAULT_SECONDS = 60

#: Command params read as seconds, in order of preference.
DURATION_PARAMS = ("duration", "duration_seconds", "seconds", "run_time", "time", "timeout")


@dataclass(frozen=True)
class Estimate:
    step_id: str
    seconds: float
    source: str  # "tool" | "params" | "default"
    detail: str = ""


def _steps(program: Mapping[str, Any]) -> Iterator[Dict[str, Any]]:
    for track in program.get("tracks") or []:
        for step in track.get("steps") or []:
            yield step


def _from_params(params: Optional[Mapping[str, Any]]) -> Optional[Tuple[float, str]]:
    for key in DURATION_PARAMS:
        value = (params or {}).get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0:
            return float(value), key
    return None


def _json_number(seconds: float) -> Any:
    """5.0 -> 5, so filled programs read like hand-written ones."""
    return int(seconds) if float(seconds).is_integer() else seconds


def fill_durations(
    program: Mapping[str, Any],
    workcell: Optional[Workcell] = None,
    client_factory: Callable[[ToolBinding], ToolClient] = GrpcToolClient.for_binding,
) -> Tuple[Dict[str, Any], List[Estimate]]:
    """Return a copy of ``program`` with instrument durations filled, and how."""
    filled = copy.deepcopy(dict(program))
    estimates: List[Estimate] = []
    clients: Dict[str, ToolClient] = {}
    asked: Dict[str, Optional[Tuple[float, str]]] = {}
    try:
        for step in _steps(filled):
            instrument = step.get("instrument")
            if not isinstance(instrument, Mapping) or "duration" in step:
                continue
            estimate = None
            binding = workcell.tools.get(instrument.get("tool")) if workcell else None
            if binding is not None:
                key = json.dumps(
                    [binding.name, instrument.get("command"), instrument.get("params")],
                    sort_keys=True,
                    default=str,
                )
                if key not in asked:
                    asked[key] = _ask_tool(binding, instrument, clients, client_factory)
                if asked[key] is not None:
                    seconds, detail = asked[key]
                    estimate = Estimate(str(step.get("stepId")), seconds, "tool", detail)
            if estimate is None:
                found = _from_params(instrument.get("params"))
                if found is not None:
                    estimate = Estimate(
                        str(step.get("stepId")), found[0], "params", f"params.{found[1]}"
                    )
            if estimate is None:
                estimate = Estimate(
                    str(step.get("stepId")), float(DEFAULT_SECONDS), "default"
                )
            seconds = _json_number(estimate.seconds)
            step["duration"] = {"type": "fixed", "seconds": seconds}
            metadata = step.setdefault("metadata", {})
            metadata["durationEstimate"] = {"source": estimate.source, "seconds": seconds}
            estimates.append(estimate)
    finally:
        for client in clients.values():
            client.close()
    return filled, estimates


def _ask_tool(
    binding: ToolBinding,
    instrument: Mapping[str, Any],
    clients: Dict[str, ToolClient],
    client_factory: Callable[[ToolBinding], ToolClient],
) -> Optional[Tuple[float, str]]:
    try:
        command = build_command(
            binding.type, str(instrument.get("command")), instrument.get("params")
        )
    except CommandError:
        return None
    if binding.name not in clients:
        clients[binding.name] = client_factory(binding)
    try:
        seconds, reply = clients[binding.name].estimate(command)
    except Exception:  # an unreachable tool falls back to the params
        return None
    if reply.ok and seconds is not None and seconds > 0:
        return float(seconds), f"{binding.name} EstimateDuration"
    return None


def describe(estimates: List[Estimate]) -> List[str]:
    """One line per filled duration, for command-line reports."""
    how = {
        "tool": "from {detail}",
        "params": "from {detail}",
        "default": "default, no estimate available",
    }
    return [
        f"  {e.step_id}: {e.seconds:g} s ({how[e.source].format(detail=e.detail)})"
        for e in estimates
    ]
