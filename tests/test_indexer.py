import unittest
import os
import shutil
import json
from gortex.utils.indexer import SynapticIndexer

class TestGortexSynapticIndexer(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_workspace"
        os.makedirs(self.test_dir, exist_ok=True)
        # 테스트용 코드 파일 생성
        self.code = """
class TestClass:
    '''This is a test class docstring'''
    def test_method(self):
        '''Method docstring'''
        pass

def global_function():
    pass
"""
        with open(os.path.join(self.test_dir, "sample.py"), "w") as f: f.write(self.code)
        self.indexer = SynapticIndexer() # 인자 제거

    def tearDown(self):
        if os.path.exists(self.test_dir): shutil.rmtree(self.test_dir)
        # 기본 인덱스 파일 경로 정리 (기존 logs/synaptic_index.json 환경 주의)
        if os.path.exists("logs/synaptic_index.json"): os.remove("logs/synaptic_index.json")

    def test_symbol_extraction(self):
        """Python 파일에서 클래스와 메서드, 함수를 정확히 추출하는지 테스트"""
        # WORKING_DIR 환경 변수를 테스트 디렉토리로 임시 변경
        import os
        old_working_dir = os.environ.get("WORKING_DIR", ".")
        os.environ["WORKING_DIR"] = self.test_dir
        
        try:
            self.indexer.scan_project()
            
            # 인덱스 내용 확인 (file_path: [defs] 구조 대응)
            all_symbols = []
            for defs in self.indexer.index.values():
                all_symbols.extend(defs)
                
            symbol_names = [s["name"] for s in all_symbols if "name" in s]
            self.assertIn("TestClass", symbol_names)
            self.assertIn("test_method", symbol_names)
            self.assertIn("global_function", symbol_names)
        finally:
            os.environ["WORKING_DIR"] = old_working_dir

    def test_semantic_search(self):
        """자연어 질의를 통해 관련 심볼을 점수순으로 검색하는지 테스트"""
        import os
        old_working_dir = os.environ.get("WORKING_DIR", ".")
        os.environ["WORKING_DIR"] = self.test_dir
        
        try:
            self.indexer.scan_project()
            # 'class' 키워드로 검색
            results = self.indexer.search("class", normalize=True)
            self.assertTrue(len(results) > 0)
            self.assertEqual(results[0]["name"], "TestClass")
        finally:
            os.environ["WORKING_DIR"] = old_working_dir

if __name__ == '__main__':
    unittest.main()
