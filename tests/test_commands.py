import unittest
import asyncio
import os
import json
from unittest.mock import MagicMock, patch, mock_open
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

    def test_mode_command(self):
        """/mode [mode_name] 명령어 테스트"""
        res = self.run_async(handle_command("/mode coding", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.ui.set_mode.assert_called_with("coding")
        self.assertIn("모드로 전환", self.ui.chat_history[-1][1])

    def test_theme_command(self):
        """/theme 명령어 테스트"""
        res = self.run_async(handle_command("/theme dark", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.theme.apply_theme.assert_called_with("dark")

    @patch("gortex.core.commands.SynapticIndexer")
    def test_search_command_with_results(self, mock_indexer_cls):
        """/search 명령어가 결과를 정상 표시하는지 확인"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.search.return_value = [
            {"name": "core.commands.handle_command", "file": "core/commands.py", "line": 20},
        ]
        res = self.run_async(handle_command("/search handle", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        last_entry = self.ui.chat_history[-1][1]
        self.assertEqual(last_entry.title, "🔍 Search Results")
        mock_indexer.search.assert_called()

    @patch("gortex.core.commands.SynapticIndexer")
    def test_map_command_triggers_scan(self, mock_indexer_cls):
        """/map 명령어가 인덱스 스캔 및 트리를 생성하는지 확인"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.index_path = "fake_index.json"
        mock_indexer.generate_map.return_value = {
            "nodes": {
                "core.commands": {
                    "file": "core/commands.py",
                    "classes": ["GortexCommands"],
                    "functions": ["handle_command"],
                }
            }
        }
        with patch("os.path.exists", return_value=False):
            res = self.run_async(handle_command("/map", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertTrue(mock_indexer.scan_project.called)
        tree_obj = self.ui.chat_history[-1][1]
        self.assertIn("Gortex Project Map", str(tree_obj.label))

    def test_help_command(self):
        """/help 명령어가 HELP CENTER 패널을 표시하는지 확인"""
        res = self.run_async(handle_command("/help", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        self.assertEqual(self.ui.chat_history[-1][1].title, "HELP CENTER")

    def test_status_command(self):
        """/status 명령어가 OBS stats를 렌더링"""
        self.observer.get_stats.return_value = {"total_tokens": 10, "total_cost": 0.05, "uptime": "5m"}
        res = self.run_async(handle_command("/status", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        self.assertEqual(self.ui.chat_history[-1][1].title, "STATUS")

    def test_rca_command_without_id(self):
        """/rca 명령어에 ID 누락 시 메시지"""
        res = self.run_async(handle_command("/rca", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("사용법", self.ui.chat_history[-1][1])

    def test_rca_command_with_chain(self):
        """/rca 명령어에 체인이 있을 때 트리 생성"""
        self.observer.get_causal_chain.return_value = [
            {"agent": "coder", "event": "execute", "id": "E1"},
            {"agent": "tester", "event": "verify", "id": "E2"},
        ]
        res = self.run_async(handle_command("/rca E1", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(self.ui.chat_history[-1][1].__class__.__name__, "Tree")

    def test_bug_command(self):
        """/bug 명령어 테스트"""
        res = self.run_async(handle_command("/bug", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("이슈 리포트", self.ui.chat_history[-1][1])

if __name__ == '__main__':
    unittest.main()
