
import unittest
import os
import shutil
import tempfile
from gortex.core.tools.analysis import ViewFileOutlineTool

class TestAnalysisTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.analyzer = ViewFileOutlineTool()
        
        # 샘플 파이썬 파일 생성 (클래스, 메서드, 함수 포함)
        self.sample_code = """
import os

class MyClass:
    def __init__(self):
        pass
        
    def my_method(self, arg1):
        return arg1

def global_function():
    print("global")
""".strip()
        self.create_file("complex.py", self.sample_code)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.test_dir)

    def create_file(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def test_view_outline(self):
        """AST 기반 파일 아웃라인 추출 테스트"""
        outline = self.analyzer.execute(path="complex.py")
        
        self.assertIn("class MyClass", outline)
        self.assertIn("def my_method(self, arg1)", outline)
        self.assertIn("def global_function", outline)
        # Import 문은 아웃라인에 포함되지 않거나 별도로 처리될 수 있음 (구현 의존)

    def test_syntax_error_handling(self):
        """문법 오류가 있는 파일 처리 테스트"""
        self.create_file("bad.py", "def broken_func(")
        
        result = self.analyzer.execute(path="bad.py")
        self.assertIn("Syntax Error", result)

if __name__ == '__main__':
    unittest.main()
