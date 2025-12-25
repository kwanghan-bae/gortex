import unittest
from unittest.mock import patch, MagicMock
import os
from gortex.core.auth import GortexAuth, APIKeyInfo

class TestAuthResilience(unittest.TestCase):
    """
    인증 시스템의 복원력(Resilience)과 폴백(Fallback) 로직을 검증하는 테스트.
    API 키가 없거나 모델이 없을 때의 동작을 시뮬레이션한다.
    """

    def setUp(self):
        # 싱글톤 초기화 (매 테스트마다 리셋)
        if hasattr(GortexAuth, "_instance"):
            GortexAuth._instance = None
        
        # 환경 변수 백업 및 클리어
        self.env_patcher = patch.dict(os.environ, {}, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    def test_init_without_keys(self):
        """Gemini Key가 하나도 없을 때도 에러 없이 초기화되어야 하며, Ollama 모드로 전환되어야 한다."""
        auth = GortexAuth()
        self.assertEqual(len(auth.key_pool), 0)
        self.assertEqual(auth._provider, "ollama", "키가 없으면 Provider는 'ollama'여야 한다.")

    @patch('gortex.core.auth.requests.get')
    @patch('gortex.core.auth.requests.post')
    def test_ollama_fallback_logic(self, mock_post, mock_get):
        """Gemini 호출 실패 시 Ollama로 넘어가는지 검증"""
        # Mock requests
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "qwen2.5:7b"}]}
        
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Ollama Response"}}

        auth = GortexAuth()
        # 강제로 Gemini 키가 있는 것처럼 속임 (하지만 Dead 상태)
        auth.key_pool = [APIKeyInfo(key="fake_key", client=MagicMock(), status="dead")]
        
        # Generate 호출 -> Gemini Dead -> Ollama 호출 기대
        response = auth.generate("gemini-1.5-flash", "Hello")
        
        self.assertEqual(response.text, "Ollama Response")
        self.assertEqual(auth.get_provider(), "OLLAMA")

    @patch('builtins.input', return_value='y') # 사용자가 'y'를 입력했다고 가정
    @patch('subprocess.run')
    @patch('gortex.core.auth.requests.get')
    def test_auto_pull_trigger(self, mock_get, mock_subprocess, mock_input):
        """필요한 모델이 없을 때 사용자에게 묻고 pull 명령어를 실행하는지 검증"""
        
        # 1. 모델 목록 조회 시 원하는 모델이 없음
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "other-model"}]}
        
        auth = GortexAuth()
        
        # 2. _generate_ollama 내부 로직 테스트 (직접 호출이 어렵다면 generate를 통해 간접 호출)
        # 여기서는 auth._generate_ollama를 테스트하기 위해 필요한 의존성을 주입
        try:
            auth._generate_ollama("manager", "test", None) # manager -> granite3.1-moe:3b 요구
        except:
            # 실제 요청은 실패할 수 있음 (requests.post를 mock 안 했으므로)
            pass

        # 3. subprocess.run이 'ollama pull granite3.1-moe:3b'와 비슷한 인자로 호출되었는지 확인
        # role_map에 따라 manager의 첫 번째 후보는 granite3.1-moe:3b
        
        # NOTE: 실제 구현에서 subprocess.run이 호출되었는지 확인
        # arguments 중 'pull'이 포함되어 있는지 체크
        called = False
        for call in mock_subprocess.call_args_list:
            args = call[0][0] # 첫 번째 인자 (리스트)
            if "pull" in args and any("granite" in arg or "smollm" in arg for arg in args):
                called = True
                break
        
        self.assertTrue(called, "필요한 모델이 없을 때 'ollama pull' 명령어가 실행되어야 한다.")

if __name__ == "__main__":
    unittest.main()
