from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("open_carrier", "close_carrier", "start_read", "set_temperature")
    class OpenCarrier(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class CloseCarrier(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class StartRead(_message.Message):
        __slots__ = ("protocol_name", "plate_id", "assay_id", "timepoint")
        PROTOCOL_NAME_FIELD_NUMBER: _ClassVar[int]
        PLATE_ID_FIELD_NUMBER: _ClassVar[int]
        ASSAY_ID_FIELD_NUMBER: _ClassVar[int]
        TIMEPOINT_FIELD_NUMBER: _ClassVar[int]
        protocol_name: str
        plate_id: str
        assay_id: str
        timepoint: str
        def __init__(self, protocol_name: _Optional[str] = ..., plate_id: _Optional[str] = ..., assay_id: _Optional[str] = ..., timepoint: _Optional[str] = ...) -> None: ...
    class SetTemperature(_message.Message):
        __slots__ = ("temperature",)
        TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
        temperature: float
        def __init__(self, temperature: _Optional[float] = ...) -> None: ...
    OPEN_CARRIER_FIELD_NUMBER: _ClassVar[int]
    CLOSE_CARRIER_FIELD_NUMBER: _ClassVar[int]
    START_READ_FIELD_NUMBER: _ClassVar[int]
    SET_TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    open_carrier: Command.OpenCarrier
    close_carrier: Command.CloseCarrier
    start_read: Command.StartRead
    set_temperature: Command.SetTemperature
    def __init__(self, open_carrier: _Optional[_Union[Command.OpenCarrier, _Mapping]] = ..., close_carrier: _Optional[_Union[Command.CloseCarrier, _Mapping]] = ..., start_read: _Optional[_Union[Command.StartRead, _Mapping]] = ..., set_temperature: _Optional[_Union[Command.SetTemperature, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("protocol_dir", "data_dir", "device_name", "output_dir")
    PROTOCOL_DIR_FIELD_NUMBER: _ClassVar[int]
    DATA_DIR_FIELD_NUMBER: _ClassVar[int]
    DEVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_DIR_FIELD_NUMBER: _ClassVar[int]
    protocol_dir: str
    data_dir: str
    device_name: str
    output_dir: str
    def __init__(self, protocol_dir: _Optional[str] = ..., data_dir: _Optional[str] = ..., device_name: _Optional[str] = ..., output_dir: _Optional[str] = ...) -> None: ...
