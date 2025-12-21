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

    def test_mode_command_missing(self):
        """/mode 명령어 인자 누락 시 경고"""
        res = self.run_async(handle_command("/mode", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("사용 가능한 모드", self.ui.chat_history[-1][1])

    def test_clear_command(self):
        """/clear 명령어가 채팅을 초기화"""
        self.ui.chat_history.append(("user", "Hello"))
        res = self.run_async(handle_command("/clear", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(len(self.ui.chat_history), 0)

    def test_bug_command(self):
        """/bug 명령어 테스트"""
        res = self.run_async(handle_command("/bug", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("이슈 리포트", self.ui.chat_history[-1][1])

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

    @patch("gortex.core.commands.SynapticIndexer")
    def test_kg_command_generates_graph(self, mock_indexer_cls):
        """/kg 명령어가 지식 그래프를 생성하고 UI에 요약을 추가"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.generate_knowledge_graph.return_value = {"nodes": {"n": {}}, "edges": []}
        res = self.run_async(handle_command("/kg", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(res, "skip")
        summary_panel = self.ui.chat_history[-1][1]
        self.assertEqual(summary_panel.title, "BRAIN MAP")
        mock_indexer.generate_knowledge_graph.assert_called()

    @patch("gortex.utils.translator.i18n")
    def test_language_command(self, mock_i18n):
        """/language 명령어가 언어를 전환"""
        res = self.run_async(handle_command("/language en", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(mock_i18n.current_lang, "en")
        self.assertEqual(self.ui.target_language, "en")
        self.assertIn("언어가 'en'", self.ui.chat_history[-1][1])

    def test_export_command(self):
        """/export 명령어가 파일을 생성하고 알림"""
        with patch("builtins.open", mock_open()) as mock_file:
            res = self.run_async(handle_command("/export", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("Exported", self.ui.chat_history[-1][1])
            mock_file.assert_called()

    def test_save_command(self):
        """/save 명령어가 세션 상태를 파일로 저장"""
        with patch("builtins.open", mock_open()) as mock_file:
            res = self.run_async(handle_command("/save", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("저장", self.ui.chat_history[-1][1])
            mock_file.assert_called()

    def test_load_command(self):
        """/load 명령어가 파일이 존재할 때 복원"""
        sample = '{"thread_id": "test_thread"}'
        with patch("builtins.open", mock_open(read_data=sample)) as mock_file, patch("os.path.exists", return_value=True):
            res = self.run_async(handle_command("/load", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("복원", self.ui.chat_history[-1][1])
            self.assertEqual(self.cache[self.thread_id], {"thread_id": "test_thread"})

    def test_rca_command_missing_chain(self):
        """/rca 명령어가 체인을 찾지 못했을 때 메시지"""
        self.observer.get_causal_chain.return_value = []
        res = self.run_async(handle_command("/rca missing", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("계보", self.ui.chat_history[-1][1])

    @patch("gortex.core.commands.SynapticIndexer")
    def test_search_command_no_results(self, mock_indexer_cls):
        """/search 명령어가 결과 없음 상태를 처리"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.search.return_value = []
        res = self.run_async(handle_command("/search nothing", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("검색 결과가 없습니다", self.ui.chat_history[-1][1])

    def test_unknown_command(self):
        """알 수 없는 명령어에 대해 에러 안내"""
        res = self.run_async(handle_command("/unknown", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("알 수 없는 명령어", self.ui.chat_history[-1][1])

if __name__ == '__main__':
    unittest.main()
