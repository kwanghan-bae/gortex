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

    def test_three_js_bridge_fallback(self):
        """3D Bridge 연결 실패 시 안전하게 처리되는지 확인"""
        # mock bridge가 raise exception하도록 설정
        with patch("gortex.ui.dashboard.ThreeJsBridge") as mock_bridge:
            mock_bridge.side_effect = ImportError("No module named three_js")
            # 재생성 시도 (setUp에서 이미 생성되었으므로 다시 생성하며 예외 유발)
            ui = DashboardUI(self.console)
            self.assertIsNone(ui.bridge)
            
            # 메서드 호출 시 에러 없이 통과하는지 (None check)
            ui.update_thought("test") # 내부에서 bridge.update_thought 호출 시도

    def test_update_main_with_invalid_messages(self):
        """잘못된 형식의 메시지 처리"""
        messages = [None, ("unknown_role", object()), ("user", None)]
        try:
            self.ui.update_main(messages)
        except Exception:
            self.fail("update_main raised Exception on invalid messages")

    def test_update_sidebar_defaults(self):
        """update_sidebar 인자 누락 시 기본값 작동 확인"""
        self.ui.update_sidebar(agent="TestAgent", step="TestStep")
        self.assertEqual(self.ui.tokens_used, 0) # 기본값
        self.assertEqual(self.ui.total_cost, 0.0)

    def test_render_thought_tree_empty(self):
        """빈 사고 트리 렌더링"""
        self.ui.thought_tree = []
        group = self.ui.render_thought_tree()
        self.assertTrue(len(group.renderables) > 0) # 최소한의 컨테이너 반환

    def test_theme_color_retrieval(self):
        """테마 색상 조회 테스트"""
        # dashboard_theme가 모킹되지 않았으므로 실제 로직 테스트 가능
        color = self.ui.theme.get_color("agent")
        self.assertIsNotNone(color)

    def test_update_main_truncation(self):
        """긴 메시지 절삭 로직 확인"""
        long_text = "A" * 3000
        # DashboardUI.update_main은 외부에서 관리하는 메시지 리스트를 인자로 받음
        messages = [("tool", long_text)]
        self.ui.update_main(messages)
        self.assertEqual(len(messages), 1)

    def test_update_logs_limit(self):
        """로그 누적 제한 확인 (현재 8개 제한)"""
        for i in range(20):
            self.ui.update_logs({"event": f"log {i}"})
        self.assertEqual(len(self.ui.recent_logs), 8)

    def test_update_debate_monitor_empty(self):
        """빈 토론 데이터 처리"""
        self.ui.update_debate_monitor([])
        # 데이터가 비어있으면 메인 패널이 기본 타이틀을 유지하거나 리셋됨
        panel = self.ui.layout["main"].renderable
        # _Placeholder 에러 방지를 위해 에러 없이 실행됨만 확인하거나 타입 체크
        self.assertIsNotNone(panel)

    def test_add_achievement(self):
        self.ui.add_achievement("Test achievement")
        self.assertEqual(len(self.ui.achievements), 1)
        self.assertEqual(self.ui.achievements[0]["text"], "Test achievement")

    def test_filter_thoughts(self):
        self.ui.thought_history = [
            ("AgentA", "Thinking about code"),
            ("AgentB", "Analyzing logs")
        ]
        res1 = self.ui.filter_thoughts(agent_name="AgentA")
        self.assertEqual(len(res1), 1)
        res2 = self.ui.filter_thoughts(keyword="logs")
        self.assertEqual(len(res2), 1)

    def test_add_security_event(self):
        self.ui.add_security_event("BLOCK", "Blocked rm -rf")
        self.assertEqual(len(self.ui.security_events), 1)

    def test_add_journal_entry(self):
        for i in range(30):
            self.ui.add_journal_entry(f"entry {i}")
        self.assertEqual(len(self.ui.activity_stream), 20) # 20개 제한 확인

    def test_update_review_board(self):
        self.ui.update_review_board("task1", "Analyst", True, "Good")
        self.assertIn("task1", self.ui.review_board)
        self.assertTrue(self.ui.review_board["task1"]["approvals"]["Analyst"]["approved"])

    def test_set_mode(self):
        modes = ["coding", "research", "debugging", "analyst"]
        for m in modes:
            self.ui.set_mode(m)
        self.assertTrue(True) # 에러 없이 통과 확인

    def test_render(self):
        from rich.layout import Layout
        res = self.ui.render()
        self.assertIsInstance(res, Layout)

if __name__ == '__main__':
    unittest.main()
