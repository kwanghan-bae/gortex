import unittest
from unittest.mock import MagicMock, patch
from gortex.agents.manager import manager_node

class TestGortexManager(unittest.TestCase):
    @patch('gortex.agents.manager.GortexAuth')
    def test_manager_routing_to_planner(self, mock_auth_cls):
        """개발 관련 요청 시 planner로 라우팅되는지 테스트"""
        # Mock Auth 설정
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.parsed = {
            "thought": "사용자가 파이썬 코드를 짜달라고 함. planner로 보냄.",
            "next_node": "planner"
        }
        mock_auth.generate.return_value = mock_response

        # 상태 설정
        state = {
            "messages": [("user", "파이썬으로 구구단 출력하는 코드 짜줘")],
            "active_constraints": ["항상 타입 힌트를 사용하라"]
        }

        # 실행
        result = manager_node(state)

        # 검증
        self.assertEqual(result["next_node"], "planner")
        # 시스템 프롬프트에 제약 조건이 포함되었는지 간접 확인 (Mock 호출 인자 확인)
        args, kwargs = mock_auth.generate.call_args
        self.assertIn("항상 타입 힌트를 사용하라", kwargs["config"].system_instruction)

    @patch('gortex.agents.manager.GortexAuth')
    def test_manager_ambiguity_handling(self, mock_auth_cls):
        """모호한 요청 시 질문을 던지고 종료하는지 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.parsed = {
            "thought": "요청이 너무 짧음. 무엇을 분석할지 물어봐야 함.",
            "next_node": "__end__",
            "response_to_user": "무엇을 분석해 드릴까요? 대상 파일을 알려주세요."
        }
        mock_auth.generate.return_value = mock_response

        state = {
            "messages": [("user", "분석해줘")],
            "active_constraints": []
        }

        result = manager_node(state)

        self.assertEqual(result["next_node"], "__end__")
        self.assertEqual(result["messages"][0][1], "무엇을 분석해 드릴까요? 대상 파일을 알려주세요.")

    @patch('gortex.agents.manager.GortexAuth')
    def test_manager_error_fallback(self, mock_auth_cls):
        """API 에러 발생 시 안전하게 종료되는지 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_auth.generate.side_effect = Exception("API connection error")

        state = {
            "messages": [("user", "Hello")],
            "active_constraints": []
        }

        result = manager_node(state)

        # 검증: 에러 상황에서도 결과가 반환되어야 함
        self.assertEqual(result["next_node"], "__end__")
        self.assertIn("오류가 발생했습니다", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()
