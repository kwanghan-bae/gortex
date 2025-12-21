import unittest
from unittest.mock import MagicMock, patch
from gortex.core.graph import route_manager, route_coder
from gortex.core.state import GortexState

class TestGortexGraphRouting(unittest.TestCase):
    def test_route_manager_standard(self):
        """Manager가 next_node로 정상 라우팅하는지 테스트"""
        state = {"next_node": "planner", "messages": []}
        result = route_manager(state)
        self.assertEqual(result, "planner")

    def test_route_manager_summarization_trigger(self):
        """메시지 수가 많으면 요약(summarizer)으로 라우팅되는지 테스트"""
        long_messages = [MagicMock(content="token "*100) for _ in range(15)]
        state = {"next_node": "planner", "messages": long_messages}
        result = route_manager(state)
        self.assertEqual(result, "summarizer")

    def test_route_manager_end(self):
        """종료 조건 처리 테스트"""
        state = {"next_node": "__end__"}
        result = route_manager(state)
        self.assertEqual(result, "__end__")

    def test_route_coder_loop(self):
        """Coder가 완료되지 않았을 때 다시 Coder로 라우팅되는지 테스트"""
        state = {"next_node": "coder"}
        result = route_coder(state)
        self.assertEqual(result, "coder")

    def test_route_coder_validation(self):
        """Coder 완료 후 Analyst 검증으로 라우팅되는지 테스트"""
        state = {"next_node": "__end__"}
        result = route_coder(state)
        self.assertEqual(result, "analyst")

if __name__ == '__main__':
    unittest.main()
