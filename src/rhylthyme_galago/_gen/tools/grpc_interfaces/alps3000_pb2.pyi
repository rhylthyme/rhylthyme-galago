from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("get_status", "seal_plate", "get_error", "set_temperature", "set_sealing_time", "get_sealing_temperature_setpoint", "get_sealing_time", "get_sealing_temperature_actual")
    class SetTemperature(_message.Message):
        __slots__ = ("temperature",)
        TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        temperature: int
        def __init__(self, temperature: _Optional[int] = ...) -> None: ...
    class SetSealTime(_message.Message):
        __slots__ = ("seal_time",)
        SEAL_TIME_FIELD_NUMBER: _ClassVar[int]
        seal_time: int
        def __init__(self, seal_time: _Optional[int] = ...) -> None: ...
    class GetInstrumentStatus(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class SealPlate(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetError(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetTemperatureActual(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetSealingTime(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GetTemperatureSetpoint(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    GET_STATUS_FIELD_NUMBER: _ClassVar[int]
    SEAL_PLATE_FIELD_NUMBER: _ClassVar[int]
    GET_ERROR_FIELD_NUMBER: _ClassVar[int]
    SET_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    SET_SEALING_TIME_FIELD_NUMBER: _ClassVar[int]
    GET_SEALING_TEMPERATURE_SETPOINT_FIELD_NUMBER: _ClassVar[int]
    GET_SEALING_TIME_FIELD_NUMBER: _ClassVar[int]
    GET_SEALING_TEMPERATURE_ACTUAL_FIELD_NUMBER: _ClassVar[int]
    get_status: Command.GetInstrumentStatus
    seal_plate: Command.SealPlate
    get_error: Command.GetError
    set_temperature: Command.SetTemperature
    set_sealing_time: Command.SetSealTime
    get_sealing_temperature_setpoint: Command.GetTemperatureSetpoint
    get_sealing_time: Command.SetSealTime
    get_sealing_temperature_actual: Command.GetTemperatureActual
    def __init__(self, get_status: _Optional[_Union[Command.GetInstrumentStatus, _Mapping]] = ..., seal_plate: _Optional[_Union[Command.SealPlate, _Mapping]] = ..., get_error: _Optional[_Union[Command.GetError, _Mapping]] = ..., set_temperature: _Optional[_Union[Command.SetTemperature, _Mapping]] = ..., set_sealing_time: _Optional[_Union[Command.SetSealTime, _Mapping]] = ..., get_sealing_temperature_setpoint: _Optional[_Union[Command.GetTemperatureSetpoint, _Mapping]] = ..., get_sealing_time: _Optional[_Union[Command.SetSealTime, _Mapping]] = ..., get_sealing_temperature_actual: _Optional[_Union[Command.GetTemperatureActual, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("profile", "com_port")
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    COM_PORT_FIELD_NUMBER: _ClassVar[int]
    profile: str
    com_port: str
    def __init__(self, profile: _Optional[str] = ..., com_port: _Optional[str] = ...) -> None: ...
