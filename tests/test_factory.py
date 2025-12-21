import unittest
import os
from unittest.mock import patch
from gortex.core.llm.factory import LLMFactory
from gortex.core.llm.gemini_client import GeminiBackend
from gortex.core.llm.ollama_client import OllamaBackend

class TestLLMFactory(unittest.TestCase):
    def setUp(self):
        LLMFactory._instances = {}

    @patch.dict(os.environ, {"LLM_BACKEND": "gemini"})
    def test_get_default_backend_gemini(self):
        backend = LLMFactory.get_default_backend()
        self.assertIsInstance(backend, GeminiBackend)

    @patch.dict(os.environ, {"LLM_BACKEND": "ollama"})
    def test_get_default_backend_ollama(self):
        backend = LLMFactory.get_default_backend()
        self.assertIsInstance(backend, OllamaBackend)

if __name__ == "__main__":
    unittest.main()
