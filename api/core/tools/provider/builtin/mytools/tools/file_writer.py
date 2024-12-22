import base64
from typing import Any
from enum import Enum

from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter, ToolParameterOption
from core.tools.tool.builtin_tool import BuiltinTool


class ContentType(str, Enum):
    TEXT = "text"
    BINARY = "binary"


class FileWriterTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        content = tool_parameters.get("content")
        content_type = tool_parameters.get("content_type", ContentType.TEXT)
        
        try:
            # コンテンツタイプに応じた処理
            if content_type == ContentType.BINARY:
                # バイナリデータをそのまま使用
                binary_content = content
                mime_type = "application/octet-stream"
            else:
                # テキストコンテンツ
                binary_content = content.encode('utf-8')
                mime_type = "text/plain"
            
            # Difyシステムにファイルを返す
            return [
                self.create_text_message("Successfully prepared content"),
                self.create_blob_message(
                    blob=binary_content,
                    meta={"mime_type": mime_type},
                    save_as=self.VariableKey.CUSTOM.value,
                ),
            ]
            
        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        parameters = []
        
        # コンテンツタイプの選択
        parameters.append(
            ToolParameter(
                name="content_type",
                label=I18nObject(
                    en_US="Content Type",
                    ja_JP="コンテンツタイプ"
                ),
                human_description=I18nObject(
                    en_US="Type of the content (text or binary)",
                    ja_JP="コンテンツの種類（テキストまたはバイナリ）"
                ),
                type=ToolParameter.ToolParameterType.SELECT,
                options=[
                    ToolParameterOption(
                        value=ContentType.TEXT,
                        label=I18nObject(
                            en_US="Text",
                            ja_JP="テキスト"
                        )
                    ),
                    ToolParameterOption(
                        value=ContentType.BINARY,
                        label=I18nObject(
                            en_US="Binary",
                            ja_JP="バイナリ"
                        )
                    )
                ],
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )
        
        # コンテンツパラメータ
        parameters.append(
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
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )
        
        return parameters
