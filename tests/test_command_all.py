
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from gortex.core.commands import handle_command
from gortex.core.observer import GortexObserver

class MockUI:
    def __init__(self):
        self.chat_history = []
        self.layout = MagicMock()
        self.target_language = "ko"
        self.memory_active = False # For /memory command toggle check
        
    def update_main(self, history):
        self.chat_history = history
        
    def toggle_memory_mode(self, query=None):
        self.memory_active = not self.memory_active
    
    def set_mode(self, mode):
        pass

class TestCommandAll(unittest.TestCase):
    def setUp(self):
        self.ui = MockUI()
        self.observer = MagicMock(spec=GortexObserver)
        self.observer.get_stats.return_value = {"total_tokens": 100, "total_cost": 0.01}
        self.cache = {}
        self.thread_id = "test_thread"
        self.theme_manager = MagicMock()

    async def _run_cmd(self, cmd_str):
        return await handle_command(cmd_str, self.ui, self.observer, self.cache, self.thread_id, self.theme_manager)

    def test_help_command(self):
        asyncio.run(self._run_cmd("/help"))
        # rich 객체는 string 변환이 안되므로 타입 체크로 대체
        from rich.markdown import Markdown
        renderable = self.ui.chat_history[-1][1].renderable
        self.assertIsInstance(renderable, Markdown)

    def test_status_command(self):
        # /status는 UI에 toggle_monitor_mode가 있는지 체크함. MockUI에는 없으므로 Fallback 로직 테스트
        asyncio.run(self._run_cmd("/status"))
        from rich.markdown import Markdown
        renderable = self.ui.chat_history[-1][1].renderable
        self.assertIsInstance(renderable, Markdown)

    def test_config_ui_signal(self):
        # /config는 "config_ui" 반환해야 함
        res = asyncio.run(self._run_cmd("/config"))
        self.assertEqual(res, "config_ui")

    def test_agents_list(self):
        # registry.list_agents 모킹 필요
        with patch('gortex.core.registry.registry.list_agents', return_value=["analyst", "coder"]), \
             patch('gortex.core.registry.registry.get_metadata') as mock_meta:
            mock_meta.return_value = MagicMock(role="tester", version="1.0", tools=[])
            asyncio.run(self._run_cmd("/agents"))
            
            # Table 객체 확인 (rich Table은 str 변환시 그대로 나오진 않으나 타입체크 가능)
            from rich.table import Table
            self.assertIsInstance(self.ui.chat_history[-1][1], Table)

    def test_search_command(self):
        # /search query
        # SynapticIndexer 모킹
        with patch('gortex.core.commands.SynapticIndexer') as MockIndexer:
            mock_inst = MockIndexer.return_value
            mock_inst.search.return_value = [{"name": "Foo", "file": "bar.py", "line": 10}]
            
            asyncio.run(self._run_cmd("/search test_query"))
            
            from rich.table import Table
            self.assertIsInstance(self.ui.chat_history[-1][1], Table)

    def test_memory_command(self):
        # /memory (toggle)
        asyncio.run(self._run_cmd("/memory"))
        self.assertTrue(self.ui.memory_active)
        
        asyncio.run(self._run_cmd("/memory"))
        self.assertFalse(self.ui.memory_active)

    def test_invalid_command_suggestion(self):
        # /helpp -> Did you mean /help?
        asyncio.run(self._run_cmd("/helpp"))
        msg = self.ui.chat_history[-1][1]
        self.assertIn("혹시", msg)
        self.assertIn("/help", msg)

if __name__ == '__main__':
    unittest.main()
