import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.planner import planner_node

class TestGortexPlanner(unittest.TestCase):
    
    @patch('gortex.agents.planner.list_files')
    @patch('gortex.agents.planner.GortexAuth')
    def test_planner_creates_plan(self, mock_auth_cls, mock_list_files):
        """Planner가 정상적으로 계획을 수립하고 coder로 라우팅하는지 테스트"""
        # Mock Setup
        mock_list_files.return_value = "main.py\nrequirements.txt"
        
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        
        # 예상되는 Planner 응답 데이터
        plan_data = {
            "thought_process": "테스트 계획 수립",
            "goal": "Test Goal",
            "steps": [
                {"id": 1, "action": "read_file", "target": "main.py", "reason": "Check content"},
                {"id": 2, "action": "write_file", "target": "test.py", "reason": "Create test"}
            ]
        }
        
        # google-genai response mocking
        mock_response.parsed = plan_data
        mock_response.text = json.dumps(plan_data)
        mock_auth.generate.return_value = mock_response

        # Input State
        state = {
            "messages": [("user", "테스트 파일 만들어줘")],
            "working_dir": ".",
            "active_constraints": ["Rule 1"]
        }

        # Execute
        result = planner_node(state)

        # Verify
        self.assertEqual(result["next_node"], "coder")
        self.assertEqual(result["current_step"], 0)
        self.assertEqual(len(result["plan"]), 2)
        
        # Plan 내용 검증 (JSON 문자열로 변환되었는지)
        first_step = json.loads(result["plan"][0])
        self.assertEqual(first_step["action"], "read_file")
        self.assertEqual(first_step["target"], "main.py")
        
        # System Prompt 검증
        args, kwargs = mock_auth.generate.call_args
        system_instruction = kwargs["config"].system_instruction
        self.assertIn("Rule 1", system_instruction) # 제약조건 주입 확인
        self.assertIn("main.py", system_instruction) # 파일 리스트 주입 확인

if __name__ == '__main__':
    unittest.main()
