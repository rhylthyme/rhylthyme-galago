"""Run instrument commands for a live program, off the runner's thread.

The executor knows nothing about the runner: ``submit`` sends one step's
command on a worker thread and calls ``on_reply(key, reply)`` from that
thread when the tool answers. The caller hands the reply back to its own
thread (the Rhylthyme runner puts it on its command queue).
"""

import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple

from .client import GrpcToolClient, ToolClient, ToolReply, ToolStatus
from .commands import CommandError, build_command, build_config
from .workcell import ToolBinding, Workcell, WorkcellError

ClientFactory = Callable[[ToolBinding], ToolClient]
OnReply = Callable[[str, ToolReply], None]

#: Response code for a step whose command could not be sent at all.
NOT_SENT = "NOT_SENT"

#: Response code for a command with no reply within its timeoutSeconds.
TIMEOUT = "TIMEOUT"

#: Extra seconds the gRPC deadline allows past timeoutSeconds, so the worker
#: thread is eventually freed after the executor has already reported TIMEOUT.
DEADLINE_GRACE = 5.0

#: Tool statuses a run can start against, by mode.
READY_STATUSES = {True: {"SIMULATED"}, False: {"READY"}}


@dataclass(frozen=True)
class ToolCheck:
    """Result of configuring and polling one tool before a run."""

    tool: str
    address: str
    configure: ToolReply
    status: ToolStatus
    ready: bool


class InstrumentExecutor:
    def __init__(
        self,
        workcell: Workcell,
        client_factory: ClientFactory = GrpcToolClient.for_binding,
        *,
        simulated: bool = True,
        max_workers: int = 16,
    ):
        self.workcell = workcell
        self.simulated = simulated
        self._client_factory = client_factory
        self._clients: Dict[str, ToolClient] = {}
        self._pool = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="rhylthyme-galago"
        )
        # key -> (token, future, timer); the token makes the first outcome
        # (reply or timeout) win and drops anything later for that submission
        self._in_flight: Dict[str, Tuple[object, Future, Optional[threading.Timer]]] = {}
        self._lock = threading.Lock()

    def client(self, tool: str) -> ToolClient:
        with self._lock:
            if tool not in self._clients:
                self._clients[tool] = self._client_factory(self.workcell.tool(tool))
            return self._clients[tool]

    def prepare(self, tools: Iterable[str]) -> List[ToolCheck]:
        """Configure each tool (simulated unless live) and poll its status."""
        checks = []
        for name in sorted(set(tools)):
            binding = self.workcell.tool(name)
            client = self.client(name)
            config = build_config(
                binding.type, binding.config, simulated=self.simulated, tool_id=name
            )
            configured = client.configure(config)
            status = client.status()
            ready = configured.ok and status.status in READY_STATUSES[self.simulated]
            checks.append(ToolCheck(name, binding.address, configured, status, ready))
        return checks

    def submit(self, key: str, instrument: Mapping[str, Any], on_reply: OnReply) -> None:
        """Send ``instrument`` ({tool, command, params, timeoutSeconds})."""
        try:
            binding = self.workcell.tool(instrument["tool"])
            command = build_command(
                binding.type, instrument["command"], instrument.get("params")
            )
            client = self.client(binding.name)
        except (CommandError, WorkcellError, KeyError) as e:
            on_reply(key, ToolReply(NOT_SENT, str(e)))
            return
        timeout = instrument.get("timeoutSeconds")
        token = object()

        def deliver(reply: ToolReply) -> None:
            with self._lock:
                entry = self._in_flight.get(key)
                if entry is None or entry[0] is not token:
                    return  # timed out, retried or shut down meanwhile
                del self._in_flight[key]
            if entry[2] is not None:
                entry[2].cancel()
            on_reply(key, reply)

        def run() -> None:
            deadline = timeout + DEADLINE_GRACE if timeout else None
            try:
                reply = client.execute(command, timeout=deadline)
            except Exception as e:  # a broken client must still end the step
                reply = ToolReply(NOT_SENT, f"{type(e).__name__}: {e}")
            deliver(reply)

        timer = None
        if timeout:
            timer = threading.Timer(
                timeout,
                deliver,
                [ToolReply(TIMEOUT, f"no reply after {timeout:g} s")],
            )
            timer.daemon = True
        with self._lock:
            self._in_flight[key] = (token, self._pool.submit(run), timer)
        if timer is not None:
            timer.start()

    def in_flight(self) -> List[str]:
        with self._lock:
            return sorted(self._in_flight)

    def shutdown(self) -> List[str]:
        """Stop accepting work; return the keys whose commands never replied."""
        with self._lock:
            pending = sorted(self._in_flight)
            for _, _, timer in self._in_flight.values():
                if timer is not None:
                    timer.cancel()
            self._in_flight.clear()
            clients = list(self._clients.values())
            self._clients.clear()
        self._pool.shutdown(wait=False, cancel_futures=True)
        for client in clients:
            client.close()
        return pending


def instrument_tools(program: Mapping[str, Any]) -> List[str]:
    """Names of the workcell tools a program's steps use."""
    names = set()
    for track in program.get("tracks", []):
        for step in track.get("steps", []):
            instrument = step.get("instrument")
            if instrument and instrument.get("tool"):
                names.add(instrument["tool"])
    return sorted(names)


__all__ = [
    "InstrumentExecutor",
    "NOT_SENT",
    "TIMEOUT",
    "ToolCheck",
    "instrument_tools",
]
