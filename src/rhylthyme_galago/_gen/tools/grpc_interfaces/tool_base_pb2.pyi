from google.protobuf import struct_pb2 as _struct_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import liconic_pb2 as _liconic_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import opentrons2_pb2 as _opentrons2_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import pf400_pb2 as _pf400_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import cytation_pb2 as _cytation_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import dataman70_pb2 as _dataman70_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import spectramax_pb2 as _spectramax_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import bioshake_pb2 as _bioshake_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import hig_centrifuge_pb2 as _hig_centrifuge_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import bravo_pb2 as _bravo_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import multidrop_pb2 as _multidrop_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import vcode_pb2 as _vcode_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import plateloc_pb2 as _plateloc_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import xpeel_pb2 as _xpeel_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import alps3000_pb2 as _alps3000_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import toolbox_pb2 as _toolbox_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import hamilton_pb2 as _hamilton_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import microserve_pb2 as _microserve_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import vprep_pb2 as _vprep_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import plr_pb2 as _plr_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import pyhamilton_pb2 as _pyhamilton_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import clariostar_pb2 as _clariostar_pb2
from rhylthyme_galago._gen.tools.grpc_interfaces import lcus1_relay_pb2 as _lcus1_relay_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_RESPONSE: _ClassVar[ResponseCode]
    SUCCESS: _ClassVar[ResponseCode]
    WRONG_TOOL: _ClassVar[ResponseCode]
    UNRECOGNIZED_COMMAND: _ClassVar[ResponseCode]
    INVALID_ARGUMENTS: _ClassVar[ResponseCode]
    DRIVER_ERROR: _ClassVar[ResponseCode]
    NOT_READY: _ClassVar[ResponseCode]
    ERROR_FROM_TOOL: _ClassVar[ResponseCode]

class ToolStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_STATUS: _ClassVar[ToolStatus]
    NOT_CONFIGURED: _ClassVar[ToolStatus]
    INITIALIZING: _ClassVar[ToolStatus]
    READY: _ClassVar[ToolStatus]
    BUSY: _ClassVar[ToolStatus]
    FAILED: _ClassVar[ToolStatus]
    OFFLINE: _ClassVar[ToolStatus]
    SIMULATED: _ClassVar[ToolStatus]
UNKNOWN_RESPONSE: ResponseCode
SUCCESS: ResponseCode
WRONG_TOOL: ResponseCode
UNRECOGNIZED_COMMAND: ResponseCode
INVALID_ARGUMENTS: ResponseCode
DRIVER_ERROR: ResponseCode
NOT_READY: ResponseCode
ERROR_FROM_TOOL: ResponseCode
UNKNOWN_STATUS: ToolStatus
NOT_CONFIGURED: ToolStatus
INITIALIZING: ToolStatus
READY: ToolStatus
BUSY: ToolStatus
FAILED: ToolStatus
OFFLINE: ToolStatus
SIMULATED: ToolStatus

class Command(_message.Message):
    __slots__ = ("cytation", "opentrons2", "pf400", "liconic", "dataman70", "spectramax", "bioshake", "hig_centrifuge", "bravo", "multidrop", "vcode", "plateloc", "xpeel", "alps3000", "toolbox", "hamilton", "microserve", "vprep", "plr", "pyhamilton", "clariostar", "lcus1_relay")
    CYTATION_FIELD_NUMBER: _ClassVar[int]
    OPENTRONS2_FIELD_NUMBER: _ClassVar[int]
    PF400_FIELD_NUMBER: _ClassVar[int]
    LICONIC_FIELD_NUMBER: _ClassVar[int]
    DATAMAN70_FIELD_NUMBER: _ClassVar[int]
    SPECTRAMAX_FIELD_NUMBER: _ClassVar[int]
    BIOSHAKE_FIELD_NUMBER: _ClassVar[int]
    HIG_CENTRIFUGE_FIELD_NUMBER: _ClassVar[int]
    BRAVO_FIELD_NUMBER: _ClassVar[int]
    MULTIDROP_FIELD_NUMBER: _ClassVar[int]
    VCODE_FIELD_NUMBER: _ClassVar[int]
    PLATELOC_FIELD_NUMBER: _ClassVar[int]
    XPEEL_FIELD_NUMBER: _ClassVar[int]
    ALPS3000_FIELD_NUMBER: _ClassVar[int]
    TOOLBOX_FIELD_NUMBER: _ClassVar[int]
    HAMILTON_FIELD_NUMBER: _ClassVar[int]
    MICROSERVE_FIELD_NUMBER: _ClassVar[int]
    VPREP_FIELD_NUMBER: _ClassVar[int]
    PLR_FIELD_NUMBER: _ClassVar[int]
    PYHAMILTON_FIELD_NUMBER: _ClassVar[int]
    CLARIOSTAR_FIELD_NUMBER: _ClassVar[int]
    LCUS1_RELAY_FIELD_NUMBER: _ClassVar[int]
    cytation: _cytation_pb2.Command
    opentrons2: _opentrons2_pb2.Command
    pf400: _pf400_pb2.Command
    liconic: _liconic_pb2.Command
    dataman70: _dataman70_pb2.Command
    spectramax: _spectramax_pb2.Command
    bioshake: _bioshake_pb2.Command
    hig_centrifuge: _hig_centrifuge_pb2.Command
    bravo: _bravo_pb2.Command
    multidrop: _multidrop_pb2.Command
    vcode: _vcode_pb2.Command
    plateloc: _plateloc_pb2.Command
    xpeel: _xpeel_pb2.Command
    alps3000: _alps3000_pb2.Command
    toolbox: _toolbox_pb2.Command
    hamilton: _hamilton_pb2.Command
    microserve: _microserve_pb2.Command
    vprep: _vprep_pb2.Command
    plr: _plr_pb2.Command
    pyhamilton: _pyhamilton_pb2.Command
    clariostar: _clariostar_pb2.Command
    lcus1_relay: _lcus1_relay_pb2.Command
    def __init__(self, cytation: _Optional[_Union[_cytation_pb2.Command, _Mapping]] = ..., opentrons2: _Optional[_Union[_opentrons2_pb2.Command, _Mapping]] = ..., pf400: _Optional[_Union[_pf400_pb2.Command, _Mapping]] = ..., liconic: _Optional[_Union[_liconic_pb2.Command, _Mapping]] = ..., dataman70: _Optional[_Union[_dataman70_pb2.Command, _Mapping]] = ..., spectramax: _Optional[_Union[_spectramax_pb2.Command, _Mapping]] = ..., bioshake: _Optional[_Union[_bioshake_pb2.Command, _Mapping]] = ..., hig_centrifuge: _Optional[_Union[_hig_centrifuge_pb2.Command, _Mapping]] = ..., bravo: _Optional[_Union[_bravo_pb2.Command, _Mapping]] = ..., multidrop: _Optional[_Union[_multidrop_pb2.Command, _Mapping]] = ..., vcode: _Optional[_Union[_vcode_pb2.Command, _Mapping]] = ..., plateloc: _Optional[_Union[_plateloc_pb2.Command, _Mapping]] = ..., xpeel: _Optional[_Union[_xpeel_pb2.Command, _Mapping]] = ..., alps3000: _Optional[_Union[_alps3000_pb2.Command, _Mapping]] = ..., toolbox: _Optional[_Union[_toolbox_pb2.Command, _Mapping]] = ..., hamilton: _Optional[_Union[_hamilton_pb2.Command, _Mapping]] = ..., microserve: _Optional[_Union[_microserve_pb2.Command, _Mapping]] = ..., vprep: _Optional[_Union[_vprep_pb2.Command, _Mapping]] = ..., plr: _Optional[_Union[_plr_pb2.Command, _Mapping]] = ..., pyhamilton: _Optional[_Union[_pyhamilton_pb2.Command, _Mapping]] = ..., clariostar: _Optional[_Union[_clariostar_pb2.Command, _Mapping]] = ..., lcus1_relay: _Optional[_Union[_lcus1_relay_pb2.Command, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ("simulated", "toolId", "cytation", "opentrons2", "pf400", "liconic", "dataman70", "spectramax", "bioshake", "hig_centrifuge", "bravo", "multidrop", "vcode", "plateloc", "xpeel", "alps3000", "toolbox", "hamilton", "microserve", "vprep", "plr", "pyhamilton", "clariostar", "lcus1_relay")
    SIMULATED_FIELD_NUMBER: _ClassVar[int]
    TOOLID_FIELD_NUMBER: _ClassVar[int]
    CYTATION_FIELD_NUMBER: _ClassVar[int]
    OPENTRONS2_FIELD_NUMBER: _ClassVar[int]
    PF400_FIELD_NUMBER: _ClassVar[int]
    LICONIC_FIELD_NUMBER: _ClassVar[int]
    DATAMAN70_FIELD_NUMBER: _ClassVar[int]
    SPECTRAMAX_FIELD_NUMBER: _ClassVar[int]
    BIOSHAKE_FIELD_NUMBER: _ClassVar[int]
    HIG_CENTRIFUGE_FIELD_NUMBER: _ClassVar[int]
    BRAVO_FIELD_NUMBER: _ClassVar[int]
    MULTIDROP_FIELD_NUMBER: _ClassVar[int]
    VCODE_FIELD_NUMBER: _ClassVar[int]
    PLATELOC_FIELD_NUMBER: _ClassVar[int]
    XPEEL_FIELD_NUMBER: _ClassVar[int]
    ALPS3000_FIELD_NUMBER: _ClassVar[int]
    TOOLBOX_FIELD_NUMBER: _ClassVar[int]
    HAMILTON_FIELD_NUMBER: _ClassVar[int]
    MICROSERVE_FIELD_NUMBER: _ClassVar[int]
    VPREP_FIELD_NUMBER: _ClassVar[int]
    PLR_FIELD_NUMBER: _ClassVar[int]
    PYHAMILTON_FIELD_NUMBER: _ClassVar[int]
    CLARIOSTAR_FIELD_NUMBER: _ClassVar[int]
    LCUS1_RELAY_FIELD_NUMBER: _ClassVar[int]
    simulated: bool
    toolId: str
    cytation: _cytation_pb2.Config
    opentrons2: _opentrons2_pb2.Config
    pf400: _pf400_pb2.Config
    liconic: _liconic_pb2.Config
    dataman70: _dataman70_pb2.Config
    spectramax: _spectramax_pb2.Config
    bioshake: _bioshake_pb2.Config
    hig_centrifuge: _hig_centrifuge_pb2.Config
    bravo: _bravo_pb2.Config
    multidrop: _multidrop_pb2.Config
    vcode: _vcode_pb2.Config
    plateloc: _plateloc_pb2.Config
    xpeel: _xpeel_pb2.Config
    alps3000: _alps3000_pb2.Config
    toolbox: _toolbox_pb2.Config
    hamilton: _hamilton_pb2.Config
    microserve: _microserve_pb2.Config
    vprep: _vprep_pb2.Config
    plr: _plr_pb2.Config
    pyhamilton: _pyhamilton_pb2.Config
    clariostar: _clariostar_pb2.Config
    lcus1_relay: _lcus1_relay_pb2.Config
    def __init__(self, simulated: _Optional[bool] = ..., toolId: _Optional[str] = ..., cytation: _Optional[_Union[_cytation_pb2.Config, _Mapping]] = ..., opentrons2: _Optional[_Union[_opentrons2_pb2.Config, _Mapping]] = ..., pf400: _Optional[_Union[_pf400_pb2.Config, _Mapping]] = ..., liconic: _Optional[_Union[_liconic_pb2.Config, _Mapping]] = ..., dataman70: _Optional[_Union[_dataman70_pb2.Config, _Mapping]] = ..., spectramax: _Optional[_Union[_spectramax_pb2.Config, _Mapping]] = ..., bioshake: _Optional[_Union[_bioshake_pb2.Config, _Mapping]] = ..., hig_centrifuge: _Optional[_Union[_hig_centrifuge_pb2.Config, _Mapping]] = ..., bravo: _Optional[_Union[_bravo_pb2.Config, _Mapping]] = ..., multidrop: _Optional[_Union[_multidrop_pb2.Config, _Mapping]] = ..., vcode: _Optional[_Union[_vcode_pb2.Config, _Mapping]] = ..., plateloc: _Optional[_Union[_plateloc_pb2.Config, _Mapping]] = ..., xpeel: _Optional[_Union[_xpeel_pb2.Config, _Mapping]] = ..., alps3000: _Optional[_Union[_alps3000_pb2.Config, _Mapping]] = ..., toolbox: _Optional[_Union[_toolbox_pb2.Config, _Mapping]] = ..., hamilton: _Optional[_Union[_hamilton_pb2.Config, _Mapping]] = ..., microserve: _Optional[_Union[_microserve_pb2.Config, _Mapping]] = ..., vprep: _Optional[_Union[_vprep_pb2.Config, _Mapping]] = ..., plr: _Optional[_Union[_plr_pb2.Config, _Mapping]] = ..., pyhamilton: _Optional[_Union[_pyhamilton_pb2.Config, _Mapping]] = ..., clariostar: _Optional[_Union[_clariostar_pb2.Config, _Mapping]] = ..., lcus1_relay: _Optional[_Union[_lcus1_relay_pb2.Config, _Mapping]] = ...) -> None: ...

class ExecuteCommandReply(_message.Message):
    __slots__ = ("response", "error_message", "return_reply", "meta_data")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RETURN_REPLY_FIELD_NUMBER: _ClassVar[int]
    META_DATA_FIELD_NUMBER: _ClassVar[int]
    response: ResponseCode
    error_message: str
    return_reply: bool
    meta_data: _struct_pb2.Struct
    def __init__(self, response: _Optional[_Union[ResponseCode, str]] = ..., error_message: _Optional[str] = ..., return_reply: _Optional[bool] = ..., meta_data: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class EstimateDurationReply(_message.Message):
    __slots__ = ("response", "estimated_duration_seconds", "error_message")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    response: ResponseCode
    estimated_duration_seconds: int
    error_message: str
    def __init__(self, response: _Optional[_Union[ResponseCode, str]] = ..., estimated_duration_seconds: _Optional[int] = ..., error_message: _Optional[str] = ...) -> None: ...

class ConfigureReply(_message.Message):
    __slots__ = ("response", "error_message")
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    response: ResponseCode
    error_message: str
    def __init__(self, response: _Optional[_Union[ResponseCode, str]] = ..., error_message: _Optional[str] = ...) -> None: ...

class StatusReply(_message.Message):
    __slots__ = ("uptime", "status", "error_message")
    UPTIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    uptime: int
    status: ToolStatus
    error_message: str
    def __init__(self, uptime: _Optional[int] = ..., status: _Optional[_Union[ToolStatus, str]] = ..., error_message: _Optional[str] = ...) -> None: ...
