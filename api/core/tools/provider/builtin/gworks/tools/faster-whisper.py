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

        # デフォルトモデルの指定
        #model = "Systran/faster-distil-whisper-large-v3"
        model = "Systran/faster-whisper-large-v3"
        language = tool_parameters.get("language", "en")

        audio_binary = io.BytesIO(download(audio_file))
        mime_type = get_attr(file=audio_file, attr=FileAttribute.MIME_TYPE)
        file_data = audio_binary.getvalue()

        try:
            files = {"file": ("audio_file", file_data, mime_type)}
            data = {
                "model": model,
                "task": "transcribe",  # 固定値
                "language": language,
                "response_format": "verbose_json",
                "timestamp_granularities": ["segment"],
                "prompt": "",
                "hotwords": "",
                "temperature": 0.0,
                "stream": False,
            }
            response = requests.post(
                "http://faster-whisper-server:8000/v1/audio/transcriptions",
                files=files,
                data=data
            )
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
                human_description=I18nObject(
                    en_US="The audio file to be transcribed.", 
                    ja_JP="文字起こし対象のオーディオファイル。"
                ),
                type="file",
                form=ToolParameter.ToolParameterForm.LLM,
                required=True
            ),
            ToolParameter(
                name="language",
                label=I18nObject(en_US="Language", ja_JP="言語"),
                human_description=I18nObject(
                    en_US="Language of the audio file (e.g., en, ja, fr).", 
                    ja_JP="オーディオファイルの言語（例：en, ja, fr）。"
                ),
                type="string",
                form=ToolParameter.ToolParameterForm.LLM,
                required=False,
                default="en"
            )
        ]