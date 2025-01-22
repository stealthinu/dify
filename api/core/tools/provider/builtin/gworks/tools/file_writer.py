from typing import Any

from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter, ToolParameterOption
from core.tools.tool.builtin_tool import BuiltinTool


class FileWriterTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        content = tool_parameters.get("content")
        file_type = tool_parameters.get("file_type", "text")
        file_name = tool_parameters.get("file_name", "file")
        
        if not content:
            return [self.create_text_message("No content provided")]

        try:
            # ファイル形式に応じた設定
            mime_types = {
                "text": "text/plain",
                "json": "application/json",
                "markdown": "text/markdown"
            }
            extensions = {
                "text": ".txt",
                "json": ".json",
                "markdown": ".md"
            }
            
            mime_type = mime_types.get(file_type, "text/plain")
            extension = extensions.get(file_type, ".txt")
            
            # テキストベースのコンテンツはUTF-8でエンコード
            binary_content = content.encode('utf-8')

            # Difyシステムにファイルを返す
            return [
                self.create_text_message("Successfully prepared content"),
                self.create_blob_message(
                    blob=binary_content,
                    meta={"mime_type": mime_type},
                    save_as=f"{file_name}{extension}"
                ),
            ]
            
        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="content",
                label=I18nObject(
                    en_US="Content",
                    ja_JP="内容"
                ),
                human_description=I18nObject(
                    en_US="The content to write to the file.",
                    ja_JP="ファイルに書き込む内容。"
                ),
                type="string",
                form=ToolParameter.ToolParameterForm.LLM,
                required=True
            ),
            ToolParameter(
                name="file_type",
                label=I18nObject(
                    en_US="File Type",
                    ja_JP="ファイル形式"
                ),
                human_description=I18nObject(
                    en_US="The type of file to create.",
                    ja_JP="作成するファイルの形式。"
                ),
                type="select",
                form=ToolParameter.ToolParameterForm.LLM,
                required=True,
                options=[
                    ToolParameterOption(value="text", label=I18nObject(en_US="Text", ja_JP="テキスト")),
                    ToolParameterOption(value="json", label=I18nObject(en_US="JSON", ja_JP="JSON")),
                    ToolParameterOption(value="markdown", label=I18nObject(en_US="Markdown", ja_JP="Markdown"))
                ],
                default="text"
            ),
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
        ]
