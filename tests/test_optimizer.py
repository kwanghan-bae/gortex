import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.agents.optimizer import OptimizerAgent, optimizer_node

class TestGortexOptimizer(unittest.TestCase):
    def setUp(self):
        self.log_path = "test_trace.jsonl"
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        
        # 가짜 로그 데이터 생성
        logs = [
            {"agent": "Coder", "event": "error", "payload": "FileNotFoundError", "latency_ms": 100},
            {"agent": "Researcher", "event": "result", "payload": "Success", "latency_ms": 5000}
        ]
        with open(self.log_path, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    @patch('gortex.agents.optimizer.GortexAuth')
    def test_optimizer_analysis(self, mock_auth_cls):
        """Optimizer 로그 분석 및 LLM 호출 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "analysis": "문제점: 파일 에러 빈발. 개선 제안: 파일을 먼저 확인하세요.",
            "improvement_task": "Add file checks",
            "priority": "high"
        })
        mock_auth.generate.return_value = mock_res

        agent = OptimizerAgent(log_path=self.log_path)
        result = agent.analyze_performance()
        
        self.assertIsInstance(result, dict)
        self.assertIn("개선 제안", result["analysis"])
        self.assertEqual(mock_auth.generate.call_count, 1)


    @patch('gortex.agents.optimizer.OptimizerAgent')
    def test_optimizer_node(self, mock_agent_cls):
        """Optimizer 노드 실행 테스트"""
        mock_agent = mock_agent_cls.return_value
        mock_agent.analyze_performance.return_value = {
            "analysis": "Mocked Analysis",
            "improvement_task": "Do something",
            "priority": "low"
        }
        
        state = {"messages": []}
        result = optimizer_node(state)
        
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("Mocked Analysis", result["messages"][0][1])


if __name__ == '__main__':
    unittest.main()
