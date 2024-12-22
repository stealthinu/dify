import base64
import os
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
        filename = tool_parameters.get("filename")
        content_type = tool_parameters.get("content_type", ContentType.TEXT)
        
        # ファイル名のバリデーション
        if not filename or not isinstance(filename, str):
            return [self.create_text_message("Invalid filename")]
        
        try:
            # コンテンツタイプに応じた処理
            if content_type == ContentType.BINARY:
                try:
                    # Base64デコード
                    binary_content = base64.b64decode(content)
                    mime_type = "application/octet-stream"
                except base64.binascii.Error:
                    return [self.create_text_message("Invalid base64 encoded binary content")]
            else:
                # テキストコンテンツ
                binary_content = content.encode('utf-8')
                mime_type = "text/plain"
            
            # Difyシステムにファイルを返す
            return [
                self.create_text_message(f"Successfully prepared content for {filename}"),
                self.create_blob_message(
                    blob=binary_content,
                    meta={"mime_type": mime_type, "filename": filename},
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
                            en_US="Binary (Base64)",
                            ja_JP="バイナリ（Base64）"
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
                    en_US="The content to write to the file. For binary data, provide base64 encoded string",
                    ja_JP="ファイルに書き込む内容。バイナリデータの場合は、Base64エンコードされた文字列を指定してください"
                ),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )
        
        # ファイル名パラメータ
        parameters.append(
            ToolParameter(
                name="filename",
                label=I18nObject(
                    en_US="Filename",
                    ja_JP="ファイル名"
                ),
                human_description=I18nObject(
                    en_US="The name of the file to create",
                    ja_JP="作成するファイルの名前"
                ),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )
        
        return parameters
