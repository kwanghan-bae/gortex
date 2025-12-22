import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.planner import planner_node
from gortex.core.state import GortexState

class TestTaskPrioritization(unittest.TestCase):
    @patch("gortex.agents.planner.LLMFactory.get_default_backend")
    @patch("gortex.agents.planner.SynapticIndexer")
    @patch("gortex.agents.planner.EfficiencyMonitor")
    def test_plan_pruning_on_low_energy(self, mock_monitor, mock_indexer, mock_factory):
        """저에너지 상황에서 중요하지 않은 작업이 제거되는지 테스트"""
        # 1. Setup Mock Backend
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # 2. Mock LLM Response (3 steps: 2 essential, 1 optional)
        plan_response = {
            "thought_process": "Planning with pruning in mind",
            "impact_analysis": {"target": "file.py", "direct": [], "indirect": [], "risk_level": "low"},
            "internal_critique": "None",
            "thought_tree": [],
            "goal": "Test Goal",
            "steps": [
                {"id": 1, "action": "Essential Action 1", "target": "a.py", "reason": "R1", "priority": 10, "is_essential": True},
                {"id": 2, "action": "Optional Action 2", "target": "b.py", "reason": "R2", "priority": 3, "is_essential": False},
                {"id": 3, "action": "Essential Action 3", "target": "c.py", "reason": "R3", "priority": 9, "is_essential": True}
            ]
        }
        mock_backend.generate.return_value = json.dumps(plan_response)
        mock_backend.supports_structured_output.return_value = False
        
        # 3. Setup State with LOW ENERGY (20)
        state: GortexState = {
            "messages": [("user", "do something")],
            "agent_energy": 20,
            "assigned_model": "gemini-1.5-flash",
            "working_dir": "."
        }
        
        # 4. Run Planner
        result = planner_node(state)
        
        # 5. Verify: Step 2 should be pruned
        plan = result["plan"]
        self.assertEqual(len(plan), 2)
        self.assertIn("Essential Action 1", plan[0])
        self.assertIn("Essential Action 3", plan[1])
        self.assertNotIn("Optional Action 2", str(plan))
        self.assertIn("생략되었습니다", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()
