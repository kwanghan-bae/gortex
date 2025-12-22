import unittest
from unittest.mock import MagicMock
from gortex.utils.economy import get_economy_manager
from gortex.agents.analyst.reflection import ReflectionAnalyst
from gortex.core.state import GortexState

class TestSkillTree(unittest.TestCase):
    def setUp(self):
        self.economy = get_economy_manager()
        self.state: GortexState = {
            "agent_economy": {},
            "messages": [],
            "achievements": []
        }

    def test_record_skill_gain(self):
        """분야별 스킬 포인트 획득 테스트"""
        agent = "coder"
        self.economy.record_skill_gain(self.state, agent, "Coding", 50)
        
        skills = self.state["agent_economy"][agent]["skill_points"]
        self.assertEqual(skills["Coding"], 50)
        self.assertEqual(skills["Research"], 0)

    def test_evaluate_work_quality_with_category(self):
        """Analyst의 분야 판별 테스트"""
        analyst = ReflectionAnalyst()
        analyst.backend = MagicMock()
        analyst.backend.generate.return_value = '{"quality_score": 1.5, "category": "Coding", "rationale": "Good code", "feedback": "Nice"}'
        
        evaluation = analyst.evaluate_work_quality("coder", "Implement feature", "code...")
        self.assertEqual(evaluation["category"], "Coding")

if __name__ == '__main__':
    unittest.main()
