import unittest
from unittest.mock import patch
from gortex.agents.manager import manager_node
from gortex.core.state import GortexState

class TestProactiveExpansion(unittest.TestCase):
    @patch("gortex.agents.manager.SemanticLogSearch")
    @patch("gortex.agents.manager.SynapticTranslator")
    @patch("gortex.agents.manager.LongTermMemory")
    @patch("gortex.agents.manager.EfficiencyMonitor")
    def test_manager_handles_agent_proposal(self, mock_monitor, mock_ltm, mock_trans, mock_log):
        """TrendScout의 에이전트 확장 제안 시 Manager의 라우팅 테스트"""
        
        # 1. TrendScout이 보낸 가상의 제안 데이터 설정
        mock_proposal = {
            "agent_name": "RustOptimizer",
            "role": "Performance Expert",
            "strategic_value": "Accelerates core engine by 300%"
        }
        
        state: GortexState = {
            "messages": [("user", "Check for trends")],
            "agent_proposals": [mock_proposal], # 제안 주입
            "agent_energy": 100,
            "working_dir": "."
        }
        
        # 2. Manager 실행 (LLM 호출 없이 즉시 제안 처리 로직 작동 기대)
        result = manager_node(state)
        
        # 3. 결과 확인
        # Manager는 제안을 받으면 즉시 Analyst에게 검토(capability_gap_analysis)를 요청해야 함
        self.assertEqual(result["next_node"], "analyst")
        self.assertEqual(result["required_capability"], "capability_gap_analysis")
        self.assertIn("RustOptimizer", result["thought"])
        self.assertIn("handoff_instruction", result)

if __name__ == '__main__':
    unittest.main()
