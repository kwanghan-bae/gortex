import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from gortex.core.engine import GortexEngine

class TestGortexEngine(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        self.ui.web_manager = MagicMock()
        self.ui.web_manager.broadcast = AsyncMock()
        self.ui.chat_history = []
        self.ui.add_achievement = MagicMock()
        self.ui.add_security_event = MagicMock()
        self.ui.set_mode = MagicMock()
        self.observer = MagicMock()
        self.observer.log_event.return_value = "evt-1"
        self.observer.get_causal_graph.return_value = {}
        self.vocal = MagicMock()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.state_vars = {
            "agent_energy": 100,
            "last_efficiency": 100.0,
            "session_cache": {}
        }

    def run_async(self, coro):
        return asyncio.run(coro)

    @patch('gortex.core.engine.GortexConfig')
    def test_voice_trigger(self, mock_config_cls):
        mock_config = mock_config_cls.return_value
        mock_config.get.return_value = True
        output = {"messages": [("ai", "Hello world")], "file_cache": {}}
        self.run_async(self.engine.process_node_output("coder", output, self.state_vars))
        self.vocal.text_to_speech.assert_called_with("Hello world")
        self.vocal.play_audio.assert_called()

    def test_security_alert_detection(self):
        output = {"messages": [("ai", "❌ Security Alert: Forbidden command")], "file_cache": {}}
        self.run_async(self.engine.process_node_output("coder", output, self.state_vars))
        self.ui.add_security_event.assert_called()

    def test_state_sync(self):
        output = {"agent_energy": 85, "last_efficiency": 92.0, "file_cache": {}}
        self.run_async(self.engine.process_node_output("planner", output, self.state_vars))
        self.assertEqual(self.state_vars["agent_energy"], 85)
        self.assertEqual(self.state_vars["last_efficiency"], 92.0)

    def test_process_node_output_updates_state(self):
        output = {
            "messages": [("ai", "모든 계획된 작업을 완료했습니다")],
            "ui_mode": "coding",
            "agent_economy": {"streak": 1},
            "token_credits": {"credit": 5},
            "agent_energy": 80,
            "last_efficiency": 0.88,
            "file_cache": {"foo": "bar"},
            "status": "failed"
        }
        with patch("gortex.core.engine.GortexConfig") as mock_config, \
             patch("gortex.core.engine.count_tokens", return_value=4), \
             patch("gortex.core.engine.Notifier"), \
             patch("gortex.core.engine.SelfHealingMemory") as mock_healer:
            config_instance = MagicMock()
            config_instance.get.return_value = False
            mock_config.return_value = config_instance
            healer = MagicMock()
            healer.get_solution_hint.return_value = "Try tests"
            mock_healer.return_value = healer
            self.engine.healer = healer
            tokens = asyncio.run(self.engine.process_node_output("coder", output, self.state_vars))
        self.assertEqual(tokens, 4)
        self.assertEqual(self.state_vars["agent_economy"]["streak"], 1)
        self.assertEqual(self.state_vars["token_credits"]["credit"], 5)
        self.assertEqual(self.state_vars["agent_energy"], 80)
        self.assertEqual(self.ui.add_achievement.call_args[0][0], "Goal Reached")
        self.ui.set_mode.assert_called_with("coding")
        self.assertEqual(self.state_vars["file_cache"]["foo"], "bar")
        self.assertEqual(healer.get_solution_hint.call_count, 1)
        self.observer.log_event.assert_called()

if __name__ == '__main__':
    unittest.main()
