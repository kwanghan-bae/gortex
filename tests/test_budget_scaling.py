import unittest
from gortex.core.llm.factory import LLMFactory

class TestBudgetScaling(unittest.TestCase):
    def test_model_downgrade_on_high_usage(self):
        """예산 소진 상황에서 모델 하향 조정 테스트"""
        grade = "Diamond"
        budget = 1.0
        
        # 1. 예산 넉넉할 때 (0%) -> Pro/Flash 최고 성능
        model_normal = LLMFactory.get_model_for_grade(grade, daily_cost=0.0, budget_limit=budget)
        self.assertEqual(model_normal, "gemini-2.0-flash")
        
        # 2. 예산 75% 소진 -> 한 단계 하향 (Flash로 추정되나 여기서는 gemini-1.5-flash로 매핑됨)
        model_warn = LLMFactory.get_model_for_grade(grade, daily_cost=0.75, budget_limit=budget)
        self.assertEqual(model_warn, "gemini-1.5-flash")
        
        # 3. 예산 95% 소진 -> 로컬 모델로 강제 전환
        model_critical = LLMFactory.get_model_for_grade(grade, daily_cost=0.95, budget_limit=budget)
        self.assertEqual(model_critical, "ollama/llama3")

if __name__ == '__main__':
    unittest.main()
