from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("load", "unload", "home", "abort", "retract", "go_to", "raw_command")
    class Load(_message.Message):
        __slots__ = ("stack_id", "plate_height", "stack_height", "plate_thickness")
        STACK_ID_FIELD_NUMBER: _ClassVar[int]
        PLATE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
        STACK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
        PLATE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
        stack_id: int
        plate_height: float
        stack_height: float
        plate_thickness: float
        def __init__(self, stack_id: _Optional[int] = ..., plate_height: _Optional[float] = ..., stack_height: _Optional[float] = ..., plate_thickness: _Optional[float] = ...) -> None: ...
    class Unload(_message.Message):
        __slots__ = ("stack_id", "plate_height", "stack_height", "plate_thickness")
        STACK_ID_FIELD_NUMBER: _ClassVar[int]
        PLATE_HEIGHT_FIELD_NUMBER: _ClassVar[int]
        STACK_HEIGHT_FIELD_NUMBER: _ClassVar[int]
        PLATE_THICKNESS_FIELD_NUMBER: _ClassVar[int]
        stack_id: int
        plate_height: float
        stack_height: float
        plate_thickness: float
        def __init__(self, stack_id: _Optional[int] = ..., plate_height: _Optional[float] = ..., stack_height: _Optional[float] = ..., plate_thickness: _Optional[float] = ...) -> None: ...
    class Home(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Abort(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Retract(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GoTo(_message.Message):
        __slots__ = ("stack_id",)
        STACK_ID_FIELD_NUMBER: _ClassVar[int]
        stack_id: int
        def __init__(self, stack_id: _Optional[int] = ...) -> None: ...
    class SendRawCommand(_message.Message):
        __slots__ = ("command",)
        COMMAND_FIELD_NUMBER: _ClassVar[int]
        command: str
        def __init__(self, command: _Optional[str] = ...) -> None: ...
    LOAD_FIELD_NUMBER: _ClassVar[int]
    UNLOAD_FIELD_NUMBER: _ClassVar[int]
    HOME_FIELD_NUMBER: _ClassVar[int]
    ABORT_FIELD_NUMBER: _ClassVar[int]
    RETRACT_FIELD_NUMBER: _ClassVar[int]
    GO_TO_FIELD_NUMBER: _ClassVar[int]
    RAW_COMMAND_FIELD_NUMBER: _ClassVar[int]
    load: Command.Load
    unload: Command.Unload
    home: Command.Home
    abort: Command.Abort
    retract: Command.Retract
    go_to: Command.GoTo
    raw_command: Command.SendRawCommand
    def __init__(self, load: _Optional[_Union[Command.Load, _Mapping]] = ..., unload: _Optional[_Union[Command.Unload, _Mapping]] = ..., home: _Optional[_Union[Command.Home, _Mapping]] = ..., abort: _Optional[_Union[Command.Abort, _Mapping]] = ..., retract: _Optional[_Union[Command.Retract, _Mapping]] = ..., go_to: _Optional[_Union[Command.GoTo, _Mapping]] = ..., raw_command: _Optional[_Union[Command.SendRawCommand, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("ip", "port")
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...
