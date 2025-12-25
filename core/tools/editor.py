
import os
import ast
from .base import BaseTool

class ReplaceFileContentTool(BaseTool):
    """파일 내용의 특정 블록을 안전하게 교체 (Unique Check & Syntax Validation)"""

    def execute(self, path: str, target_content: str, replacement_content: str) -> str:
        if not os.path.exists(path):
            return f"❌ Error: File not found at {path}"

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. 고유성 검사 (Unique Check)
            count = content.count(target_content)
            if count == 0:
                return f"❌ Error: Target content not found in {path}"
            if count > 1:
                return f"❌ Error: Target content found {count} times (multiple occurrences). Be more specific."

            # 2. 내용 교체
            new_content = content.replace(target_content, replacement_content)

            # 3. 문법 검증 (Syntax Validation) - Python 파일인 경우
            if path.endswith(".py"):
                try:
                    ast.parse(new_content)
                except SyntaxError as e:
                    return f"❌ Error: Replacement caused Syntax Error: {e}"
                except Exception as e:
                    # AST 파싱 중 기타 에러는 경고 수준으로 처리하거나 차단
                    return f"❌ Error: Code validation failed: {e}"

            # 4. 파일 쓰기
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return f"✅ Successfully replaced content in {path}"

        except Exception as e:
            return f"❌ Error: {str(e)}"
