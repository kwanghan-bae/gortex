import unittest
import json
from unittest.mock import patch
from gortex.core.llm.factory import HybridBackend
from gortex.utils.tools import repair_and_load_json

class TestHybridLLM(unittest.TestCase):
    def test_json_repair(self):
        """비정형 JSON 복구 테스트"""
        malformed = "Here is the result: ```json\n{'key': 'value', 'missing': 'brace' \n```"
        repaired = repair_and_load_json(malformed)
        self.assertEqual(repaired["key"], "value")
        self.assertIn("missing", repaired)

    @patch("gortex.core.llm.ollama_client.requests.get")
    @patch("gortex.core.llm.ollama_client.requests.post")
    @patch("gortex.core.llm.gemini_client.GeminiBackend.generate")
    def test_hybrid_fallback(self, mock_gemini, mock_ollama_post, mock_ollama_get):
        """Gemini 실패 시 Ollama 폴백 테스트"""
        # 1. Gemini 에러 설정
        mock_gemini.side_effect = Exception("Quota Exceeded")
        
        # 2. Ollama 정상 응답 설정
        mock_ollama_get.return_value.status_code = 200
        mock_ollama_post.return_value.status_code = 200
        mock_ollama_post.return_value.json.return_value = {
            "message": {"content": '{"status": "ok"}'}
        }
        
        backend = HybridBackend()
        result = backend.generate("any-model", [{"role": "user", "content": "hi"}])
        
        self.assertEqual(json.loads(result)["status"], "ok")
        mock_gemini.assert_called_once()
        mock_ollama_post.assert_called_once()

if __name__ == '__main__':
    unittest.main()
