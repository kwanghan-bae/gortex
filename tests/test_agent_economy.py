import unittest
from unittest.mock import MagicMock, patch
from gortex.utils.economy import get_economy_manager
from gortex.agents.analyst.reflection import ReflectionAnalyst
from gortex.core.state import GortexState

class TestAgentEconomy(unittest.TestCase):
    def setUp(self):
        self.economy = get_economy_manager()
        self.state: GortexState = {
            "agent_economy": {},
            "messages": []
        }

    def test_record_success_increases_points(self):
        """성공 시 포인트가 증가하는지 테스트"""
        agent = "coder"
        self.economy.record_success(self.state, agent, quality_score=1.5)
        
        points = self.state["agent_economy"][agent]["points"]
        # Base reward 10 * 1.5 = 15. Initial 100 + 15 = 115
        self.assertEqual(points, 115)
        self.assertEqual(self.state["agent_economy"][agent]["level"], "Bronze")

    def test_record_failure_decreases_points(self):
        """실패 시 포인트가 차감되는지 테스트"""
        agent = "researcher"
        self.economy.record_failure(self.state, agent, penalty_factor=2.0)
        
        points = self.state["agent_economy"][agent]["points"]
        # Base penalty 10*0.5 * 2.0 = 10. Initial 100 - 10 = 90
        self.assertEqual(points, 90)

    def test_evaluate_work_quality(self):
        """Analyst의 작업 품질 평가 로직 테스트"""
        analyst = ReflectionAnalyst()
        analyst.backend = MagicMock()
        analyst.backend.generate.return_value = '{"quality_score": 1.8, "rationale": "Perfect implementation", "feedback": "Good job"}'
        
        evaluation = analyst.evaluate_work_quality("coder", "Add feature X", "Feature X added with tests")
        
        self.assertEqual(evaluation["quality_score"], 1.8)
        self.assertEqual(evaluation["rationale"], "Perfect implementation")

    def test_level_up(self):
        """포인트에 따른 레벨업 테스트"""
        agent = "planner"
        # 초기화 메서드 사용으로 필드 누락 방지
        self.economy.initialize_agent(self.state["agent_economy"], agent)
        self.state["agent_economy"][agent]["points"] = 1995
        self.state["agent_economy"][agent]["level"] = "Gold"
        
        self.economy.record_success(self.state, agent, quality_score=1.0)
        self.assertEqual(self.state["agent_economy"][agent]["level"], "Diamond")

if __name__ == '__main__':
    unittest.main()
