import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.planner import planner_node

class TestGortexPlanner(unittest.TestCase):
    @patch('gortex.agents.planner.LLMFactory')
    @patch('gortex.agents.planner.SynapticIndexer')
    def test_planner_creates_plan(self, mock_indexer, mock_factory):
        """Planner가 정상적으로 계획을 수립하고 coder로 라우팅하는지 테스트"""
        
        # 1. Mock 설정
        mock_backend = MagicMock()
        mock_backend.supports_structured_output.return_value = False
        
        # 새로운 응답 형식에 맞게 모킹
        mock_backend.generate.return_value = json.dumps({
            "thought_process": "구구단 출력을 위해 loop가 필요함.",
            "goal": "구구단 코드 작성",
            "steps": [
                {"id": 1, "action": "write_file", "target": "gugu.py", "reason": "코드 생성"},
                {"id": 2, "action": "execute_shell", "target": "python3 gugu.py", "reason": "실행 확인"}
            ],
            "internal_critique": "None",
            "thought_tree": []
        })
        mock_factory.get_default_backend.return_value = mock_backend
        
        # 2. 상태 설정
        state = {
            "messages": [("user", "파이썬 구구단 짜줘")],
            "working_dir": ".",
            "active_constraints": []
        }

        # 3. 실행
        result = planner_node(state)

        # 4. 검증
        self.assertEqual(result["next_node"], "coder")
        self.assertEqual(len(result["plan"]), 2)
        # i18n 메시지 대응
        self.assertTrue("Establishing plan" in result["messages"][0][1] or "계획을 수립했습니다" in result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()