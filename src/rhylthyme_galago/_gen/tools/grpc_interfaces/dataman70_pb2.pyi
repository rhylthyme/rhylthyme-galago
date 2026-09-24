from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("scan", "assert_barcode")
    class Scan(_message.Message):
        __slots__ = ("mapped_variable",)
        MAPPED_VARIABLE_FIELD_NUMBER: _ClassVar[int]
        mapped_variable: str
        def __init__(self, mapped_variable: _Optional[str] = ...) -> None: ...
    class AssertBarcode(_message.Message):
        __slots__ = ("barcode",)
        BARCODE_FIELD_NUMBER: _ClassVar[int]
        barcode: str
        def __init__(self, barcode: _Optional[str] = ...) -> None: ...
    SCAN_FIELD_NUMBER: _ClassVar[int]
    ASSERT_BARCODE_FIELD_NUMBER: _ClassVar[int]
    scan: Command.Scan
    assert_barcode: Command.AssertBarcode
    def __init__(self, scan: _Optional[_Union[Command.Scan, _Mapping]] = ..., assert_barcode: _Optional[_Union[Command.AssertBarcode, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("com_port",)
    COM_PORT_FIELD_NUMBER: _ClassVar[int]
    com_port: str
    def __init__(self, com_port: _Optional[str] = ...) -> None: ...
