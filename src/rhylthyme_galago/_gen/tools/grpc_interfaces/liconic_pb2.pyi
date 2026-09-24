from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("fetch_plate", "store_plate", "reset", "raw_command")
    class FetchPlate(_message.Message):
        __slots__ = ("cassette", "level", "wait_time")
        CASSETTE_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        WAIT_TIME_FIELD_NUMBER: _ClassVar[int]
        cassette: int
        level: int
        wait_time: int
        def __init__(self, cassette: _Optional[int] = ..., level: _Optional[int] = ..., wait_time: _Optional[int] = ...) -> None: ...
    class StorePlate(_message.Message):
        __slots__ = ("cassette", "level", "wait_time")
        CASSETTE_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        WAIT_TIME_FIELD_NUMBER: _ClassVar[int]
        cassette: int
        level: int
        wait_time: int
        def __init__(self, cassette: _Optional[int] = ..., level: _Optional[int] = ..., wait_time: _Optional[int] = ...) -> None: ...
    class SendRawCommand(_message.Message):
        __slots__ = ("cmd",)
        CMD_FIELD_NUMBER: _ClassVar[int]
        cmd: str
        def __init__(self, cmd: _Optional[str] = ...) -> None: ...
    class Reset(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    FETCH_PLATE_FIELD_NUMBER: _ClassVar[int]
    STORE_PLATE_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    RAW_COMMAND_FIELD_NUMBER: _ClassVar[int]
    fetch_plate: Command.FetchPlate
    store_plate: Command.StorePlate
    reset: Command.Reset
    raw_command: Command.SendRawCommand
    def __init__(self, fetch_plate: _Optional[_Union[Command.FetchPlate, _Mapping]] = ..., store_plate: _Optional[_Union[Command.StorePlate, _Mapping]] = ..., reset: _Optional[_Union[Command.Reset, _Mapping]] = ..., raw_command: _Optional[_Union[Command.SendRawCommand, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("com_port",)
    COM_PORT_FIELD_NUMBER: _ClassVar[int]
    com_port: str
    def __init__(self, com_port: _Optional[str] = ...) -> None: ...
