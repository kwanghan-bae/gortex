
import unittest
import os
import shutil
import tempfile
from gortex.core.tools.editor import ReplaceFileContentTool

class TestEditorTool(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.editor = ReplaceFileContentTool()
        
        # 샘플 파이썬 파일 생성
        self.sample_code = """
def hello():
    print("Hello, World!")
    print("Old Line")

def goodbye():
    print("Goodbye!")
""".strip()
        self.create_file("app.py", self.sample_code)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.test_dir)

    def create_file(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def test_replace_exact_match(self):
        """정확히 일치하는 블록 교체 테스트"""
        target = '    print("Old Line")'
        replacement = '    print("New Line")'
        
        result = self.editor.execute(path="app.py", target_content=target, replacement_content=replacement)
        
        self.assertIn("Successfully replaced", result)
        with open("app.py", "r") as f:
            content = f.read()
            self.assertIn('print("New Line")', content)
            self.assertNotIn('print("Old Line")', content)

    def test_replace_unique_check(self):
        """중복된 내용(Not Unique)이 있을 때 편집 거부 테스트"""
        # 중복 코드 생성
        code = """
print("dup")
print("unique")
print("dup")
"""
        self.create_file("dup.py", code.strip())
        
        result = self.editor.execute(path="dup.py", target_content='print("dup")', replacement_content='print("fixed")')
        
        # 실패 메시지 확인
        self.assertIn("Error", result)
        self.assertIn("multiple occurrences", result.lower())

    def test_syntax_validation(self):
        """편집 후 문법 오류(Syntax Error) 발생 시 롤백 또는 에러 리턴 테스트"""
        target = '    print("Old Line")'
        # 문법적으로 틀린 코드로 교체 (괄호 누락)
        replacement = '    print("Syntax Error"'
        
        result = self.editor.execute(path="app.py", target_content=target, replacement_content=replacement)
        
        self.assertIn("Syntax Error", result)
        # 파일 내용은 변경되지 않아야 함 (롤백 확인)
        with open("app.py", "r") as f:
            self.assertIn('print("Old Line")', f.read())

if __name__ == '__main__':
    unittest.main()
