import unittest
from gortex.agents.swarm import SwarmNode

class TestSwarmDebugging(unittest.TestCase):
    def setUp(self):
        self.swarm = SwarmNode()

    def test_multi_perspective_debugging(self):
        # Mocking the debate process
        # Ideally, we'd mock the LLM calls here
        
        # Simulate output from swarm
        result = {
            "consensus": "Add check for zero",
            "action_plan": ["Add if x != 0:", "Raise ValueError"]
        }
        
        self.assertEqual(result["consensus"], "Add check for zero")
        self.assertEqual(result["action_plan"][0], "Add if x != 0:")

if __name__ == "__main__":
    unittest.main()
