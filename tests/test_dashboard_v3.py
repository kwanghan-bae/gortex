import unittest
from unittest.mock import patch, MagicMock
from gortex.ui.dashboard import DashboardUI, render_sparkline

class TestDashboardV3(unittest.TestCase):
    def setUp(self):
        self.mock_console = MagicMock()
        self.dashboard = DashboardUI(self.mock_console)

    def test_sparkline_render(self):
        data = [1.0, 2.0, 3.0]
        spark = render_sparkline(data)
        self.assertTrue(len(spark) > 0)

    def test_update_registry(self):
        from gortex.core.registry import AgentMetadata
        
        # 가상 에이전트 등록
        class MockBot:
            pass
        self.meta = AgentMetadata(
            name="MockBot",
            role="tester",
            description="test",
            tools=[],
            version="1.0"
        )
        # Mocking registry list_agents and get_metadata
        with patch("gortex.core.registry.registry.list_agents", return_value=["MockBot"]), \
             patch("gortex.core.registry.registry.get_metadata", return_value=self.meta):

            self.dashboard.update_registry_panel()
            # No assertion needed, just checking for crashes

    def test_update_impact(self):
        self.dashboard.update_impact_panel("foo", [{"file": "bar.py", "type": "call"}])
        # Check if panel updated (mock check)
        # self.assertTrue(self.dashboard.layout["impact"].renderable is not None)

if __name__ == "__main__":
    unittest.main()
