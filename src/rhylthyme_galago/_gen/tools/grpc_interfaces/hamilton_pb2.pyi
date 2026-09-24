from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("run_protocol", "load_protocol")
    class RunProtocol(_message.Message):
        __slots__ = ("protocol",)
        PROTOCOL_FIELD_NUMBER: _ClassVar[int]
        protocol: str
        def __init__(self, protocol: _Optional[str] = ...) -> None: ...
    class LoadProtocol(_message.Message):
        __slots__ = ("protocol",)
        PROTOCOL_FIELD_NUMBER: _ClassVar[int]
        protocol: str
        def __init__(self, protocol: _Optional[str] = ...) -> None: ...
    RUN_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    LOAD_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    run_protocol: Command.RunProtocol
    load_protocol: Command.LoadProtocol
    def __init__(self, run_protocol: _Optional[_Union[Command.RunProtocol, _Mapping]] = ..., load_protocol: _Optional[_Union[Command.LoadProtocol, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
