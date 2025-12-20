import unittest
from unittest.mock import MagicMock, patch
import time
from gortex.core.auth import GortexAuth

class TestGortexAuth(unittest.TestCase):
    def setUp(self):
        # 싱글톤 인스턴스 초기화
        GortexAuth._reset()
        # 환경 변수 Mocking
        self.env_patcher = patch('os.getenv')

        self.mock_getenv = self.env_patcher.start()
        # 기본적으로 두 개의 키가 있다고 가정
        self.mock_getenv.side_effect = lambda k: "fake_key_1" if k == "GEMINI_API_KEY_1" else ("fake_key_2" if k == "GEMINI_API_KEY_2" else None)
        
        # google.genai.Client 생성자 Mocking
        self.client_patcher = patch('google.genai.Client')
        self.mock_client_cls = self.client_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        self.client_patcher.stop()

    def test_init(self):
        """초기화 시 클라이언트가 올바르게 생성되는지 테스트"""
        auth = GortexAuth()
        self.assertEqual(len(auth.clients), 2)
        self.assertEqual(auth.current_index, 0)

    @patch('time.sleep')
    def test_rotation_on_429(self, mock_sleep):
        """429 에러 발생 시 로테이션 및 재시도 로직 테스트"""
        auth = GortexAuth()
        
        # Mock Client 인스턴스 설정
        mock_client_1 = MagicMock()
        mock_client_2 = MagicMock()
        auth.clients = [mock_client_1, mock_client_2]
        
        # 첫 번째 클라이언트는 429 에러 발생, 두 번째는 성공 설정
        # google-genai는 예외를 발생시킴
        mock_client_1.models.generate_content.side_effect = Exception("429 ResourceExhausted")
        mock_client_2.models.generate_content.return_value = "Success"
        
        # 실행
        result = auth.generate("model", "content")
        
        # 검증
        self.assertEqual(result, "Success")
        self.assertEqual(auth.current_index, 1) # 인덱스가 변경되었는지 확인
        mock_client_1.models.generate_content.assert_called_once()
        mock_client_2.models.generate_content.assert_called_once()
        
        # Jitter (sleep) 호출 확인
        mock_sleep.assert_called()
        args, _ = mock_sleep.call_args
        sleep_time = args[0]
        self.assertTrue(5.5 <= sleep_time <= 12.0, f"Sleep time {sleep_time} is out of range")

    @patch('time.sleep')
    def test_server_error_503(self, mock_sleep):
        """503 에러 발생 시 재시도 로직 테스트"""
        auth = GortexAuth()
        mock_client = MagicMock()
        auth.clients = [mock_client]
        
        # 첫 번째는 503, 두 번째는 성공
        mock_client.models.generate_content.side_effect = [Exception("503 Service Unavailable"), "Success"]
        
        result = auth.generate("model", "content")
        
        self.assertEqual(result, "Success")
        # 3초 대기 확인
        mock_sleep.assert_called_with(3)

if __name__ == '__main__':
    unittest.main()
