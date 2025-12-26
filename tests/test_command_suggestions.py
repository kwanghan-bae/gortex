import unittest
from unittest.mock import MagicMock
from gortex.core.commands import handle_command

class TestCommandSuggestions(unittest.IsolatedAsyncioTestCase):
    async def test_command_suggestion_status(self):
        """/staus 오타 시 /status를 추천하는지 테스트"""
        ui = MagicMock()
        ui.chat_history = []
        observer = MagicMock()
        
        await handle_command("/staus", ui, observer, {}, "test_thread", None)
        
        # chat_history에 추가된 메시지 확인
        last_msg = ui.chat_history[-1][1]
        self.assertIn("/status", last_msg)
        self.assertIn("혹시", last_msg)

    async def test_command_suggestion_help(self):
        """/hlp 오타 시 /help를 추천하는지 테스트"""
        ui = MagicMock()
        ui.chat_history = []
        observer = MagicMock()
        
        await handle_command("/hlp", ui, observer, {}, "test_thread", None)
        
        last_msg = ui.chat_history[-1][1]
        self.assertIn("/help", last_msg)

if __name__ == "__main__":
    unittest.main()
