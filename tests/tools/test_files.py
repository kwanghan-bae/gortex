
import unittest
import os
import shutil
import tempfile
from gortex.core.tools.files import FindByNameTool, GrepSearchTool

class TestFileTools(unittest.TestCase):
    def setUp(self):
        # 테스트용 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 더미 파일 생성
        os.makedirs("src/core", exist_ok=True)
        os.makedirs("src/utils", exist_ok=True)
        os.makedirs(".git", exist_ok=True)
        os.makedirs("venv", exist_ok=True)
        
        self.create_file("src/core/main.py", "print('Hello, Core!')")
        self.create_file("src/utils/helper.py", "def help(): pass")
        self.create_file("src/utils/config.py", "SECRET = 'hidden'")
        self.create_file("README.md", "# Project Title")
        self.create_file(".git/config", "[core]")
        self.create_file("venv/bin/activate", "export PATH=...")
        self.create_file(".gitignore", "venv/\n*.log")

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.test_dir)

    def create_file(self, path, content):
        if os.path.dirname(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)

    def test_find_by_name(self):
        """FindByNameTool: 패턴 매칭 및 gitignore 동작 테스트"""
        finder = FindByNameTool()
        
        # 1. 기본 파이썬 파일 검색
        results = finder.execute(pattern="*.py", path=".")
        self.assertIn("src/core/main.py", results)
        self.assertIn("src/utils/helper.py", results)
        
        # 2. Ignored 파일 제외 확인 (venv 내부)
        self.assertNotIn("venv/bin/activate", results)

    def test_grep_search(self):
        """GrepSearchTool: 텍스트 검색 테스트"""
        searcher = GrepSearchTool()
        
        # 1. 일반 문자열 검색
        results = searcher.execute(query="Hello", path=".")
        self.assertTrue(any(res['file'] == "src/core/main.py" for res in results))
        
        # 2. 결과 포맷 확인
        # 결과는 "filepath:line_number: content" 형식을 기대하거나 딕셔너리 리스트일 수 있음.
        # 구현 계획에 따라 딕셔너리 리스트 반환을 가정.
        # [{"file": "...", "line": 1, "content": "..."}]
        
        hits = [r for r in results if r['file'] == "src/core/main.py"]
        self.assertEqual(len(hits), 1)
        self.assertIn("Hello, Core!", hits[0]['content'])

if __name__ == '__main__':
    unittest.main()
