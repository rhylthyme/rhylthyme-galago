"""Talking to one galago tool: over gRPC, or to a scripted fake in tests."""

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Protocol, Tuple

import grpc
from google.protobuf import empty_pb2, json_format

from ._gen.tools.grpc_interfaces import tool_base_pb2, tool_driver_pb2_grpc
from .commands import describe_command
from .workcell import ToolBinding

#: Response code for a transport failure (tool unreachable, deadline passed).
UNREACHABLE = "UNREACHABLE"


@dataclass(frozen=True)
class ToolReply:
    """Outcome of ``Configure`` or ``ExecuteCommand``."""

    code: str
    error_message: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.code == "SUCCESS"


@dataclass(frozen=True)
class ToolStatus:
    status: str
    uptime: int = 0
    error_message: str = ""


class ToolClient(Protocol):
    def configure(self, config: tool_base_pb2.Config) -> ToolReply: ...

    def status(self) -> ToolStatus: ...

    def execute(
        self, command: tool_base_pb2.Command, timeout: Optional[float] = None
    ) -> ToolReply: ...

    def estimate(self, command: tool_base_pb2.Command) -> Tuple[Optional[int], ToolReply]: ...

    def close(self) -> None: ...


def _code_name(code: int) -> str:
    return tool_base_pb2.ResponseCode.Name(code)


def _rpc_failure(e: grpc.RpcError) -> ToolReply:
    detail = e.details() if hasattr(e, "details") else str(e)
    status = e.code().name if hasattr(e, "code") else "UNKNOWN"
    return ToolReply(UNREACHABLE, f"{status}: {detail}")


class GrpcToolClient:
    """``ToolDriver`` client for one tool server."""

    def __init__(self, address: str, connect_timeout: float = 5.0):
        self.address = address
        self.connect_timeout = connect_timeout
        self._channel = grpc.insecure_channel(address)
        self._stub = tool_driver_pb2_grpc.ToolDriverStub(self._channel)

    @classmethod
    def for_binding(cls, binding: ToolBinding) -> "GrpcToolClient":
        return cls(binding.address)

    def configure(self, config: tool_base_pb2.Config) -> ToolReply:
        try:
            reply = self._stub.Configure(config, timeout=self.connect_timeout * 6)
        except grpc.RpcError as e:
            return _rpc_failure(e)
        return ToolReply(_code_name(reply.response), reply.error_message)

    def status(self) -> ToolStatus:
        try:
            reply = self._stub.GetStatus(empty_pb2.Empty(), timeout=self.connect_timeout)
        except grpc.RpcError as e:
            return ToolStatus("OFFLINE", error_message=_rpc_failure(e).error_message)
        return ToolStatus(
            tool_base_pb2.ToolStatus.Name(reply.status), reply.uptime, reply.error_message
        )

    def execute(
        self, command: tool_base_pb2.Command, timeout: Optional[float] = None
    ) -> ToolReply:
        try:
            reply = self._stub.ExecuteCommand(command, timeout=timeout)
        except grpc.RpcError as e:
            return _rpc_failure(e)
        return ToolReply(
            _code_name(reply.response),
            reply.error_message,
            json_format.MessageToDict(reply.meta_data),
        )

    def estimate(self, command: tool_base_pb2.Command) -> Tuple[Optional[int], ToolReply]:
        try:
            reply = self._stub.EstimateDuration(command, timeout=self.connect_timeout)
        except grpc.RpcError as e:
            return None, _rpc_failure(e)
        result = ToolReply(_code_name(reply.response), reply.error_message)
        return (reply.estimated_duration_seconds if result.ok else None), result

    def close(self) -> None:
        self._channel.close()


class FakeToolClient:
    """In-memory tool for tests.

    ``replies`` maps a command name (``"start_shake"``) to a ``ToolReply`` or
    to a callable returning one; unscripted commands succeed. Set ``gate`` to
    a ``threading.Event`` to hold every ``execute`` until the test releases it.
    """

    def __init__(
        self,
        replies: Optional[Mapping[str, Any]] = None,
        *,
        status: str = "READY",
        estimates: Optional[Mapping[str, int]] = None,
        gate: Optional[threading.Event] = None,
    ):
        self.replies: Dict[str, Any] = dict(replies or {})
        self.estimates = dict(estimates or {})
        self.gate = gate
        self._status = status
        self.configured: List[tool_base_pb2.Config] = []
        self.executed: List[Dict[str, Any]] = []
        self.closed = False

    def configure(self, config: tool_base_pb2.Config) -> ToolReply:
        self.configured.append(config)
        if config.simulated:
            self._status = "SIMULATED"
        return ToolReply("SUCCESS")

    def status(self) -> ToolStatus:
        return ToolStatus(self._status)

    def execute(
        self, command: tool_base_pb2.Command, timeout: Optional[float] = None
    ) -> ToolReply:
        name = describe_command(command)["command"]
        self.executed.append({"command": name, "timeout": timeout})
        if self.gate is not None:
            self.gate.wait()
        reply = self.replies.get(name, ToolReply("SUCCESS"))
        return reply(command) if callable(reply) else reply

    def estimate(self, command: tool_base_pb2.Command) -> Tuple[Optional[int], ToolReply]:
        name = describe_command(command)["command"]
        if name in self.estimates:
            return self.estimates[name], ToolReply("SUCCESS")
        return None, ToolReply("UNRECOGNIZED_COMMAND")

    def close(self) -> None:
        self.closed = True
