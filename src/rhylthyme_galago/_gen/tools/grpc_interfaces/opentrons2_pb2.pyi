from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("run_program", "pause", "resume", "cancel", "toggle_light")
    class RunProgram(_message.Message):
        __slots__ = ("script_content", "variables")
        SCRIPT_CONTENT_FIELD_NUMBER: _ClassVar[int]
        VARIABLES_FIELD_NUMBER: _ClassVar[int]
        script_content: str
        variables: _struct_pb2.Struct
        def __init__(self, script_content: _Optional[str] = ..., variables: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    class Pause(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Resume(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Cancel(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ToggleLight(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    RUN_PROGRAM_FIELD_NUMBER: _ClassVar[int]
    PAUSE_FIELD_NUMBER: _ClassVar[int]
    RESUME_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    TOGGLE_LIGHT_FIELD_NUMBER: _ClassVar[int]
    run_program: Command.RunProgram
    pause: Command.Pause
    resume: Command.Resume
    cancel: Command.Cancel
    toggle_light: Command.ToggleLight
    def __init__(self, run_program: _Optional[_Union[Command.RunProgram, _Mapping]] = ..., pause: _Optional[_Union[Command.Pause, _Mapping]] = ..., resume: _Optional[_Union[Command.Resume, _Mapping]] = ..., cancel: _Optional[_Union[Command.Cancel, _Mapping]] = ..., toggle_light: _Optional[_Union[Command.ToggleLight, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("robot_ip", "robot_port")
    ROBOT_IP_FIELD_NUMBER: _ClassVar[int]
    ROBOT_PORT_FIELD_NUMBER: _ClassVar[int]
    robot_ip: str
    robot_port: int
    def __init__(self, robot_ip: _Optional[str] = ..., robot_port: _Optional[int] = ...) -> None: ...
