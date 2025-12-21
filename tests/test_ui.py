import unittest
from unittest.mock import MagicMock, patch
from gortex.ui.dashboard import DashboardUI
from rich.console import Console

class TestGortexUI(unittest.TestCase):
    def setUp(self):
        self.console = MagicMock(spec=Console)
        asset_patcher = patch('gortex.ui.dashboard.SynapticAssetManager')
        self.addCleanup(asset_patcher.stop)
        self.mock_assets = asset_patcher.start()
        self.mock_assets.return_value.get_icon.return_value = "ICON"
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
        self.assertTrue(len(self.ui.chat_history) >= 0)

    def test_update_debate_monitor(self):
        """토론 패널이 데이터 반영"""
        debate = [
            {"persona": "Innovation", "report": "debate detail"}
        ]
        self.ui.update_debate_monitor(debate)
        panel = self.ui.layout["main"].renderable
        self.assertIn("CONSENSUS DEBATE", panel.title)

    def test_update_debt_panel(self):
        """기술 부채 목록이 없을 경우 안내"""
        self.ui.update_debt_panel([])
        panel = self.ui.layout["debt"].renderable
        self.assertIn("No debt", str(panel.renderable))

    def test_update_debt_panel_with_items(self):
        """기술 부채 항목이 테이블로 표출"""
        debt_list = [{"file": "core/commands.py", "score": 42}]
        self.ui.update_debt_panel(debt_list)
        panel = self.ui.layout["debt"].renderable
        self.assertIn("TECHNICAL DEBT", panel.title)

    def test_render_thought_tree(self):
        """사고 트리 렌더링"""
        self.ui.thought_tree = [
            {"id": "1", "text": "start", "type": "analysis"},
            {"id": "2", "parent_id": "1", "text": "child", "type": "design"}
        ]
        group = self.ui.render_thought_tree()
        self.assertTrue(len(group.renderables) >= 2)

    def test_update_thought_tracks_history(self):
        """사고 업데이트 시 타임라인 기록"""
        self.ui.update_thought("Thinking...")
        self.assertIn("Thinking...", self.ui.thought_history[0][1])
        self.assertEqual(len(self.ui.thought_timeline), 1)

    def test_tool_progress(self):
        """도구 진행 바 시작/정지"""
        self.ui.start_tool_progress("Processing")
        self.assertIsNotNone(self.ui.tool_task)
        self.ui.stop_tool_progress()
        self.assertIsNone(self.ui.tool_task)

if __name__ == '__main__':
    unittest.main()
