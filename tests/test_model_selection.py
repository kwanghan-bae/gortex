import unittest
import os
import shutil
from gortex.core.engine import GortexEngine
from gortex.core.state import GortexState
from gortex.utils.token_counter import DailyTokenTracker

class TestModelSelection(unittest.TestCase):
    def setUp(self):
        self.test_log_dir = "tests/test_logs_selection"
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        os.makedirs(self.test_log_dir, exist_ok=True)
        
        self.budget_path = os.path.join(self.test_log_dir, "token_budget.json")
        self.engine = GortexEngine()
        self.engine.tracker = DailyTokenTracker(storage_path=self.budget_path)

    def tearDown(self):
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

    def test_downgrade_on_budget_critical(self):
        """예산 고갈 시 Ollama로 강제 다운그레이드 테스트"""
        # 1. 예산 상태 90% 소모로 조작
        self.engine.tracker.data["total_tokens"] = 450000 # Limit is 500000
        
        state: GortexState = {
            "risk_score": 0.9, # 고위험 작업임에도
            "agent_economy": {"Planner": {"points": 2000}} # 엘리트 에이전트임에도
        }
        
        model = self.engine.select_optimal_model(state, "Planner")
        self.assertEqual(model, "ollama/llama3", "Should downgrade to Ollama due to budget")

    def test_pro_model_for_elite_agent_and_high_risk(self):
        """엘리트 에이전트와 고위험 작업에 Pro 모델 할당 테스트"""
        # 1. 쾌적한 예산 상태 (0% 소모)
        self.engine.tracker.data["total_tokens"] = 0
        
        state: GortexState = {
            "risk_score": 0.9, 
            "agent_economy": {"Coder": {"points": 1500}} 
        }
        
        model = self.engine.select_optimal_model(state, "Coder")
        self.assertEqual(model, "gemini-1.5-pro")

    def test_flash_model_for_normal_work(self):
        """일반적인 전문 작업에 Flash 모델 할당 테스트"""
        self.engine.tracker.data["total_tokens"] = 0
        
        state: GortexState = {
            "risk_score": 0.5, 
            "agent_economy": {"Analyst": {"points": 600}} 
        }
        
        model = self.engine.select_optimal_model(state, "Analyst")
        self.assertEqual(model, "gemini-2.0-flash")

if __name__ == '__main__':
    unittest.main()