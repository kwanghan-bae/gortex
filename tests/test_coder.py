import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.coder import coder_node

class TestGortexCoder(unittest.TestCase):
    def setUp(self):
        self.state = {
            "messages": [],
            "plan": [json.dumps({"action": "read_file", "target": "test.py"})],
            "current_step": 0,
            "coder_iteration": 0,
            "assigned_model": "test-model"
        }

    @patch('gortex.agents.coder.LLMFactory')
    @patch('gortex.agents.coder.read_file')
    @patch('gortex.agents.coder.execute_shell')
    def test_coder_executes_step(self, mock_shell, mock_read, mock_factory):
        """Coder가 계획된 단계를 실행하고 LLM을 호출하는지 확인"""
        mock_shell.return_value = "Ready to commit"
        mock_backend = MagicMock()
        # Ollama 스타일 JSON 응답 모킹
        mock_backend.generate.return_value = json.dumps({
            "thought": "I will read the file",
            "action": "none",
            "status": "success"
        })
        mock_backend.supports_structured_output.return_value = False
        mock_factory.get_default_backend.return_value = mock_backend
        
        mock_read.return_value = "file content"
        
        res = coder_node(self.state)
        
        self.assertEqual(res["current_step"], 1)
        mock_backend.generate.assert_called_once()

    @patch('gortex.agents.coder.LLMFactory')
    def test_coder_handles_tool_call(self, mock_factory):
        """LLM 응답에 포함된 action을 파싱하여 실행하는지 확인"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = json.dumps({
            "thought": "Writing file",
            "action": "write_file",
            "action_input": {"path": "out.txt", "content": "hello"},
            "status": "in_progress"
        })
        mock_backend.supports_structured_output.return_value = False
        mock_factory.get_default_backend.return_value = mock_backend
        
        with patch('gortex.agents.coder.write_file') as mock_write:
            mock_write.return_value = "Success"
            res = coder_node(self.state)
            
            mock_write.assert_called_with("out.txt", "hello")
            self.assertIn("Executed write_file", res["messages"][0][1])

if __name__ == "__main__":
    unittest.main()