from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("switch", "timed_switch")
    class Switch(_message.Message):
        __slots__ = ("on",)
        ON_FIELD_NUMBER: _ClassVar[int]
        on: bool
        def __init__(self, on: _Optional[bool] = ...) -> None: ...
    class TimedSwitch(_message.Message):
        __slots__ = ("duration_seconds",)
        DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
        duration_seconds: float
        def __init__(self, duration_seconds: _Optional[float] = ...) -> None: ...
    SWITCH_FIELD_NUMBER: _ClassVar[int]
    TIMED_SWITCH_FIELD_NUMBER: _ClassVar[int]
    switch: Command.Switch
    timed_switch: Command.TimedSwitch
    def __init__(self, switch: _Optional[_Union[Command.Switch, _Mapping]] = ..., timed_switch: _Optional[_Union[Command.TimedSwitch, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("com_port",)
    COM_PORT_FIELD_NUMBER: _ClassVar[int]
    com_port: str
    def __init__(self, com_port: _Optional[str] = ...) -> None: ...
