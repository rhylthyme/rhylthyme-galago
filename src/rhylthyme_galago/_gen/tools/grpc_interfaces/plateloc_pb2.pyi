from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("seal", "set_temperature", "set_seal_time", "get_actual_temperature", "stage_in", "stage_out", "show_diagnostics")
    class Seal(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class SetTemperature(_message.Message):
        __slots__ = ("temperature",)
        TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        temperature: int
        def __init__(self, temperature: _Optional[int] = ...) -> None: ...
    class SetSealTime(_message.Message):
        __slots__ = ("time",)
        TIME_FIELD_NUMBER: _ClassVar[int]
        time: float
        def __init__(self, time: _Optional[float] = ...) -> None: ...
    class GetActualTemperature(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class StageIn(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class StageOut(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ShowDiagsDialog(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SEAL_FIELD_NUMBER: _ClassVar[int]
    SET_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SET_SEAL_TIME_FIELD_NUMBER: _ClassVar[int]
    GET_ACTUAL_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    STAGE_IN_FIELD_NUMBER: _ClassVar[int]
    STAGE_OUT_FIELD_NUMBER: _ClassVar[int]
    SHOW_DIAGNOSTICS_FIELD_NUMBER: _ClassVar[int]
    seal: Command.Seal
    set_temperature: Command.SetTemperature
    set_seal_time: Command.SetSealTime
    get_actual_temperature: Command.GetActualTemperature
    stage_in: Command.StageIn
    stage_out: Command.StageOut
    show_diagnostics: Command.ShowDiagsDialog
    def __init__(self, seal: _Optional[_Union[Command.Seal, _Mapping]] = ..., set_temperature: _Optional[_Union[Command.SetTemperature, _Mapping]] = ..., set_seal_time: _Optional[_Union[Command.SetSealTime, _Mapping]] = ..., get_actual_temperature: _Optional[_Union[Command.GetActualTemperature, _Mapping]] = ..., stage_in: _Optional[_Union[Command.StageIn, _Mapping]] = ..., stage_out: _Optional[_Union[Command.StageOut, _Mapping]] = ..., show_diagnostics: _Optional[_Union[Command.ShowDiagsDialog, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("profile",)
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    profile: str
    def __init__(self, profile: _Optional[str] = ...) -> None: ...
