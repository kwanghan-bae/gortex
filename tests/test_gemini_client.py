import unittest
from unittest.mock import MagicMock, patch
from gortex.core.llm.gemini_client import GeminiBackend

class TestGeminiBackend(unittest.TestCase):
    @patch("gortex.core.llm.gemini_client.GortexAuth")
    def test_generate_delegation(self, mock_auth_cls):
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.text = "Gemini Response"
        mock_auth.generate.return_value = mock_response

        backend = GeminiBackend()
        response = backend.generate("gemini-pro", [{"role": "user", "content": "hi"}])
        self.assertEqual(response, "Gemini Response")

    @patch("gortex.core.llm.gemini_client.GortexAuth")
    def test_generate_with_config(self, mock_auth_cls):
        mock_auth = mock_auth_cls.return_value
        backend = GeminiBackend()
        config = {"temperature": 0.5, "max_tokens": 100}
        
        backend.generate("model", [], config)
        args, _ = mock_auth.generate.call_args
        gen_config = args[2]
        self.assertEqual(gen_config.temperature, 0.5)

    @patch("gortex.core.llm.gemini_client.GortexAuth")
    def test_generate_exception(self, mock_auth_cls):
        mock_auth = mock_auth_cls.return_value
        mock_auth.generate.side_effect = Exception("API Fail")
        backend = GeminiBackend()
        with self.assertRaises(Exception):
            backend.generate("model", [])

if __name__ == "__main__":
    unittest.main()
