from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Command(_message.Message):
    __slots__ = ("slack_message", "run_script", "send_slack_alert", "clear_last_slack_alert", "write_to_json", "text_to_speech")
    class WriteToJson(_message.Message):
        __slots__ = ("struct_object", "file_path")
        STRUCT_OBJECT_FIELD_NUMBER: _ClassVar[int]
        FILE_PATH_FIELD_NUMBER: _ClassVar[int]
        struct_object: _struct_pb2.Struct
        file_path: str
        def __init__(self, struct_object: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., file_path: _Optional[str] = ...) -> None: ...
    class SlackMessage(_message.Message):
        __slots__ = ("message",)
        MESSAGE_FIELD_NUMBER: _ClassVar[int]
        message: str
        def __init__(self, message: _Optional[str] = ...) -> None: ...
    class TextToSpeech(_message.Message):
        __slots__ = ("text",)
        TEXT_FIELD_NUMBER: _ClassVar[int]
        text: str
        def __init__(self, text: _Optional[str] = ...) -> None: ...
    class RunScript(_message.Message):
        __slots__ = ("script_content", "blocking")
        SCRIPT_CONTENT_FIELD_NUMBER: _ClassVar[int]
        BLOCKING_FIELD_NUMBER: _ClassVar[int]
        script_content: str
        blocking: bool
        def __init__(self, script_content: _Optional[str] = ..., blocking: _Optional[bool] = ...) -> None: ...
    class SendSlackAlert(_message.Message):
        __slots__ = ("workcell", "tool", "protocol", "error_message")
        WORKCELL_FIELD_NUMBER: _ClassVar[int]
        TOOL_FIELD_NUMBER: _ClassVar[int]
        PROTOCOL_FIELD_NUMBER: _ClassVar[int]
        ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
        workcell: str
        tool: str
        protocol: str
        error_message: str
        def __init__(self, workcell: _Optional[str] = ..., tool: _Optional[str] = ..., protocol: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...
    class ClearLastSlackAlert(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class ValidateFolder(_message.Message):
        __slots__ = ("folder_path",)
        FOLDER_PATH_FIELD_NUMBER: _ClassVar[int]
        folder_path: str
        def __init__(self, folder_path: _Optional[str] = ...) -> None: ...
    SLACK_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RUN_SCRIPT_FIELD_NUMBER: _ClassVar[int]
    SEND_SLACK_ALERT_FIELD_NUMBER: _ClassVar[int]
    CLEAR_LAST_SLACK_ALERT_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_JSON_FIELD_NUMBER: _ClassVar[int]
    TEXT_TO_SPEECH_FIELD_NUMBER: _ClassVar[int]
    slack_message: Command.SlackMessage
    run_script: Command.RunScript
    send_slack_alert: Command.SendSlackAlert
    clear_last_slack_alert: Command.ClearLastSlackAlert
    write_to_json: Command.WriteToJson
    text_to_speech: Command.TextToSpeech
    def __init__(self, slack_message: _Optional[_Union[Command.SlackMessage, _Mapping]] = ..., run_script: _Optional[_Union[Command.RunScript, _Mapping]] = ..., send_slack_alert: _Optional[_Union[Command.SendSlackAlert, _Mapping]] = ..., clear_last_slack_alert: _Optional[_Union[Command.ClearLastSlackAlert, _Mapping]] = ..., write_to_json: _Optional[_Union[Command.WriteToJson, _Mapping]] = ..., text_to_speech: _Optional[_Union[Command.TextToSpeech, _Mapping]] = ...) -> None: ...

class Config(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
