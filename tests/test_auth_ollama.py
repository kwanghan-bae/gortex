import unittest
from unittest.mock import MagicMock, patch
from gortex.core.auth import GortexAuth

class TestGortexAuthOllama(unittest.TestCase):
    def setUp(self):
        GortexAuth._reset()
        self.auth = GortexAuth()

    @patch("requests.get")
    def test_check_ollama_connection_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(self.auth.check_ollama_connection())

    @patch("requests.get")
    def test_list_ollama_models(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3:latest"}, {"name": "qwen2.5-coder:7b"}]
        }
        mock_get.return_value = mock_response
        models = self.auth.list_ollama_models()
        self.assertIn("llama3:latest", models)
        self.assertIn("qwen2.5-coder:7b", models)

    def test_role_mapping_v3_standard(self):
        # docs/OLLAMA.md 기준 매핑 확인
        self.auth.set_provider("ollama")
        # GortexAuth의 role_map이 업데이트되어야 함
        # 현재 코드에서는 _generate_ollama 내부에 하드코딩되어 있으므로 이를 클래스 속성으로 추출할 필요가 있음
        pass

if __name__ == "__main__":
    unittest.main()
