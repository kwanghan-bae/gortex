import unittest
import os
from unittest.mock import MagicMock, patch
from gortex.core.state import GortexState
from gortex.utils.memory import compress_synapse, prune_synapse

class TestContextPruning(unittest.TestCase):
    def setUp(self):
        # 더미 상태 생성 (20개의 메시지)
        self.messages = [("user", f"message {i}") for i in range(20)]
        self.state: GortexState = {
            "messages": self.messages,
            "history_summary": "",
            "active_constraints": ["Rule 1"]
        }

    @patch("gortex.utils.memory.get_summarizer")
    def test_compress_synapse_ollama(self, mock_get_summarizer):
        """Ollama 환경에서 압축이 일찍 트리거되는지 테스트"""
        os.environ["LLM_BACKEND"] = "ollama"
        
        mock_summarizer = mock_get_summarizer.return_value
        mock_summarizer.summarize.return_value = "Structured Summary Result"
        
        # 20개 메시지 상태에서 압축 실행
        result = compress_synapse(self.state)
        
        # 결과 확인: 메시지 수가 줄어들어야 함 (시스템 요약 + 최근 4개 = 5개)
        self.assertEqual(len(result["messages"]), 5)
        self.assertIn("[PROJECT STATE SUMMARY]", result["messages"][0][1])
        self.assertEqual(result["history_summary"], "Structured Summary Result")

    def test_prune_synapse_limit(self):
        """가지치기 한계치가 정상 적용되는지 테스트"""
        os.environ["LLM_BACKEND"] = "ollama" # Limit 20
        
        # 30개 메시지 생성
        long_messages = [("ai", f"msg {i}") for i in range(30)]
        state: GortexState = {"messages": long_messages}
        
        pruned_state = prune_synapse(state)
        
        # 30개 -> 20개로 줄어들어야 함
        self.assertEqual(len(pruned_state["messages"]), 20)
        # 첫 번째 메시지는 보존되어야 함
        self.assertEqual(pruned_state["messages"][0], long_messages[0])
        # 마지막 메시지도 보존되어야 함
        self.assertEqual(pruned_state["messages"][-1], long_messages[-1])

if __name__ == '__main__':
    unittest.main()
