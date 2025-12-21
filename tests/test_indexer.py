import unittest
from unittest.mock import MagicMock, patch
from gortex.utils.indexer import SynapticIndexer
from gortex.core.auth import GortexAuth

class TestGortexSynapticIndexer(unittest.TestCase):
    def setUp(self):
        self.indexer = SynapticIndexer(root_dir=".")

    @patch('gortex.core.auth.GortexAuth')
    def test_semantic_search(self, mock_auth_cls):
        """자연어 질의를 통해 관련 심볼을 점수순으로 검색하는지 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.text = "class"
        mock_auth.generate.return_value = mock_response

        self.indexer.index = {
            "test.py": [
                {"name": "TestClass", "type": "class", "file": "test.py", "line": 10, "docstring": "A test class"},
                {"name": "OtherFunc", "type": "function", "file": "utils.py", "line": 5, "docstring": "Utility"}
            ]
        }

        results = self.indexer.search("class", normalize=True)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["name"], "TestClass")
        if len(results) > 1:
            self.assertTrue(results[0]["score"] >= results[1]["score"])

    def test_scan_project(self):
        """AST 파싱 및 인덱스 빌드 테스트"""
        with open("temp_index_test.py", "w") as f:
            f.write("class MyClass:\n    'Doc'\n    def my_method(self): pass\n")
        try:
            self.indexer.scan_project()
            found = False
            for defs in self.indexer.index.values():
                names = [d["name"] for d in defs]
                if "MyClass" in names and "my_method" in names:
                    found = True
                    break
            self.assertTrue(found)
        finally:
            import os
            if os.path.exists("temp_index_test.py"):
                os.remove("temp_index_test.py")

    def test_save_index(self):
        """인덱스 저장 테스트"""
        self.indexer.index = {"test.py": [{"name": "SavedSymbol"}]}
        self.indexer.index_path = "temp_index.json"
        self.indexer._save_index()
        import os
        self.assertTrue(os.path.exists("temp_index.json"))
        if os.path.exists("temp_index.json"):
            os.remove("temp_index.json")

    def test_generate_map_and_call_graph(self):
        """generate_map과 generate_call_graph가 정의된 심볼을 처리"""
        self.indexer.index = {
            "module.py": [
                {"type": "class", "name": "Base", "bases": [], "line": 1, "docstring": "Base"},
                {"type": "function", "name": "helper", "line": 5, "args": ["x"], "calls": ["compute"], "docstring": "Helper"},
                {"type": "function", "name": "compute", "line": 9, "args": [], "calls": [], "docstring": ""}
            ]
        }
        proj_map = self.indexer.generate_map()
        self.assertIn("module", proj_map["nodes"])
        call_graph = self.indexer.generate_call_graph()
        self.assertIn("module.py:helper", call_graph["nodes"])
        self.assertEqual(len(call_graph["edges"]), 1)

    def test_impact_radius(self):
        """get_impact_radius가 직접/간접 영향을 계산"""
        self.indexer.index = {
            "target.py": [
                {"type": "function", "name": "entry", "line": 1, "calls": [], "docstring": ""}
            ],
            "dependent.py": [
                {"type": "import", "name": "target", "line": 1},
                {"type": "function", "name": "use", "line": 5, "calls": ["entry"], "docstring": ""}
            ],
            "indirect.py": [
                {"type": "import", "name": "dependent", "line": 2}
            ]
        }
        radius = self.indexer.get_impact_radius("target.py")
        self.assertIn("dependent.py", radius["direct"])
        self.assertIn("indirect.py", radius["indirect"])

if __name__ == '__main__':
    unittest.main()
