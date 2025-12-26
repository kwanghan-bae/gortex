import unittest
from gortex.core.state import GortexState

class TestGortexState(unittest.TestCase):
    def test_state_structure(self):
        # TypedDict doesn't allow instantiation like a class, but we can verify it behaves like a dict
        state: GortexState = {
            "messages": [],
            "plan": [],
            "current_step": 0,
            "working_dir": ".",
            "file_cache": {},
            "next_node": "manager",
            "assigned_model": "gemini-1.5-flash",
            "coder_iteration": 0,
            "history_summary": "",
            "active_constraints": [],
            "agent_energy": 100,
            "last_efficiency": 0.0,
            "efficiency_history": [],
            "agent_economy": {}
        }
        self.assertEqual(state["current_step"], 0)
        self.assertIsInstance(state["messages"], list)

if __name__ == "__main__":
    unittest.main()
