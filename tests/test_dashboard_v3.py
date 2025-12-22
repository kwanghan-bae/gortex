import unittest
from unittest.mock import MagicMock, patch
from rich.console import Console
from gortex.ui.dashboard import DashboardUI
from gortex.core.registry import registry, AgentMetadata
from gortex.core.commands import handle_command

class TestDashboardV3(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.console = Console()
        self.ui = DashboardUI(self.console)
        
        # 가상 에이전트 등록
        class MockBot: pass
        self.meta = AgentMetadata(
            name="MockBot",
            role="Testing",
            description="Unit test bot",
            tools=["jump", "run"],
            version="3.0.0"
        )
        registry.register("MockBot", MockBot, self.meta)

    def test_update_registry_panel(self):
        """레지스트리 패널 렌더링 테스트"""
        self.ui.update_registry_panel()
        # 레이아웃에 데이터가 반영되었는지 확인 (Rich Layout 특성상 렌더링 시도)
        renderable = self.ui.render()
        self.assertIsNotNone(renderable)

    async def test_agents_command(self):
        """/agents 명령어 실행 및 결과 표 생성 테스트"""
        observer = MagicMock()
        theme = MagicMock()
        
        # 명령어 처리
        await handle_command("/agents", self.ui, observer, {}, "thread_1", theme)
        
        # 채팅 히스토리에 Table 객체가 추가되었는지 확인
        last_msg = self.ui.chat_history[-1]
        self.assertEqual(last_msg[0], "system")
        from rich.table import Table
        self.assertIsInstance(last_msg[1], Table)
        self.assertEqual(last_msg[1].title, "🤖 Gortex Active Agents (v3.0)")

    def test_sidebar_capability_display(self):
        """사이드바에 에이전트 능력 표시 테스트"""
        self.ui.update_sidebar(agent="MockBot", capability="jump")
        # 내부 상태 업데이트 확인
        self.assertEqual(self.ui.current_capability, "jump")

if __name__ == '__main__':
    unittest.main()
