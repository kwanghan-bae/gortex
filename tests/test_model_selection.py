import unittest
from unittest.mock import MagicMock, patch
from gortex.agents.manager import manager_node
from gortex.core.llm.factory import LLMFactory
from gortex.core.state import GortexState

class TestMultiModelSelection(unittest.TestCase):
    def test_factory_grade_mapping(self):
        """등급별 모델 매핑 테스트"""
        self.assertEqual(LLMFactory.get_model_for_grade("Diamond"), "gemini-2.0-flash")
        self.assertEqual(LLMFactory.get_model_for_grade("Bronze"), "gemini-2.5-flash-lite")
        self.assertEqual(LLMFactory.get_model_for_grade("Newbie"), "ollama/llama3")

    @patch("gortex.agents.manager.LLMFactory.get_default_backend")
    @patch("gortex.agents.manager.SemanticLogSearch")
    @patch("gortex.agents.manager.SynapticTranslator")
    @patch("gortex.agents.manager.LongTermMemory")
    @patch("gortex.agents.manager.EfficiencyMonitor")
    def test_manager_assigns_pro_for_diamond(self, mock_monitor, mock_ltm, mock_trans, mock_log, mock_factory):
        """다이아몬드 등급 에이전트에게 고성능 모델이 할당되는지 테스트"""
        # 1. Setup Mock
        mock_monitor.return_value.calculate_model_scores.return_value = {}
        mock_monitor.return_value.get_best_model_for_task.return_value = None
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        mock_backend.generate.return_value = '{"thought": "test", "internal_critique": "none", "thought_tree": [], "next_node": "coder", "assigned_persona": "innovation"}'
        mock_backend.supports_structured_output.return_value = False
        
        # 2. Setup State with Diamond Coder
        state: GortexState = {
            "messages": [("user", "make something great")],
            "agent_economy": {
                "coder": {"level": "Diamond", "points": 2500}
            },
            "agent_energy": 100,
            "working_dir": "."
        }
        
        # 3. Run Manager
        result = manager_node(state)
        
        # 4. Verify: Assigned model for coder should be gemini-2.0-flash
        self.assertEqual(result["assigned_model"], "gemini-2.0-flash")

    @patch("gortex.agents.manager.LLMFactory.get_default_backend")
    @patch("gortex.agents.manager.SemanticLogSearch")
    @patch("gortex.agents.manager.SynapticTranslator")
    @patch("gortex.agents.manager.LongTermMemory")
    @patch("gortex.agents.manager.EfficiencyMonitor")
    def test_manager_assigns_lite_for_bronze(self, mock_monitor, mock_ltm, mock_trans, mock_log, mock_factory):
        """브론즈 등급 에이전트에게 경량 모델이 할당되는지 테스트"""
        mock_monitor.return_value.calculate_model_scores.return_value = {}
        mock_monitor.return_value.get_best_model_for_task.return_value = None
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        mock_backend.generate.return_value = '{"thought": "test", "internal_critique": "none", "thought_tree": [], "next_node": "planner", "assigned_persona": "standard"}'
        mock_backend.supports_structured_output.return_value = False
        
        state: GortexState = {
            "messages": [("user", "low priority task")],
            "agent_economy": {
                "planner": {"level": "Bronze", "points": 150}
            },
            "agent_energy": 100,
            "working_dir": "."
        }
        
        result = manager_node(state)
        self.assertEqual(result["assigned_model"], "gemini-2.5-flash-lite")

if __name__ == '__main__':
    unittest.main()
