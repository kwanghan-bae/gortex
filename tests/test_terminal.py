import unittest
from unittest.mock import MagicMock
from gortex.ui.terminal import TerminalHandler

class TestTerminalHandler(unittest.TestCase):
    def setUp(self):
        self.mock_ui = MagicMock()
        self.mock_ui.chat_history = []
        self.terminal = TerminalHandler(self.mock_ui)

    def test_update_status(self):
        self.terminal.update_status("Coder", "Writing code", extra="info")
        self.mock_ui.update_sidebar.assert_called_with("Coder", "Writing code", extra="info")

    def test_display_message(self):
        self.terminal.display_message("user", "Hello")
        
        # chat_history에 추가되었는지 확인
        self.assertEqual(len(self.mock_ui.chat_history), 1)
        self.assertEqual(self.mock_ui.chat_history[0], ("user", "Hello"))
        
        # update_main 호출 확인
        self.mock_ui.update_main.assert_called_with(self.mock_ui.chat_history)

if __name__ == "__main__":
    unittest.main()
