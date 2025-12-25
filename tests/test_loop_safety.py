import unittest
import asyncio
from unittest.mock import patch, MagicMock
from gortex.main import get_user_input

class TestLoopSafety(unittest.TestCase):
    """
    메인 루프의 안전성을 검증하는 테스트.
    사용자 입력 시 예외가 발생해도 시스템이 멈추거나 폭주하지 않아야 한다.
    """

    @patch('gortex.main.prompt_session.prompt_async')
    def test_input_eof_handling(self, mock_prompt):
        """EOFError(Ctrl+D) 발생 시 None을 반환해야 한다 (종료 시그널)"""
        mock_prompt.side_effect = EOFError
        
        result = asyncio.run(get_user_input(MagicMock()))
        self.assertIsNone(result, "EOFError 발생 시 None을 반환해야 한다.")

    @patch('gortex.main.prompt_session.prompt_async')
    def test_input_interrupt_handling(self, mock_prompt):
        """KeyboardInterrupt(Ctrl+C) 발생 시 None을 반환해야 한다"""
        mock_prompt.side_effect = KeyboardInterrupt
        
        result = asyncio.run(get_user_input(MagicMock()))
        self.assertIsNone(result, "KeyboardInterrupt 발생 시 None을 반환해야 한다.")

    @patch('gortex.main.prompt_session.prompt_async')
    def test_normal_input(self, mock_prompt):
        """정상 입력 시 문자열을 반환해야 한다"""
        mock_prompt.return_value = "  Hello  "
        
        result = asyncio.run(get_user_input(MagicMock()))
        self.assertEqual(result, "Hello", "입력값의 공백이 제거되어야 한다.")

if __name__ == "__main__":
    unittest.main()
