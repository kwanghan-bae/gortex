import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from rich.panel import Panel
from rich.console import Console
from gortex.ui.dashboard import DashboardUI

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
        main_panel = self.ui.layout["main"].renderable
        self.assertEqual(main_panel.title, "[bold cyan]🧠 GORTEX TERMINAL[/bold cyan]")

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

    def test_update_sidebar_updates_layout(self):
        """사이드바 정보가 상태/통계 패널을 갱신"""
        style = SimpleNamespace(color=SimpleNamespace(name="magenta"))
        self.console.get_style.return_value = style
        self.ui.update_sidebar(
            agent="coder",
            step="deploy",
            tokens=123,
            cost=0.123456,
            rules=1,
            provider="GEMINI",
            call_count=5,
            avg_latency=100,
            energy=80,
            efficiency=90.5,
            knowledge_lineage=[{"source": "log", "score": 0.8}],
            suggested_actions=[{"label": "Next"}]
        )
        self.assertEqual(self.ui.current_agent, "coder")
        self.assertEqual(self.ui.tokens_used, 123)
        status_panel = self.ui.layout["status"].renderable
        self.assertIn("SYSTEM STATUS", status_panel.title)
        stats_panel = self.ui.layout["stats"].renderable
        self.assertIn("USAGE STATS", stats_panel.title)

    def test_update_main_detects_json_and_table(self):
        """툴 메시지 JSON 및 테이블 감지를 모두 처리"""
        tool_msg = '{"status": "ok"}'
        table_msg = "| Name | Value |\n|---|---|\n| A | 1 |"
        self.ui.update_main([("tool", tool_msg), ("tool", table_msg)])
        main_panel = self.ui.layout["main"].renderable
        self.assertEqual(main_panel.title, "[bold cyan]🧠 GORTEX TERMINAL[/bold cyan]")
        group = main_panel.renderable
        json_panels = [
            item for item in group.renderables
            if isinstance(item, Panel)
            and ("OBSERVATION (JSON)" in str(item.title) or "OBSERVATION (PYTHON)" in str(item.title))
        ]
        table_panels = [
            item for item in group.renderables
            if isinstance(item, Panel) and "OBSERVATION (TABLE)" in str(item.title)
        ]
        self.assertTrue(json_panels)
        self.assertTrue(table_panels)

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

    def test_update_logs_panel_title(self):
        """로그 패널 타이틀 확인"""
        log = {"agent": "Planner", "event": "start"}
        self.ui.update_logs(log)
        panel = self.ui.layout["logs"].renderable
        self.assertIn("TRACE LOGS", panel.title)

    def test_tool_progress(self):
        """도구 진행 바 시작/정지"""
        self.ui.start_tool_progress("Processing")
        self.assertIsNotNone(self.ui.tool_task)
        self.ui.stop_tool_progress()
        self.assertIsNone(self.ui.tool_task)

if __name__ == '__main__':
    unittest.main()
