from typing import Any

from core.file.enums import FileType
from core.file.file_manager import download
from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter
from core.tools.tool.builtin_tool import BuiltinTool


class FileUploaderTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        file = tool_parameters.get("file")
        if not file:
            return [self.create_text_message("No file provided")]

        try:
            file_binary = download(file)
            file_type = file.type

            # ファイル形式に応じた設定
            mime_types = {
                FileType.AUDIO: "audio/mpeg",
                FileType.VIDEO: "video/mp4",
                FileType.IMAGE: "image/jpeg",
                FileType.APPLICATION: "application/octet-stream"
            }
            extensions = {
                FileType.AUDIO: ".mp3",
                FileType.VIDEO: ".mp4",
                FileType.IMAGE: ".jpg",
                FileType.APPLICATION: ".bin"
            }

            mime_type = mime_types.get(file_type, "application/octet-stream")
            extension = extensions.get(file_type, ".bin")
            file_name = tool_parameters.get("file_name", "file")

            return [
                self.create_text_message("Successfully processed file"),
                self.create_blob_message(
                    blob=file_binary,
                    meta={"mime_type": mime_type},
                    save_as=f"{file_name}{extension}"
                ),
            ]

        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        parameters = []

        # ファイルパラメータ
        parameters.append(
            ToolParameter(
                name="file",
                label=I18nObject(
                    en_US="File",
                    ja_JP="ファイル"
                ),
                human_description=I18nObject(
                    en_US="The file to be uploaded (audio, video, or other binary files).",
                    ja_JP="アップロードするファイル（音声、動画、その他のバイナリファイル）。"
                ),
                type="file",
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )

        # ファイル名パラメータ
        parameters.append(
            ToolParameter(
                name="file_name",
                label=I18nObject(
                    en_US="File Name",
                    ja_JP="ファイル名"
                ),
                human_description=I18nObject(
                    en_US="The name of the file (without extension).",
                    ja_JP="ファイル名（拡張子なし）。"
                ),
                type="string",
                form=ToolParameter.ToolParameterForm.LLM,
                required=True
            )
        )

        return parameters
