from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("home", "dispense")
    class Home(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Dispense(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    HOME_FIELD_NUMBER: _ClassVar[int]
    DISPENSE_FIELD_NUMBER: _ClassVar[int]
    home: Command.Home
    dispense: Command.Dispense
    def __init__(self, home: _Optional[_Union[Command.Home, _Mapping]] = ..., dispense: _Optional[_Union[Command.Dispense, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("port",)
    PORT_FIELD_NUMBER: _ClassVar[int]
    port: int
    def __init__(self, port: _Optional[int] = ...) -> None: ...
