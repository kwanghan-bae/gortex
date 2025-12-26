import unittest
from unittest.mock import patch
from gortex.agents.analyst import AnalystAgent, analyst_node

class TestGortexAnalystIntegrated(unittest.TestCase):
    def setUp(self):
        self.agent = AnalystAgent()
        self.state = {
            "messages": [("ai", "Code completed.")],
            "next_node": "analyst",
            "active_constraints": ["Rule 1"],
            "agent_economy": {},
            "token_credits": {}
        }

    @patch('gortex.agents.analyst.reflection.ReflectionAnalyst.validate_constraints')
    def test_analyst_node_validation_flow(self, mock_val):
        """Analyst 노드가 Coder의 결과를 성공적으로 검증하고 보상을 지급하는지 테스트"""
        mock_val.return_value = {"is_valid": True}
        
        result = analyst_node(self.state)
        
        # 검증 통과 후 manager로 라우팅 확인
        self.assertEqual(result["next_node"], "manager")
        # 경제 시스템 보상 반영 확인
        self.assertIn("coder", result["agent_economy"])
        self.assertEqual(result["token_credits"]["coder"], 110.0)

    @patch('gortex.agents.analyst.reflection.ReflectionAnalyst.synthesize_consensus')
    def test_analyst_node_consensus_flow(self, mock_syn):
        """토론 데이터가 있을 때 합의 도출 로직이 작동하는지 테스트"""
        mock_syn.return_value = {"final_decision": "Choose Path A", "rationale": "Reason X"}
        self.state["debate_context"] = [{"persona": "Innovation", "report": "..."}]
        
        result = analyst_node(self.state)
        
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("Choose Path A", result["messages"][0][1])
        # 합의 이력 기록 확인
        self.assertEqual(len(result["consensus_history"]), 1)

    def test_analyst_node_data_trigger(self):
        """메시지에 데이터 파일명이 포함된 경우 분석 로직이 트리거되는지 테스트"""
        self.state["messages"] = [("user", "Analyze data.csv")]
        self.state["next_node"] = "manager" # 일반 대화 상태
        
        result = analyst_node(self.state)
        
        self.assertIn("data.csv", result["messages"][0][1])
        self.assertEqual(result["next_node"], "manager")

if __name__ == '__main__':
    unittest.main()
