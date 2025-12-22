import unittest
import os
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from gortex.core.auth import GortexAuth, APIKeyInfo

class TestAuthRotation(unittest.TestCase):
    def setUp(self):
        GortexAuth._reset()
        # Mock env vars
        os.environ["GEMINI_API_KEY_1"] = "key1"
        os.environ["GEMINI_API_KEY_2"] = "key2"
        self.auth = GortexAuth()

    def test_key_cooldown_on_429(self):
        """429 에러 발생 시 키가 쿨다운 상태로 전환되는지 테스트"""
        key_info = self.auth.key_pool[0]
        
        # 1. 429 에러 발생 보고
        self.auth.report_key_failure(key_info, is_quota_error=True)
        
        # 2. 상태 확인
        self.assertEqual(key_info.status, "cooldown")
        self.assertTrue(key_info.cooldown_until > datetime.now())
        
        # 3. 다음 가용 키 요청 시 2번 키가 나와야 함
        next_key = self.auth._get_available_gemini_key()
        self.assertEqual(next_key.key, "key2")

    def test_cooldown_expiration(self):
        """쿨다운 시간이 지나면 키가 다시 활성화되는지 테스트"""
        key_info = self.auth.key_pool[0]
        key_info.status = "cooldown"
        # 과거 시간으로 설정
        key_info.cooldown_until = datetime.now() - timedelta(minutes=1)
        
        available = self.auth._get_available_gemini_key()
        self.assertEqual(available.key, "key1")
        self.assertEqual(available.status, "alive")

    @patch("google.genai.Client")
    def test_fallback_to_openai(self, mock_client_cls):
        """Gemini 키가 모두 소진되었을 때 OpenAI로 폴백하는지 테스트"""
        # 모든 키를 쿨다운으로 설정
        for k in self.auth.key_pool:
            k.status = "cooldown"
            k.cooldown_until = datetime.now() + timedelta(hours=1)
            
        # OpenAI 클라이언트 모킹
        self.auth.openai_client = MagicMock()
        mock_res = MagicMock()
        mock_res.choices[0].message.content = "OpenAI Response"
        self.auth.openai_client.chat.completions.create.return_value = mock_res
        
        # Generate 호출
        res = self.auth.generate("gemini-1.5-flash", "hello")
        
        self.assertEqual(res.text, "OpenAI Response")
        self.assertEqual(self.auth.get_provider(), "OPENAI")

if __name__ == '__main__':
    unittest.main()
