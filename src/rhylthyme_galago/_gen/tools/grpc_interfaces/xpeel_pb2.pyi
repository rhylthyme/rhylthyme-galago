from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("peel", "check_status", "reset", "restart", "get_remaining_tape")
    class Peel(_message.Message):
        __slots__ = ("threshold",)
        THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        threshold: int
        def __init__(self, threshold: _Optional[int] = ...) -> None: ...
    class CheckStatus(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Reset(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Restart(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetRemainingTape(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PEEL_FIELD_NUMBER: _ClassVar[int]
    CHECK_STATUS_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    RESTART_FIELD_NUMBER: _ClassVar[int]
    GET_REMAINING_TAPE_FIELD_NUMBER: _ClassVar[int]
    peel: Command.Peel
    check_status: Command.CheckStatus
    reset: Command.Reset
    restart: Command.Restart
    get_remaining_tape: Command.GetRemainingTape
    def __init__(self, peel: _Optional[_Union[Command.Peel, _Mapping]] = ..., check_status: _Optional[_Union[Command.CheckStatus, _Mapping]] = ..., reset: _Optional[_Union[Command.Reset, _Mapping]] = ..., restart: _Optional[_Union[Command.Restart, _Mapping]] = ..., get_remaining_tape: _Optional[_Union[Command.GetRemainingTape, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("com_port",)
    COM_PORT_FIELD_NUMBER: _ClassVar[int]
    com_port: str
    def __init__(self, com_port: _Optional[str] = ...) -> None: ...
