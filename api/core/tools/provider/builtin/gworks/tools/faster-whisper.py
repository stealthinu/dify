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

        # パラメータを取得（デフォルト値付き）
        model = tool_parameters.get("model", "Systran/faster-whisper-large-v3")
        language = tool_parameters.get("language", "en")
        response_format = tool_parameters.get("response_format", "text")
        endpoint = tool_parameters.get("endpoint", "http://faster-whisper-server:8000").rstrip('/')

        audio_binary = io.BytesIO(download(audio_file))
        mime_type = get_attr(file=audio_file, attr=FileAttribute.MIME_TYPE)
        file_data = audio_binary.getvalue()

        try:
            files = {"file": ("audio_file", file_data, mime_type)}
            data = {
                "model": model,
                "task": "transcribe",  # 固定値
                "language": language,
                "response_format": response_format,
                "timestamp_granularities": ["segment"],
                "prompt": "",
                "hotwords": "",
                "temperature": 0.0,
                "stream": False,
            }
            response = requests.post(
                f"{endpoint}/v1/audio/transcriptions",
                files=files,
                data=data
            )
            response.raise_for_status()

            result = response.json()
            
            # response形式に応じて返却するメッセージを変更
            if response_format == "text":
                return [self.create_text_message(result)]
            else:  # json or verbose_json
                return [self.create_json_message(result)]

        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="audio_file",
                label=I18nObject(en_US="Audio File", ja_JP="音声ファイル"),
                human_description=I18nObject(
                    en_US="The audio file to be transcribed.", 
                    ja_JP="文字起こし対象の音声ファイル"
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
                    ja_JP="音声ファイルの言語（例：en, ja, fr）。"
                ),
                type="string",
                form=ToolParameter.ToolParameterForm.LLM,
                required=False,
                default="en"
            ),
            ToolParameter(
                name="response_format",
                label=I18nObject(en_US="Response Format", ja_JP="レスポンス形式"),
                human_description=I18nObject(
                    en_US="Format of the response.", 
                    ja_JP="レスポンスの形式"
                ),
                type="select",
                form=ToolParameter.ToolParameterForm.LLM,
                required=False,
                options=[
                    {"value": "text", "label": I18nObject(en_US="Text", ja_JP="テキスト")},
                    {"value": "json", "label": I18nObject(en_US="JSON", ja_JP="JSON")},
                    {"value": "verbose_json", "label": I18nObject(en_US="Verbose JSON", ja_JP="詳細なJSON")}
                ],
                default="text"
            ),
            ToolParameter(
                name="endpoint",
                label=I18nObject(en_US="API Endpoint", ja_JP="APIエンドポイント"),
                human_description=I18nObject(
                    en_US="API endpoint URL (default: http://faster-whisper-server:8000)", 
                    ja_JP="APIエンドポイントURL（デフォルト：http://faster-whisper-server:8000）"
                ),
                type="string",
                form=ToolParameter.ToolParameterForm.LLM,
                required=False,
                default="http://faster-whisper-server:8000"
            )
        ]