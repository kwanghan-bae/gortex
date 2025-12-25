import unittest
import json
from unittest.mock import MagicMock
from gortex.agents.planner import PlannerAgent
from gortex.core.state import GortexState

class TestTaskPrioritization(unittest.TestCase):
    def setUp(self):
        self.planner = PlannerAgent()
        self.planner.backend = MagicMock()
        
        self.state: GortexState = {
            "messages": [("user", "System maintenance required.")],
            "working_dir": ".",
            "agent_energy": 100,
            "assigned_model": "flash"
        }

    def test_plan_sorting_by_priority(self):
        """작업 우선순위에 따른 계획 재배열 테스트"""
        # Mock LLM response with mixed priorities
        mock_steps = {
            "thought_process": "Planning tasks...",
            "goal": "Maintenance",
            "steps": [
                {"id": 1, "action": "update_docs", "category": "Doc", "priority_score": 3},
                {"id": 2, "action": "fix_security_vulnerability", "category": "Security", "priority_score": 10},
                {"id": 3, "action": "refactor_code", "category": "Refactor", "priority_score": 7}
            ],
            "handoff_instruction": "Proceed to Coder"
        }
        self.planner.backend.generate.return_value = json.dumps(mock_steps)
        
        result = self.planner.run(self.state)
        plan = [json.loads(s) for r in [result] for s in r["plan"]]
        
        # Security(10) -> Refactor(7) -> Doc(3) 순서여야 함
        self.assertEqual(plan[0]["category"], "Security")
        self.assertEqual(plan[1]["category"], "Refactor")
        self.assertEqual(plan[2]["category"], "Doc")

    def test_pruning_under_low_energy(self):
        """저에너지 상태에서 가치가 낮은 작업 제거 테스트"""
        self.state["agent_energy"] = 20 # Critical energy
        
        mock_steps = {
            "thought_process": "Planning tasks...",
            "goal": "Maintenance",
            "steps": [
                {"id": 1, "action": "fix_critical_bug", "category": "Fix", "priority_score": 9},
                {"id": 2, "action": "minor_doc_fix", "category": "Doc", "priority_score": 2}
            ],
            "handoff_instruction": "Proceed to Coder"
        }
        self.planner.backend.generate.return_value = json.dumps(mock_steps)
        
        result = self.planner.run(self.state)
        plan = [json.loads(s) for s in result["plan"]]
        
        # 'Doc' 카테고리의 낮은 우선순위 작업은 제거되어야 함
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["category"], "Fix")

if __name__ == '__main__':
    unittest.main()