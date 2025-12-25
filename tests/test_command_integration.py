
import unittest
import asyncio
from unittest.mock import MagicMock
from gortex.core.commands import handle_command
from gortex.core.observer import GortexObserver

class MockUI:
    def __init__(self):
        self.chat_history = []
        self.layout = MagicMock()
        
    def update_main(self, history):
        self.chat_history = history

class TestCommandIntegration(unittest.TestCase):
    def setUp(self):
        self.ui = MockUI()
        self.observer = MagicMock(spec=GortexObserver)
        self.cache = {}
        self.thread_id = "test_thread"
        
    def test_help_command(self):
        """/help 명령어가 chat_history에 도움말을 추가하는지 검증"""
        asyncio.run(handle_command("/help", self.ui, self.observer, self.cache, self.thread_id, None))
        
        self.assertTrue(len(self.ui.chat_history) > 0)
        last_msg = self.ui.chat_history[-1]
        self.assertEqual(last_msg[0], "system")
        # Panel 객체이므로 문자열 포함 여부 등은 복잡할 수 있음. 타입 확인.
        from rich.panel import Panel
        self.assertIsInstance(last_msg[1], Panel)
        print("✅ /help command logic verified.")

    def test_unknown_command(self):
        """알 수 없는 명령어 처리 검증"""
        asyncio.run(handle_command("/unknown_cmd_xyz", self.ui, self.observer, self.cache, self.thread_id, None))
        
        last_msg = self.ui.chat_history[-1]
        self.assertIn("알 수 없는 명령어", str(last_msg[1]))
        print("✅ Unknown command logic verified.")

if __name__ == '__main__':
    unittest.main()
