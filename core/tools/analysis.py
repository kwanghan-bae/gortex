
import os
import ast
from typing import List
from .base import BaseTool

class OutlineVisitor(ast.NodeVisitor):
    def __init__(self):
        self.outline = []
        self.indent_level = 0

    def visit_ClassDef(self, node):
        indent = "  " * self.indent_level
        # 베이스 클래스 정보 포함
        bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
        bases_str = f"({', '.join(bases)})" if bases else ""
        self.outline.append(f"{indent}class {node.name}{bases_str}:")
        
        self.indent_level += 1
        self.generic_visit(node)
        self.indent_level -= 1

    def visit_FunctionDef(self, node):
        indent = "  " * self.indent_level
        # 인자 정보 포맷팅 (간단하게)
        args_str = ", ".join([a.arg for a in node.args.args])
        if node.args.vararg: args_str += f", *{node.args.vararg.arg}"
        if node.args.kwarg: args_str += f", **{node.args.kwarg.arg}"
        
        self.outline.append(f"{indent}def {node.name}({args_str}):")

    def visit_AsyncFunctionDef(self, node):
        indent = "  " * self.indent_level
        args_str = ", ".join([a.arg for a in node.args.args])
        self.outline.append(f"{indent}async def {node.name}({args_str}):")

class ViewFileOutlineTool(BaseTool):
    """파이썬 파일의 구조(Outline)를 추출하여 요약"""

    def execute(self, path: str) -> str:
        if not os.path.exists(path):
            return f"❌ Error: File not found at {path}"

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                return f"❌ Error: Syntax Error in {os.path.basename(path)}: {e}"

            visitor = OutlineVisitor()
            visitor.visit(tree)
            
            if not visitor.outline:
                return f"ℹ️ No classes or functions found in {os.path.basename(path)}."
                
            return "\n".join(visitor.outline)

        except Exception as e:
            return f"❌ Error analyzing file: {str(e)}"
