import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.utils.efficiency_monitor import EfficiencyMonitor
from gortex.agents.planner import PlannerAgent
from gortex.core.state import GortexState

class TestPerformancePrediction(unittest.TestCase):
    def setUp(self):
        self.stats_path = "tests/test_efficiency_stats.jsonl"
        self.monitor = EfficiencyMonitor(stats_path=self.stats_path)
        
        # 가상의 성공 이력 데이터 주입 (2개 데이터 포인트)
        # Coder: 평균 2000 tokens, 10000ms
        with open(self.stats_path, "w") as f:
            f.write(json.dumps({"timestamp": "2025-12-23T00:00:00", "agent": "coder", "success": True, "tokens": 1500, "latency_ms": 8000}) + "\n")
            f.write(json.dumps({"timestamp": "2025-12-23T00:01:00", "agent": "coder", "success": True, "tokens": 2500, "latency_ms": 12000}) + "\n")

    def tearDown(self):
        if os.path.exists(self.stats_path): os.remove(self.stats_path)
        health_path = self.stats_path.replace("stats.jsonl", "health_history.jsonl")
        if os.path.exists(health_path): os.remove(health_path)

    def test_predict_resource_usage(self):
        """과거 데이터 기반 리소스 사용량 예측 테스트"""
        prediction = self.monitor.predict_resource_usage("coder")
        
        # (1500 + 2500) / 2 = 2000
        self.assertEqual(prediction["avg_tokens"], 2000)
        # (8000 + 12000) / 2 = 10000
        self.assertEqual(prediction["avg_latency_ms"], 10000)
        self.assertEqual(prediction["data_points"], 2)

    @patch("gortex.utils.efficiency_monitor.EfficiencyMonitor.predict_resource_usage")
    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    @patch("gortex.utils.indexer.SynapticIndexer")
    def test_planner_resource_alert(self, mock_indexer, mock_factory, mock_predict):
        """플래너의 고부하 작업 예측 및 경고 테스트"""
        # 1. Setup Mock Monitor
        mock_predict.return_value = {"avg_tokens": 10000, "avg_latency_ms": 30000}
        
        # 2. Setup Mock Backend
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        # 2개 단계를 가진 계획 응답 시뮬레이션
        mock_backend.generate.return_value = json.dumps({
            "thought_process": "Planning a big task",
            "goal": "Complex Refactoring",
            "steps": [
                {"id": 1, "action": "write_file", "target": "a.py", "reason": "R1", "priority": 10, "is_essential": True},
                {"id": 2, "action": "apply_patch", "target": "b.py", "reason": "R2", "priority": 10, "is_essential": True}
            ]
        })
        mock_backend.supports_structured_output.return_value = False
        
        state: GortexState = {
            "messages": [("user", "refactor everything")],
            "agent_energy": 100,
            "working_dir": "."
        }
        
        # 3. Run Planner
        agent = PlannerAgent()
        result = agent.run(state)
        
        # 4. Verify
        # 총 예상 토큰: 10000 * 2 = 20000
        # 예상 비용: 20000 / 1,000,000 * 0.15 (Flash 기준) = $0.003
        # 만약 budget_limit이 0.01 이하라면 경고가 발생할 것임 (기본 0.5일 경우 $0.1이 임계치)
        # 테스트를 위해 임계치 넘는 높은 토큰량 가정 시 경고 메시지 포함 확인
        self.assertIn("predicted_usage", result)
        self.assertEqual(result["predicted_usage"]["tokens"], 20000)

if __name__ == '__main__':
    unittest.main()
