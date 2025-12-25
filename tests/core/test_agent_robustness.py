
import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.coder import CoderAgent
from gortex.core.state import GortexState

class TestAgentRobustness(unittest.TestCase):
    def setUp(self):
        self.agent = CoderAgent()
        self.agent.backend = MagicMock()
        # State 초기화
        self.state = {
            "messages": [],
            "plan": [json.dumps({"action": "coding", "target": "test.py"})],
            "current_step": 0,
            "agent_economy": {}
        }

    def test_malformed_json_response(self):
        """LLM이 깨진 JSON을 반환할 때 에러를 잡고 다음 턴으로 넘어가야 함"""
        # Given
        self.agent.backend.generate.return_value = '```json\n{"thought": "broken... missing bracket'
        
        # When
        result = self.agent.run(self.state)
        
        # Then
        # CoderAgent는 json.loads 실패 시 Exception 블록으로 감
        self.assertIn("messages", result)
        last_msg = result["messages"][0]
        self.assertEqual(last_msg[0], "system")
        self.assertIn("Error", str(last_msg[1])) # JSONDecodeError 포함

    @patch("gortex.agents.coder.write_file")
    @patch("gortex.agents.coder.registry") 
    def test_tool_execution_crash_handling(self, mock_registry, mock_write_file):
        """툴 실행 중 크래시가 발생하면 시스템 메시지로 에러를 보고해야 함"""
        # Given
        self.agent.backend.generate.return_value = json.dumps({
            "thought": "Writing file...",
            "action": "write_file",
            "action_input": {"path": "test.py", "content": "print('hello')"},
            "status": "in_progress"
        })
        
        # 권한 허용 (registry mock)
        mock_registry.is_tool_permitted.return_value = True
        
        # 툴이 예외를 던지도록 설정
        mock_write_file.side_effect = RuntimeError("Disk full!")
        
        # When
        result = self.agent.run(self.state)
        
        # Then
        self.assertIn("messages", result)
        last_msg = result["messages"][0]
        # CoderAgent.run의 except 블록에서 ("system", "Error: ...") 반환
        self.assertEqual(last_msg[0], "system")
        self.assertIn("Disk full!", str(last_msg[1]))

if __name__ == '__main__':
    unittest.main()
