import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.coder import coder_node

class TestGortexCoder(unittest.TestCase):
    @patch('gortex.agents.coder.GortexAuth')
    def test_coder_execution_limit(self, mock_auth_cls):
        """최대 반복 횟수 초과 시 중단 테스트"""
        state = {
            "coder_iteration": 30,
            "plan": [],
            "messages": []
        }
        result = coder_node(state)
        self.assertEqual(result["next_node"], "__end__")
        self.assertIn("30회에서 중단", result["messages"][0][1])

    @patch('gortex.agents.coder.execute_shell')
    @patch('gortex.agents.coder.GortexAuth')
    def test_coder_executes_step(self, mock_auth_cls, mock_exec):
        """Coder가 계획된 단계를 실행하려고 도구를 호출하는지 테스트"""
        # Mock Auth Response (Function Calling 시뮬레이션)
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        
        # 가짜 Function Call 생성
        mock_part = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "execute_shell"
        mock_fc.args = {"command": "echo test"}
        mock_part.function_call = mock_fc
        mock_response.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]
        
        mock_auth.generate.return_value = mock_response
        
        # Tool execution result
        mock_exec.return_value = "test output"

        # State 설정
        plan_step = json.dumps({
            "id": 1,
            "action": "execute_shell",
            "target": "echo test",
            "reason": "Test execution"
        })
        state = {
            "plan": [plan_step],
            "current_step": 0,
            "coder_iteration": 0,
            "messages": [],
            "active_constraints": []
        }

        # 실행
        result = coder_node(state)

        # 검증
        self.assertEqual(result["next_node"], "coder") # 결과 확인을 위해 다시 호출되어야 함
        self.assertEqual(result["coder_iteration"], 1) # 반복 횟수 증가
        mock_exec.assert_called_with("echo test") # 실제 도구 함수 호출 확인

if __name__ == '__main__':
    unittest.main()
