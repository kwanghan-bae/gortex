import unittest
import asyncio
from unittest.mock import MagicMock, patch
from gortex.core.engine import GortexEngine

class TestGortexEngine(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        # web_manager와 broadcast를 AsyncMock으로 설정
        self.ui.web_manager = MagicMock()
        self.ui.web_manager.broadcast = unittest.mock.AsyncMock()
        
        self.ui.chat_history = []
        self.observer = MagicMock()
        self.vocal = MagicMock()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.state_vars = {
            "agent_energy": 100, "last_efficiency": 100.0,
            "session_cache": {}
        }

    def run_async(self, coro):
        return asyncio.run(coro)

    @patch('gortex.core.engine.GortexConfig')
    def test_voice_trigger(self, mock_config_cls):
        """음성 활성화 시 AI 메시지가 TTS로 전달되는지 테스트"""
        mock_config = mock_config_cls.return_value
        mock_config.get.return_value = True # Voice ON
        
        output = {"messages": [("ai", "Hello world")]}
        self.run_async(self.engine.process_node_output("coder", output, self.state_vars))
        
        self.vocal.text_to_speech.assert_called_with("Hello world")
        self.vocal.play_audio.assert_called()

    def test_security_alert_detection(self):
        """보안 위반 메시지 감지 시 UI에 보안 이벤트가 추가되는지 테스트"""
        output = {"messages": [("ai", "❌ Security Alert: Forbidden command")]}
        self.run_async(self.engine.process_node_output("coder", output, self.state_vars))
        
        self.ui.add_security_event.assert_called()

    def test_state_sync(self):
        """에너지 및 효율성 데이터가 state_vars에 올바르게 반영되는지 테스트"""
        output = {"agent_energy": 85, "last_efficiency": 92.0}
        self.run_async(self.engine.process_node_output("planner", output, self.state_vars))
        
        self.assertEqual(self.state_vars["agent_energy"], 85)
        self.assertEqual(self.state_vars["last_efficiency"], 92.0)

if __name__ == '__main__':
    unittest.main()
