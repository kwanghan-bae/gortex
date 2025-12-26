import unittest
import inspect
import asyncio
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from gortex import main

class TestMainIntegrity(unittest.IsolatedAsyncioTestCase):
    """
    main.py의 무결성을 검증하는 테스트.
    """
    def setUp(self):
        # 테스트 중 불필요한 로그 노이즈 제거
        logging.disable(logging.WARNING)

    def tearDown(self):
        # 로그 설정 원상 복구
        logging.disable(logging.NOTSET)

    def test_essential_functions_exist(self):
        """핵심 함수들이 main 모듈에 정의되어 있는지 확인"""
        self.assertTrue(hasattr(main, 'run_gortex'), "run_gortex 함수가 main.py에서 사라졌습니다!")
        self.assertTrue(hasattr(main, 'energy_recovery_loop'), "energy_recovery_loop 함수가 main.py에서 사라졌습니다!")
        self.assertTrue(hasattr(main, 'save_sessions_cache'), "save_sessions_cache 함수가 main.py에서 사라졌습니다!")

    def test_async_functions(self):
        """핵심 함수들이 올바른 비동기(async) 속성을 가졌는지 확인"""
        self.assertTrue(inspect.iscoroutinefunction(main.run_gortex), "run_gortex는 async 함수여야 합니다.")
        self.assertTrue(inspect.iscoroutinefunction(main.energy_recovery_loop), "energy_recovery_loop는 async 함수여야 합니다.")

    @patch('gortex.main.GortexAuth')
    @patch('gortex.main.console')
    @patch('gortex.main.DashboardUI')
    @patch('gortex.main.BootManager')
    @patch('gortex.main.os.path.exists')
    @patch('gortex.main.prompt_session.prompt_async')
    async def test_run_gortex_ollama_interactive_affirmative(self, mock_prompt, mock_exists, mock_boot_cls, mock_ui, mock_console, mock_auth_cls):
        """Ollama 선택 시 한국어 긍정 입력(ㅇㅇ)이 모델 다운로드를 트리거하는지 테스트"""
        mock_boot = mock_boot_cls.return_value
        mock_boot.run_sequence = AsyncMock()
        mock_exists.return_value = False
        mock_auth = mock_auth_cls.return_value
        mock_auth._CONFIG_PATH = "logs/fake_config.json"
        mock_auth.get_provider.return_value = "GEMINI"
        mock_auth.check_ollama_connection.return_value = True
        mock_auth.list_ollama_models.return_value = []
        
        mock_console.input.side_effect = ["2", "ㅇㅇ"]
        mock_prompt.side_effect = EOFError()
        
        with patch('gortex.main.argparse.ArgumentParser.parse_known_args') as mock_parse:
            args = MagicMock(); args.provider = None; args.setup = False
            mock_parse.return_value = (args, [])
            try:
                await asyncio.wait_for(main.run_gortex(), timeout=5)
            except (KeyboardInterrupt, EOFError, asyncio.TimeoutError):
                pass
            
        mock_auth.pull_recommended_stack.assert_called_once()
        mock_auth.set_provider.assert_any_call("ollama")

    @patch('gortex.main.GortexAuth')
    @patch('gortex.main.console')
    @patch('gortex.main.DashboardUI')
    @patch('gortex.main.BootManager')
    @patch('gortex.main.os.path.exists')
    @patch('gortex.main.prompt_session.prompt_async')
    async def test_run_gortex_ollama_no_redundant_pull(self, mock_prompt, mock_exists, mock_boot_cls, mock_ui, mock_console, mock_auth_cls):
        """이미 모든 권장 모델이 있을 때 다운로드 제안을 건너뛰는지 테스트"""
        mock_boot = mock_boot_cls.return_value
        mock_boot.run_sequence = AsyncMock()
        mock_exists.return_value = False
        mock_auth = mock_auth_cls.return_value
        mock_auth._CONFIG_PATH = "logs/fake_config.json"
        mock_auth.get_provider.return_value = "GEMINI"
        mock_auth.check_ollama_connection.return_value = True
        mock_auth.list_ollama_models.return_value = ["functiongemma:latest", "qwen3:8b", "qwen2.5-coder:7b", "falcon3:7b"]
        
        mock_console.input.side_effect = ["2"]
        mock_prompt.side_effect = EOFError()
        
        with patch('gortex.main.argparse.ArgumentParser.parse_known_args') as mock_parse:
            args = MagicMock(); args.provider = None; args.setup = False
            mock_parse.return_value = (args, [])
            try:
                await asyncio.wait_for(main.run_gortex(), timeout=5)
            except (KeyboardInterrupt, EOFError, asyncio.TimeoutError):
                pass
            
        self.assertEqual(mock_auth.pull_recommended_stack.call_count, 0)
        mock_auth.set_provider.assert_any_call("ollama")

    @patch('gortex.main.GortexAuth')
    @patch('gortex.main.console')
    @patch('gortex.main.DashboardUI')
    @patch('gortex.main.BootManager')
    @patch('gortex.main.argparse.ArgumentParser.parse_known_args')
    @patch('gortex.main.os.path.exists')
    @patch('gortex.main.prompt_session.prompt_async')
    async def test_run_gortex_cli_arg_override(self, mock_prompt, mock_exists, mock_parse, mock_boot_cls, mock_ui, mock_console, mock_auth_cls):
        """CLI 인자(--provider)가 설정을 강제하는지 테스트"""
        mock_boot = mock_boot_cls.return_value
        mock_boot.run_sequence = AsyncMock()
        mock_exists.return_value = True
        mock_auth = mock_auth_cls.return_value
        mock_auth._CONFIG_PATH = "logs/fake_config.json"
        
        mock_args = MagicMock()
        mock_args.provider = "ollama"; mock_args.setup = False
        mock_parse.return_value = (mock_args, [])
        
        mock_prompt.side_effect = EOFError()
        
        try:
            await asyncio.wait_for(main.run_gortex(), timeout=5)
        except (KeyboardInterrupt, EOFError, asyncio.TimeoutError):
            pass
            
        mock_auth.set_provider.assert_any_call("ollama")

if __name__ == "__main__":
    unittest.main()