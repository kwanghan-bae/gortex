import unittest
from unittest.mock import MagicMock, patch
from gortex.utils.memory import summarizer_node, compress_synapse, prune_synapse

class TestGortexMemoryLogic(unittest.TestCase):
    
    @patch('gortex.utils.memory.GortexAuth')
    def test_compress_synapse(self, mock_auth_cls):
        """메시지 압축 로직 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.text = "SUMMARY TEXT"
        mock_auth.generate.return_value = mock_response
        
        # 12개 이상의 메시지가 있을 때 압축 수행
        long_msgs = [("user", f"msg {i}") for i in range(15)]
        state = {"messages": long_msgs}
        
        new_state = compress_synapse(state)
        
        # 첫 번째 메시지가 시스템 요약으로 교체되었는지 확인
        self.assertTrue("SUMMARY TEXT" in new_state["messages"][0][1])
        # 최근 3개 메시지는 유지되었는지 확인
        self.assertEqual(len(new_state["messages"]), 4) # 요약(1) + 최근(3)

    def test_prune_synapse(self):
        """메시지 가지치기 로직 테스트"""
        limit = 5
        msgs = [("user", f"msg {i}") for i in range(10)]
        pinned = [("system", "PINNED")]
        
        state = {"messages": msgs, "pinned_messages": pinned}
        
        new_state = prune_synapse(state, limit=limit)
        
        # Pinned가 최상단에 있고, 나머지는 최근 메시지로 채워졌는지 확인
        self.assertEqual(len(new_state["messages"]), limit)
        self.assertEqual(new_state["messages"][0], pinned[0])
        self.assertEqual(new_state["messages"][-1], msgs[-1])

    @patch('gortex.utils.memory.compress_synapse')
    @patch('gortex.utils.memory.prune_synapse')
    def test_summarizer_node(self, mock_prune, mock_compress):
        """summarizer 노드가 압축과 가지치기를 순차 실행하는지 테스트"""
        mock_compress.return_value = {"messages": ["compressed"]}
        mock_prune.return_value = {"messages": ["pruned"]}
        
        state = {"messages": []}
        result = summarizer_node(state)
        
        mock_compress.assert_called_once()
        mock_prune.assert_called_once()
        self.assertEqual(result["messages"], ["pruned"])

if __name__ == '__main__':
    unittest.main()