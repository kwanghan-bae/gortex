import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.manager import manager_node

class TestGortexManager(unittest.TestCase):
    @patch('gortex.agents.manager.LLMFactory')
    def test_manager_routing_to_planner(self, mock_factory):
        """개발 관련 요청 시 planner로 라우팅되는지 테스트"""
        # Mock Backend 설정
        mock_backend = MagicMock()
        mock_backend.generate.return_value = json.dumps({
            "thought": "사용자가 파이썬 코드를 짜달라고 함. planner로 보냄.",
            "internal_critique": "Logic is sound.",
            "thought_tree": [{"id": "1", "text": "Analyzing intent", "type": "analysis", "priority": 1, "certainty": 1.0}],
            "next_node": "planner"
        })
        mock_backend.supports_structured_output.return_value = False
        mock_factory.get_default_backend.return_value = mock_backend

        # 상태 설정
        state = {
            "messages": [("user", "파이썬으로 구구단 출력하는 코드 짜줘")],
            "active_constraints": ["항상 타입 힌트를 사용하라"]
        }

        # 실행
        result = manager_node(state)

        # 검증
        self.assertEqual(result["next_node"], "planner")
        mock_backend.generate.assert_called_once()

    @patch('gortex.agents.manager.LLMFactory')
    def test_manager_ambiguity_handling(self, mock_factory):
        """모호한 요청 시 질문을 던지고 종료하는지 테스트"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = json.dumps({
            "thought": "요청이 너무 짧음. 무엇을 분석할지 물어봐야 함.",
            "internal_critique": "Ambiguous input.",
            "thought_tree": [],
            "next_node": "__end__",
            "response_to_user": "무엇을 분석해 드릴까요? 대상 파일을 알려주세요."
        })
        mock_backend.supports_structured_output.return_value = False
        mock_factory.get_default_backend.return_value = mock_backend

        state = {
            "messages": [("user", "분석해줘")],
            "active_constraints": []
        }

        result = manager_node(state)

        self.assertEqual(result["next_node"], "__end__")
        self.assertEqual(result["messages"][0][1], "무엇을 분석해 드릴까요? 대상 파일을 알려주세요.")

    @patch('gortex.agents.manager.LLMFactory')
    def test_manager_error_fallback(self, mock_factory):
        """API 에러 발생 시 안전하게 종료되는지 테스트"""
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = Exception("API connection error")
        mock_factory.get_default_backend.return_value = mock_backend

        state = {
            "messages": [("user", "Hello")],
            "active_constraints": []
        }

        result = manager_node(state)

        # 검증: 에러 상황에서도 결과가 반환되어야 함
        self.assertEqual(result["next_node"], "__end__")
        self.assertIn("실패", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()