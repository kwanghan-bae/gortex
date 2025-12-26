import unittest
from unittest.mock import patch
from gortex.agents.manager import ManagerAgent
from gortex.core.registry import AgentMetadata
from gortex.core.engine import GortexEngine

class TestIntelligentRouting(unittest.TestCase):
    def setUp(self):
        self.manager = ManagerAgent()
        self.engine = GortexEngine()
        
        # Mock Registry with hypothetical agents
        self.registry_patcher = patch('gortex.agents.manager.registry')
        self.mock_registry = self.registry_patcher.start()
        
        # Setup Agents
        # Agent A: Generalist (High Rep, Low Coding)
        self.agent_a_meta = AgentMetadata("Generalist", "Worker", "Good at general tasks", ["general_tool"], "1.0")
        # Agent B: Specialist (Low Rep, High Coding)
        self.agent_b_meta = AgentMetadata("Specialist", "Coder", "Expert at coding", ["coding_tool"], "1.0")
        
        self.mock_registry.list_agents.return_value = ["generalist", "specialist"]
        self.mock_registry.get_metadata.side_effect = lambda x: self.agent_a_meta if x == "generalist" else self.agent_b_meta
        
        # Mock Economy State
        self.state = {
            "messages": [("user", "Fix this bug")],
            "agent_economy": {
                "generalist": {
                    "points": 2000, # High Rep
                    "skill_points": {"Coding": 100, "General": 2000}
                },
                "specialist": {
                    "points": 500,  # Low Rep
                    "skill_points": {"Coding": 3000, "General": 100} # Master Coder
                }
            },
            "agent_energy": 100
        }

    def tearDown(self):
        self.registry_patcher.stop()

    def test_routing_by_skill_mastery(self):
        """Manager should select the agent with higher specific skill for specialized tasks"""
        # Scenario: Coding task needed
        # We need to mock the LLM response to simulate Manager's decision process
        with patch.object(self.manager.backend, 'generate') as mock_gen:
            # Manager determines 'coding_tool' is needed
            mock_gen.return_value = '{"thought": "Need to fix code", "required_capability": "coding_tool", "response_to_user": "Fixing..."}'
            
            # Registry should return both candidates for the tool (simulated)
            self.mock_registry.get_agents_by_tool.return_value = ["generalist", "specialist"]
            
            # Run Manager logic (we need to access the sorting logic inside run, 
            # but run is complex. Let's test the helper method if we refactor, 
            # or mock registry to verify sort key usage.)
            
            # Since we haven't refactored yet, we will integration-test the 'run' method
            # but we need to inject the logic first. 
            # Current implementation sorts by 'points'. 
            # Test expects 'specialist' to be selected because of 'Coding' skill mapping.
            
            res = self.manager.run(self.state)
            
            # BEFORE FIX: likely 'generalist' (2000 pts > 500 pts)
            # AFTER FIX: 'specialist' (Coding 3000 > 100)
            self.assertEqual(res["next_node"], "specialist")

    def test_model_selection_by_skill(self):
        """Engine should assign high-tier model for Master-level skills"""
        # Specialist (Coding Master) should get Pro model for high risk coding task
        self.state["risk_score"] = 0.9
        model = self.engine.select_optimal_model(self.state, "specialist")
        
        # Assuming Master skill (3000) overrides or complements total points logic
        # Current logic: risk > 0.8 and points > 1000 -> Pro.
        # Specialist has 500 points but 3000 skill points. 
        # We want engine to consider skill points too.
        self.assertEqual(model, "gemini-1.5-pro")

if __name__ == '__main__':
    unittest.main()
