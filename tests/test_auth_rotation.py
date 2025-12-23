import unittest
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from gortex.core.auth import GortexAuth, APIKeyInfo

class TestAuthRotation(unittest.TestCase):
    def setUp(self):
        # 싱글톤 인스턴스 초기화
        GortexAuth._reset()
        self.auth = GortexAuth()
        
        # 테스트용 더미 키 풀 구성 (실제 API 호출 방지)
        self.auth.key_pool = [
            APIKeyInfo(key="KEY_1", client=MagicMock()),
            APIKeyInfo(key="KEY_2", client=MagicMock()),
            APIKeyInfo(key="KEY_3", client=MagicMock())
        ]

    def test_quota_error_triggers_cooldown(self):
        """할당량 초과 시 기하급수적 쿨다운 적용 테스트"""
        key_info = self.auth.key_pool[0]
        
        # 1. Quota 에러 보고 (첫 번째 실패)
        self.auth.report_key_failure(key_info, "429: Resource exhausted")
        
        self.assertEqual(key_info.status, "cooldown")
        # 2^1 = 2분 이상 쿨다운 설정 확인
        self.assertGreaterEqual(key_info.cooldown_until, datetime.now() + timedelta(seconds=110))

    def test_key_rotation_on_failure(self):
        """키 실패 시 다음 건강한 키로의 로테이션 테스트"""
        # 첫 번째 키를 Cooldown 상태로 강제 전환
        self.auth.key_pool[0].status = "cooldown"
        self.auth.key_pool[0].cooldown_until = datetime.now() + timedelta(minutes=10)
        
        # 가용한 키 조회 시 두 번째 키가 반환되어야 함
        available_key = self.auth._get_available_gemini_key()
        self.assertEqual(available_key.key, "KEY_2")

    def test_success_resets_status(self):
        """성공 보고 시 쿨다운 해제 및 카운트 리셋 테스트"""
        key_info = self.auth.key_pool[0]
        key_info.status = "cooldown"
        key_info.failure_count = 5
        
        self.auth.report_key_success(key_info)
        
        self.assertEqual(key_info.status, "alive")
        self.assertEqual(key_info.failure_count, 0)
        self.assertEqual(key_info.success_count, 1)

    def test_get_pool_status_format(self):
        """UI용 풀 상태 데이터 형식 검증"""
        self.auth.key_pool[0].status = "cooldown"
        self.auth.key_pool[0].cooldown_until = datetime.now() + timedelta(seconds=30)
        
        status = self.auth.get_pool_status()
        
        self.assertEqual(len(status), 3)
        self.assertEqual(status[0]["status"], "cooldown")
        self.assertGreater(status[0]["cooldown"], 0)
        self.assertIn("KEY_1", status[0]["key_hint"])

if __name__ == '__main__':
    unittest.main()