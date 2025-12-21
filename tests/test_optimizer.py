import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.optimizer import OptimizerAgent, optimizer_node

class TestGortexOptimizer(unittest.TestCase):
    @patch('gortex.agents.optimizer.LLMFactory')
    def test_optimizer_analysis(self, mock_factory):
        """Optimizer 로그 분석 및 LLM 호출 테스트"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = json.dumps({
            "analysis": "성능 지연 발견. 병렬 처리 도입 권장.",
            "improvement_task": "Swarm 노드 활용도 증대",
            "priority": "medium"
        })
        mock_backend.supports_structured_output.return_value = False
        mock_factory.get_default_backend.return_value = mock_backend

        agent = OptimizerAgent(log_path="dummy.jsonl")
        # 로그가 없을 때의 기본 동작 확인
        result = agent.analyze_performance()
        
        self.assertIn("분석", result["analysis"])
        
    def test_stuck_state_detection(self):
        """동일 동작 반복 감지 테스트"""
        agent = OptimizerAgent()
        
        # 3회 반복 케이스
        msgs = [
            ("ai", "Executed read_file(a.py)"),
            ("system", "Success"),
            ("ai", "Executed read_file(a.py)"),
            ("system", "Success"),
            ("ai", "Executed read_file(a.py)"),
            ("system", "Success")
        ]
        self.assertTrue(agent.detect_stuck_state(msgs))
        
        # 정상 케이스
        msgs_ok = [
            ("ai", "Executed read_file(a.py)"),
            ("ai", "Executed write_file(b.py)")
        ]
        self.assertFalse(agent.detect_stuck_state(msgs_ok))

if __name__ == '__main__':
    unittest.main()