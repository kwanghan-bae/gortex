
import unittest
from gortex.core.middleware import HealingMiddleware

class TestHealingMiddleware(unittest.TestCase):
    def setUp(self):
        self.middleware = HealingMiddleware(max_retries=2)
        
    def test_process_success(self):
        """정상 Output은 그대로 통과"""
        output = {"status": "success", "result": "ok"}
        state = {"retry_count": 0}
        
        # 정상 케이스는 state를 변경하지 않음
        processed = self.middleware.process_response(output, state)
        self.assertEqual(processed, output)
        self.assertEqual(state.get("next_node"), None)

    def test_detect_failure_and_route_to_healing(self):
        """실패 감지 시 Healing 노드로 라우팅 변경"""
        output = {"status": "failed", "error": "SyntaxError"}
        state = {"retry_count": 0}
        
        self.middleware.process_response(output, state)
        
        self.assertEqual(state["next_node"], "healer")
        self.assertEqual(state["retry_count"], 1)
        self.assertIn("error_context", state)

    def test_max_retries_exceeded(self):
        """최대 재시도 초과 시 포기"""
        output = {"status": "failed", "error": "PersistentError"}
        state = {"retry_count": 2} # 이미 2번 시도함
        
        self.middleware.process_response(output, state)
        
        # 재시도하지 않고 에러 전파 (또는 종료)
        self.assertNotEqual(state.get("next_node"), "healer")
        # Retry count는 증가하지 않아야 함 (이미 Max 도달)
        self.assertEqual(state["retry_count"], 2)

if __name__ == '__main__':
    unittest.main()
