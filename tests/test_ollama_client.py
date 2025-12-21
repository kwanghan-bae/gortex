import unittest
from unittest.mock import MagicMock, patch
from gortex.core.llm.ollama_client import OllamaBackend

class TestOllamaBackend(unittest.TestCase):
    @patch("gortex.core.llm.ollama_client.requests.post")
    def test_generate_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Ollama Response"}}
        mock_post.return_value = mock_response

        backend = OllamaBackend(base_url="http://test-url")
        response = backend.generate("test-model", [{"role": "user", "content": "hi"}])
        
        self.assertEqual(response, "Ollama Response")
        mock_post.assert_called_once()
        
    @patch("gortex.core.llm.ollama_client.requests.get")
    def test_is_available(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(OllamaBackend().is_available())

        mock_get.side_effect = Exception("Down")
        self.assertFalse(OllamaBackend().is_available())

if __name__ == "__main__":
    unittest.main()
