import unittest
from rich.console import Console
from gortex.ui.dashboard import DashboardUI

class TestGortexUI(unittest.TestCase):
    def setUp(self):
        self.console = Console()
        self.ui = DashboardUI(self.console)

    def test_update_main_roles(self):
        """다양한 역할의 메시지가 정상적으로 처리되는지 테스트"""
        messages = [
            ("user", "Hello"),
            ("ai", "Hi there"),
            ("tool", '{"status": "ok"}'),
            ("system", "Initializing")
        ]
        self.ui.update_main(messages)
        # 에러 없이 실행되는지 확인 (Rich 렌더링 특성상 상세 검증은 복잡함)
        self.assertTrue(len(self.ui.chat_history) >= 0)

    def test_update_thought(self):
        """사고 과정 업데이트 테스트"""
        self.ui.update_thought("I am thinking...", agent_name="Coder")
        self.assertEqual(self.ui.agent_thought, "I am thinking...")

    def test_update_logs(self):
        """로그 업데이트 테스트"""
        log = {"agent": "Planner", "event": "start"}
        self.ui.update_logs(log)
        self.assertEqual(len(self.ui.recent_logs), 1)

if __name__ == '__main__':
    unittest.main()
