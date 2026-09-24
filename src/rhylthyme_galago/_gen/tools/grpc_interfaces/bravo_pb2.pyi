from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("initialize", "run_protocol", "run_runset")
    class Initialize(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class RunProtocol(_message.Message):
        __slots__ = ("protocol_file",)
        PROTOCOL_FILE_FIELD_NUMBER: _ClassVar[int]
        protocol_file: str
        def __init__(self, protocol_file: _Optional[str] = ...) -> None: ...
    class RunRunset(_message.Message):
        __slots__ = ("runset_file",)
        RUNSET_FILE_FIELD_NUMBER: _ClassVar[int]
        runset_file: str
        def __init__(self, runset_file: _Optional[str] = ...) -> None: ...
    INITIALIZE_FIELD_NUMBER: _ClassVar[int]
    RUN_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    RUN_RUNSET_FIELD_NUMBER: _ClassVar[int]
    initialize: Command.Initialize
    run_protocol: Command.RunProtocol
    run_runset: Command.RunRunset
    def __init__(self, initialize: _Optional[_Union[Command.Initialize, _Mapping]] = ..., run_protocol: _Optional[_Union[Command.RunProtocol, _Mapping]] = ..., run_runset: _Optional[_Union[Command.RunRunset, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("device_file",)
    DEVICE_FILE_FIELD_NUMBER: _ClassVar[int]
    device_file: str
    def __init__(self, device_file: _Optional[str] = ...) -> None: ...
