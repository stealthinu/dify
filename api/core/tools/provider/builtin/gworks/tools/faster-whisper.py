from typing import Any
import requests
import io

from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter
from core.tools.tool.builtin_tool import BuiltinTool
from core.file.enums import FileType, FileAttribute
from core.file.file_manager import download, get_attr

class FasterWhisperTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        audio_file = tool_parameters.get("audio_file")
        if not audio_file or audio_file.type != FileType.AUDIO:
            return [self.create_text_message("Not a valid audio file.")]

        task = tool_parameters.get("task", "transcribe")
        language = tool_parameters.get("language", "en")
        chunk_level = tool_parameters.get("chunk_level", "segment")
        version = tool_parameters.get("version", "3")

        audio_binary = io.BytesIO(download(audio_file))
        mime_type = get_attr(file=audio_file, attr=FileAttribute.MIME_TYPE)
        file_data = audio_binary.getvalue()

        try:
            files = {"file": ("audio_file", file_data, mime_type)}
            data = {"model": "whisper-1", "task": task, "language": language, "chunk_level": chunk_level, "version": version}
            response = requests.post("http://localhost:8000/v1/audio/transcriptions", files=files, data=data)
            response.raise_for_status()

            result = response.json()
            json_message = self.create_json_message(result)
            text = result.get("text", "")
            text_message = self.create_text_message(text)
            return [json_message, text_message]

        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="audio_file",
                label=I18nObject(en_US="Audio File", ja_JP="オーディオファイル"),
                human_description=I18nObject(en_US="The audio file to be transcribed.", ja_JP="文字起こし対象のオーディオファイル。"),
                type=ToolParameter.ToolParameterType.FILE,
                form=ToolParameter.ToolParameterForm.UPLOAD,
                required=True
            ),
            ToolParameter(
                name="task",
                label=I18nObject(en_US="Task", ja_JP="タスク"),
                human_description=I18nObject(en_US="Transcribe or translate", ja_JP="書き起こしか翻訳かを指定。"),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.INPUT,
                required=False
            ),
            ToolParameter(
                name="language",
                label=I18nObject(en_US="Language", ja_JP="言語"),
                human_description=I18nObject(en_US="Language of the audio file.", ja_JP="オーディオファイルの言語。"),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.INPUT,
                required=False
            ),
            ToolParameter(
                name="chunk_level",
                label=I18nObject(en_US="Chunk Level", ja_JP="チャンクレベル"),
                human_description=I18nObject(en_US="Segment or word level.", ja_JP="セグメント単位か単語単位か。"),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.INPUT,
                required=False
            ),
            ToolParameter(
                name="version",
                label=I18nObject(en_US="Model Version", ja_JP="モデルバージョン"),
                human_description=I18nObject(en_US="Which Whisper version to use.", ja_JP="使用するWhisperバージョン。"),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.INPUT,
                required=False
            )
        ]