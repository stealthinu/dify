from typing import Any

from core.tools.entities.common_entities import I18nObject
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter
from core.tools.tool.builtin_tool import BuiltinTool


class FileWriterTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        content = tool_parameters.get("content")
        
        if not content:
            return [self.create_text_message("No content provided")]

        try:
            # コンテンツをUTF-8でエンコード
            binary_content = content.encode('utf-8')

            # Difyシステムにファイルを返す
            return [
                self.create_text_message("Successfully prepared content"),
                self.create_blob_message(
                    blob=binary_content,
                    meta={"mime_type": "text/plain"},
                    save_as=self.VariableKey.CUSTOM.value,
                ),
            ]
            
        except Exception as e:
            return [self.create_text_message(f"Failed to process file: {str(e)}")]

    def get_runtime_parameters(self) -> list[ToolParameter]:
        parameters = []

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
                form=ToolParameter.ToolParameterForm.LLM,
                required=True
            )
        )

        return parameters