import unittest
import asyncio
from unittest.mock import MagicMock, patch
from gortex.core.commands import handle_command

class TestGortexCommands(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        self.ui.chat_history = []
        self.observer = MagicMock()
        self.cache = {}
        self.thread_id = "test_thread"
        self.theme = MagicMock()

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_help_command(self):
        """/help 명령어가 도움말 패널을 출력하는지 테스트"""
        res = self.run_async(handle_command("/help", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        # 패널이나 마크다운이 추가되었는지 확인
        self.assertTrue(any(msg[0] == "system" for msg in self.ui.chat_history))

    def test_status_command(self):
        """/status 명령어가 성능 리포트를 출력하는지 테스트"""
        self.observer.get_stats.return_value = {"total_tokens": 100, "total_cost": 0.1, "uptime": "1h"}
        res = self.run_async(handle_command("/status", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        self.ui.update_main.assert_called()

    def test_clear_command(self):
        """/clear 명령어가 대화 이력을 비우는지 테스트"""
        self.ui.chat_history = [("user", "hi")]
        res = self.run_async(handle_command("/clear", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(self.ui.chat_history, [])
        self.ui.update_main.assert_called_with([])

    def test_unknown_command(self):
        """알 수 없는 명령어에 대한 에러 메시지 테스트"""
        res = self.run_async(handle_command("/unknown", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        self.assertIn("알 수 없는 명령어", self.ui.chat_history[-1][1])

if __name__ == '__main__':
    unittest.main()
