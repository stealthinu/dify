import io
import os
import base64
from typing import Any
from enum import Enum

from core.file.enums import FileType
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
            
        # 安全なファイルパスの作成（ディレクトリトラバーサル対策）
        safe_filename = os.path.basename(filename)
        
        try:
            # 出力ディレクトリの作成（存在しない場合）
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # ファイルパスの生成
            file_path = os.path.join(output_dir, safe_filename)
            
            # コンテンツタイプに応じた書き込み処理
            if content_type == ContentType.BINARY:
                try:
                    # Base64デコード
                    binary_content = base64.b64decode(content)
                    with open(file_path, 'wb') as f:
                        f.write(binary_content)
                except base64.binascii.Error:
                    return [self.create_text_message("Invalid base64 encoded binary content")]
            else:
                # テキストとして書き込み
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return [self.create_text_message(f"Successfully wrote content to {safe_filename}")]
            
        except Exception as e:
            return [self.create_text_message(f"Failed to write file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        parameters = []
        
        # コンテンツタイプの選択
        parameters.append(
            ToolParameter(
                name="content_type",
                label=I18nObject(
                    en_US="Content Type",
                    zh_Hans="内容类型",
                    ja_JP="コンテンツタイプ"
                ),
                human_description=I18nObject(
                    en_US="Type of the content (text or binary)",
                    zh_Hans="内容的类型（文本或二进制）",
                    ja_JP="コンテンツの種類（テキストまたはバイナリ）"
                ),
                type=ToolParameter.ToolParameterType.SELECT,
                options=[
                    ToolParameterOption(
                        value=ContentType.TEXT,
                        label=I18nObject(
                            en_US="Text",
                            zh_Hans="文本",
                            ja_JP="テキスト"
                        )
                    ),
                    ToolParameterOption(
                        value=ContentType.BINARY,
                        label=I18nObject(
                            en_US="Binary (Base64)",
                            zh_Hans="二进制（Base64）",
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
                    zh_Hans="内容",
                    ja_JP="内容"
                ),
                human_description=I18nObject(
                    en_US="The content to write to the file. For binary data, provide base64 encoded string",
                    zh_Hans="要写入文件的内容。对于二进制数据，请提供base64编码的字符串",
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
                    zh_Hans="文件名",
                    ja_JP="ファイル名"
                ),
                human_description=I18nObject(
                    en_US="The name of the file to create",
                    zh_Hans="要创建的文件名",
                    ja_JP="作成するファイルの名前"
                ),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True
            )
        )
        
        return parameters

