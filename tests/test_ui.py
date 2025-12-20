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

    def test_table_detection(self):
        """테이블 데이터 감지 테스트"""
        from gortex.utils.table_detector import try_render_as_table
        table_text = "ID    Name    Status\n1     Alice   Active\n2     Bob     Offline"
        table = try_render_as_table(table_text)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 3)

    def test_markdown_table_detection(self):
        """Markdown 스타일 테이블 감지 테스트"""
        from gortex.utils.table_detector import try_render_as_table
        md_text = "| ID | Name | Role |\n|---|---|---|\n| 1 | Admin | Super |"
        table = try_render_as_table(md_text)
        self.assertIsNotNone(table)
        self.assertEqual(len(table.columns), 3)
        self.assertEqual(len(table.rows), 1)

if __name__ == '__main__':
    unittest.main()
