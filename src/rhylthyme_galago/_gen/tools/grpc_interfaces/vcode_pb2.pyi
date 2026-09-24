from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("home", "print", "print_and_apply", "rotate_180", "rotate_stage", "show_diagnostics")
    class RotateStage(_message.Message):
        __slots__ = ("angle",)
        ANGLE_FIELD_NUMBER: _ClassVar[int]
        angle: int
        def __init__(self, angle: _Optional[int] = ...) -> None: ...
    class Home(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class PrintAndApply(_message.Message):
        __slots__ = ("format_name", "side", "drop_stage", "field_0", "field_1", "field_2", "field_3", "field_4", "field_5")
        FORMAT_NAME_FIELD_NUMBER: _ClassVar[int]
        SIDE_FIELD_NUMBER: _ClassVar[int]
        DROP_STAGE_FIELD_NUMBER: _ClassVar[int]
        FIELD_0_FIELD_NUMBER: _ClassVar[int]
        FIELD_1_FIELD_NUMBER: _ClassVar[int]
        FIELD_2_FIELD_NUMBER: _ClassVar[int]
        FIELD_3_FIELD_NUMBER: _ClassVar[int]
        FIELD_4_FIELD_NUMBER: _ClassVar[int]
        FIELD_5_FIELD_NUMBER: _ClassVar[int]
        format_name: str
        side: str
        drop_stage: bool
        field_0: str
        field_1: str
        field_2: str
        field_3: str
        field_4: str
        field_5: str
        def __init__(self, format_name: _Optional[str] = ..., side: _Optional[str] = ..., drop_stage: _Optional[bool] = ..., field_0: _Optional[str] = ..., field_1: _Optional[str] = ..., field_2: _Optional[str] = ..., field_3: _Optional[str] = ..., field_4: _Optional[str] = ..., field_5: _Optional[str] = ...) -> None: ...
    class DropStage(_message.Message):
        __slots__ = ("drop_stage",)
        DROP_STAGE_FIELD_NUMBER: _ClassVar[int]
        drop_stage: bool
        def __init__(self, drop_stage: _Optional[bool] = ...) -> None: ...
    class Print(_message.Message):
        __slots__ = ("format_name", "field_0", "field_1", "field_2", "field_3", "field_4", "field_5")
        FORMAT_NAME_FIELD_NUMBER: _ClassVar[int]
        FIELD_0_FIELD_NUMBER: _ClassVar[int]
        FIELD_1_FIELD_NUMBER: _ClassVar[int]
        FIELD_2_FIELD_NUMBER: _ClassVar[int]
        FIELD_3_FIELD_NUMBER: _ClassVar[int]
        FIELD_4_FIELD_NUMBER: _ClassVar[int]
        FIELD_5_FIELD_NUMBER: _ClassVar[int]
        format_name: str
        field_0: str
        field_1: str
        field_2: str
        field_3: str
        field_4: str
        field_5: str
        def __init__(self, format_name: _Optional[str] = ..., field_0: _Optional[str] = ..., field_1: _Optional[str] = ..., field_2: _Optional[str] = ..., field_3: _Optional[str] = ..., field_4: _Optional[str] = ..., field_5: _Optional[str] = ...) -> None: ...
    class Rotate180(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ShowDiagsDialog(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    HOME_FIELD_NUMBER: _ClassVar[int]
    PRINT_FIELD_NUMBER: _ClassVar[int]
    PRINT_AND_APPLY_FIELD_NUMBER: _ClassVar[int]
    ROTATE_180_FIELD_NUMBER: _ClassVar[int]
    ROTATE_STAGE_FIELD_NUMBER: _ClassVar[int]
    SHOW_DIAGNOSTICS_FIELD_NUMBER: _ClassVar[int]
    home: Command.Home
    print: Command.Print
    print_and_apply: Command.PrintAndApply
    rotate_180: Command.Rotate180
    rotate_stage: Command.RotateStage
    show_diagnostics: Command.ShowDiagsDialog
    def __init__(self, home: _Optional[_Union[Command.Home, _Mapping]] = ..., print: _Optional[_Union[Command.Print, _Mapping]] = ..., print_and_apply: _Optional[_Union[Command.PrintAndApply, _Mapping]] = ..., rotate_180: _Optional[_Union[Command.Rotate180, _Mapping]] = ..., rotate_stage: _Optional[_Union[Command.RotateStage, _Mapping]] = ..., show_diagnostics: _Optional[_Union[Command.ShowDiagsDialog, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("profile",)
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    profile: str
    def __init__(self, profile: _Optional[str] = ...) -> None: ...
