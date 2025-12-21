import unittest
import os
from unittest.mock import MagicMock, patch
from gortex.utils.memory import summarizer_node, compress_synapse, prune_synapse

class TestGortexMemoryLogic(unittest.TestCase):
    
    @patch('gortex.utils.memory.LLMFactory')
    def test_compress_synapse(self, mock_factory):
        """메시지 압축 로직 테스트 (LLMFactory 사용)"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "SUMMARY TEXT"
        mock_factory.get_default_backend.return_value = mock_backend
        
        # 12개 이상의 메시지가 있을 때 압축 수행
        long_msgs = [("user", f"msg {i}") for i in range(15)]
        state = {"messages": long_msgs}
        
        new_state = compress_synapse(state)
        
        # 백엔드 호출 확인
        mock_factory.get_default_backend.assert_called_once()
        mock_backend.generate.assert_called_once()
        
        # 첫 번째 메시지가 시스템 요약으로 교체되었는지 확인
        self.assertTrue("SUMMARY TEXT" in new_state["messages"][0][1])
        # 최근 3개 메시지는 유지되었는지 확인
        self.assertEqual(len(new_state["messages"]), 4) # 요약(1) + 최근(3)

    def test_compress_synapse_early_return(self):
        """메시지 개수가 적을 때 압축을 건너뛰는지 확인"""
        state = {"messages": [("user", "hi")], "history_summary": None}
        new_state = compress_synapse(state)
        self.assertEqual(state, new_state)

    @patch('gortex.utils.memory.LLMFactory')
    def test_compress_synapse_with_constraints(self, mock_factory):
        """active_constraints가 프롬프트에 포함되는지 확인"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "SUMMARY"
        mock_factory.get_default_backend.return_value = mock_backend
        
        state = {
            "messages": [("user", f"m{i}") for i in range(15)],
            "active_constraints": ["Constraint 1"]
        }
        compress_synapse(state)
        
        # generate 호출 인자 검사
        args, _ = mock_backend.generate.call_args
        messages_arg = args[1]
        # 시스템 프롬프트(첫 번째 메시지)에 제약 조건이 포함되어야 함
        system_prompt = messages_arg[0]['content']
        self.assertIn("Constraint 1", system_prompt)

    @patch('gortex.utils.memory.LLMFactory')
    def test_compress_synapse_exception(self, mock_factory):
        """예외 발생 시 원래 상태를 반환하는지 확인"""
        mock_backend = MagicMock()
        mock_backend.generate.side_effect = Exception("Backend Fail")
        mock_factory.get_default_backend.return_value = mock_backend
        
        state = {"messages": [("user", f"m{i}") for i in range(15)]}
        new_state = compress_synapse(state)
        self.assertEqual(state, new_state)

    @patch.dict(os.environ, {"LLM_BACKEND": "ollama", "OLLAMA_DEFAULT_MODEL": "test-model"})
    @patch('gortex.utils.memory.LLMFactory')
    def test_compress_synapse_ollama_model(self, mock_factory):
        """Ollama 백엔드 사용 시 모델명 환경변수 적용 확인"""
        mock_backend = MagicMock()
        mock_factory.get_default_backend.return_value = mock_backend
        
        state = {"messages": [("user", f"m{i}") for i in range(15)]}
        compress_synapse(state)
        
        args, _ = mock_backend.generate.call_args
        self.assertEqual(args[0], "test-model")

    @patch('gortex.utils.memory.LLMFactory')
    def test_compress_synapse_dict_messages(self, mock_factory):
        """메시지가 딕셔너리 형태일 때 처리 확인"""
        mock_backend = MagicMock()
        mock_factory.get_default_backend.return_value = mock_backend
        
        # 딕셔너리 메시지 혼합
        msgs = [{"role": "user", "content": f"m{i}"} for i in range(15)]
        state = {"messages": msgs}
        
        compress_synapse(state)
        
        args, _ = mock_backend.generate.call_args
        context_msgs = args[1]
        # 시스템 프롬프트(0) 이후 사용자 메시지 확인
        self.assertEqual(context_msgs[1]["content"], "m0")

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

    def test_prune_synapse_early_return(self):
        """메시지 개수가 limit 이하일 때 건너뛰는지 확인"""
        state = {"messages": [("user", "hi")]}
        new_state = prune_synapse(state, limit=10)
        self.assertEqual(state, new_state)

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
