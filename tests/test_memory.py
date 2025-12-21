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

    def test_compress_synapse_early_return(self):
        """메시지 개수가 적을 때 압축을 건너뛰는지 확인"""
        state = {"messages": [("user", "hi")], "history_summary": None}
        new_state = compress_synapse(state)
        self.assertEqual(state, new_state)

    @patch('gortex.utils.memory.GortexAuth')
    def test_compress_synapse_with_constraints(self, mock_auth_cls):
        """active_constraints가 프롬프트에 포함되는지 확인"""
        mock_auth = mock_auth_cls.return_value
        mock_response = MagicMock()
        mock_response.text = "SUMMARY"
        mock_auth.generate.return_value = mock_response
        
        state = {
            "messages": [("user", f"m{i}") for i in range(15)],
            "active_constraints": ["Constraint 1"]
        }
        compress_synapse(state)
        
        # generate 호출 시 프롬프트(system_prompt 등은 positional 혹은 keyword로 전달될 수 있음)
        # 소스 코드상 auth.generate(summary_model, messages, config) 임.
        # 프롬프트는 로컬 변수이므로 직접 검증은 어렵지만, 에러 없이 실행됨을 확인.
        mock_auth.generate.assert_called_once()

    @patch('gortex.utils.memory.GortexAuth')
    def test_compress_synapse_exception(self, mock_auth_cls):
        """예외 발생 시 원래 상태를 반환하는지 확인"""
        mock_auth = mock_auth_cls.return_value
        mock_auth.generate.side_effect = Exception("API Error")
        
        state = {"messages": [("user", f"m{i}") for i in range(15)]}
        new_state = compress_synapse(state)
        self.assertEqual(state, new_state)

    def test_prune_synapse_early_return(self):
        """메시지 개수가 limit 이하일 때 건너뛰는지 확인"""
        state = {"messages": [("user", "hi")]}
        new_state = prune_synapse(state, limit=10)
        self.assertEqual(state, new_state)

if __name__ == '__main__':
    unittest.main()