import unittest
import asyncio
from unittest.mock import patch, MagicMock, mock_open
from gortex.core.commands import handle_command
from gortex.ui.dashboard import DashboardUI
from gortex.core.observer import GortexObserver
from gortex.ui.dashboard_theme import ThemeManager
from gortex.core.auth import GortexAuth

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock(spec=DashboardUI)
        self.ui.chat_history = []
        self.observer = MagicMock(spec=GortexObserver)
        self.cache = {}
        self.thread_id = "test_thread"
        self.theme = MagicMock(spec=ThemeManager)
        self.theme.apply_theme = MagicMock()

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_mode_command(self):
        """/mode [mode_name] 명령어 테스트"""
        self.run_async(handle_command("/mode coding", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.ui.set_mode.assert_called_with("coding")
        self.assertIn("모드로 전환", self.ui.chat_history[-1][1])

    def test_theme_command(self):
        """/theme 명령어 테스트"""
        self.run_async(handle_command("/theme dark", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.theme.apply_theme.assert_called_with("dark")

    def test_mode_command_missing(self):
        """/mode 명령어 인자 누락 시 경고"""
        self.run_async(handle_command("/mode", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("사용 가능한 모드", self.ui.chat_history[-1][1])

    def test_clear_command(self):
        """/clear 명령어가 채팅을 초기화"""
        self.ui.chat_history.append(("user", "Hello"))
        self.run_async(handle_command("/clear", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(len(self.ui.chat_history), 0)

    def test_bug_command(self):
        """/bug 명령어 테스트"""
        self.run_async(handle_command("/bug", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("이슈 리포트", self.ui.chat_history[-1][1])

    @patch("gortex.core.commands.SynapticIndexer")
    def test_search_command(self, mock_indexer_cls):
        """/search 명령어 테스트"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.search.return_value = [
            {"name": "core.commands.handle_command", "file": "core/commands.py", "line": 20},
        ]
        self.run_async(handle_command("/search handle", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        last_entry = self.ui.chat_history[-1][1]
        from rich.table import Table
        self.assertIsInstance(last_entry, Table)
        self.assertEqual(last_entry.title, "🔍 Search Results")

    @patch("gortex.core.commands.SynapticIndexer")
    def test_map_command(self, mock_indexer_cls):
        """/map 명령어 테스트"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.generate_map.return_value = {
            "nodes": {"a": {"classes": [], "file": "a.py", "functions": []}}, "edges": []
        }
        with patch("os.path.exists", return_value=False):
            self.run_async(handle_command("/map", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        # Depending on implementation, if it instantiates and calls scan_project
        self.assertTrue(mock_indexer.scan_project.called)

    @patch("gortex.utils.translator.i18n")
    def test_language_command(self, mock_i18n):
        """/language 명령어가 언어를 전환"""
        self.run_async(handle_command("/language en", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(mock_i18n.current_lang, "en")
        self.assertEqual(self.ui.target_language, "en")

    def test_export_command(self):
        """/export 명령어가 파일을 생성하고 알림"""
        with patch("builtins.open", mock_open()) as m_open:
            self.run_async(handle_command("/export", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("Exported", self.ui.chat_history[-1][1])
            m_open.assert_called()

    def test_save_command(self):
        """/save 명령어가 세션 상태를 파일로 저장"""
        with patch("builtins.open", mock_open()) as m_open:
            self.run_async(handle_command("/save", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("저장", self.ui.chat_history[-1][1])
            m_open.assert_called()

    def test_load_command(self):
        """/load 명령어가 파일이 존재할 때 복원"""
        sample = '{"thread_id": "test_thread"}'
        with patch("builtins.open", mock_open(read_data=sample)), patch("os.path.exists", return_value=True):
            self.run_async(handle_command("/load", self.ui, self.observer, self.cache, self.thread_id, self.theme))
            self.assertIn("복원", self.ui.chat_history[-1][1])
            self.assertEqual(self.cache[self.thread_id], {"thread_id": "test_thread"})

    def test_rca_command_missing(self):
        """/rca 명령어가 체인을 찾지 못했을 때 메시지"""
        self.observer.get_causal_chain.return_value = []
        self.run_async(handle_command("/rca missing", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("계보", self.ui.chat_history[-1][1])

    @patch("gortex.core.commands.SynapticIndexer")
    def test_search_no_results(self, mock_indexer_cls):
        """/search 결과 없을 때"""
        mock_indexer = mock_indexer_cls.return_value
        mock_indexer.search.return_value = []
        self.run_async(handle_command("/search nothing", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("검색 결과가 없습니다", self.ui.chat_history[-1][1])

    def test_unknown_command(self):
        """알 수 없는 명령어에 대해 에러 안내"""
        self.run_async(handle_command("/unknown", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertIn("알 수 없는 명령어", self.ui.chat_history[-1][1])

    def test_provider_switching_command(self):
        """/provider 명령어가 GortexAuth의 provider 설정을 변경하는지 테스트"""
        GortexAuth._reset()
        auth = GortexAuth()
        self.run_async(handle_command("/provider ollama", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(auth._provider, "ollama")
        self.ui.update_sidebar.assert_called()
        
        self.run_async(handle_command("/provider unknown", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(auth._provider, "ollama")
        last_msg = self.ui.chat_history[-1]
        self.assertIn("Unknown provider", last_msg[1])

    def test_model_switching_command(self):
        """/model 명령어가 Ollama 모델 설정을 변경하는지 테스트"""
        GortexAuth._reset()
        auth = GortexAuth()
        auth._provider = "ollama"
        self.run_async(handle_command("/model qwen2.5:7b", self.ui, self.observer, self.cache, self.thread_id, self.theme))
        self.assertEqual(auth.ollama_model, "qwen2.5:7b")

if __name__ == "__main__":
    unittest.main()