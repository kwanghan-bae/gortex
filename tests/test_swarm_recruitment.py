import unittest
from unittest.mock import MagicMock, patch
import asyncio
from gortex.agents.swarm import SwarmAgent
from gortex.core.registry import AgentMetadata

class TestSwarmRecruitment(unittest.TestCase):
    def setUp(self):
        self.swarm = SwarmAgent()
        
        # Mock Registry and Economy
        self.registry_patcher = patch('gortex.agents.swarm.registry') # Note: importing registry inside swarm might need careful patching
        self.mock_registry = self.registry_patcher.start()
        
        # Mock Agents in Registry
        self.agent_coder = AgentMetadata("Coder", "Developer", "Coding expert", ["write_code"], "1.0")
        self.agent_planner = AgentMetadata("Planner", "Architect", "Planning expert", ["plan"], "1.0")
        self.agent_analyst = AgentMetadata("Analyst", "Auditor", "Analysis expert", ["audit"], "1.0")
        
        self.mock_registry.list_agents.return_value = ["coder", "planner", "analyst"]
        self.mock_registry.get_metadata.side_effect = lambda x: {
            "coder": self.agent_coder,
            "planner": self.agent_planner,
            "analyst": self.agent_analyst
        }[x.lower()]

        # Mock Economy State
        self.state = {
            "agent_economy": {
                "coder": {"skill_points": {"Coding": 3000, "Security": 200}},
                "planner": {"skill_points": {"Design": 2500, "Coding": 500}},
                "analyst": {"skill_points": {"Analysis": 2800, "Security": 3000}} # Security Expert
            }
        }

    def tearDown(self):
        self.registry_patcher.stop()

    def test_recruit_experts_for_security_task(self):
        """Swarm should recruit agents with high Security skills for a security task"""
        # We need to implement recruit_experts method first to test it.
        # But in TDD, we write the test expecting the method exists or we define the interface now.
        
        # Define expected behavior:
        # Task: "Fix critical security vulnerability"
        # Expected recruits: Analyst (Security 3000), Coder (Coding 3000 for implementation)
        
        required_skills = ["Security", "Coding"]
        recruits = self.swarm.recruit_experts(self.state, required_skills)
        
        recruit_names = [r["name"].lower() for r in recruits]
        
        self.assertIn("analyst", recruit_names) # Security Expert
        self.assertIn("coder", recruit_names)   # Coding Expert
        
        # Analyst should be recruited specifically for Security
        analyst_recruit = next(r for r in recruits if r["name"].lower() == "analyst")
        self.assertEqual(analyst_recruit["recruited_for"], "Security")

    def test_dynamic_debate_participant_selection(self):
        """run_debate should use recruited experts instead of static personas"""
        # Mock backend generation
        self.swarm.backend.generate = MagicMock(return_value="I propose a fix based on my expertise.")
        
        # We assume run_debate will call recruit_experts internally if configured
        # Or we pass recruits to it. Let's assume we pass a context or it analyzes the topic.
        
        # For this unit test, we'll manually inject recruits if the method supports it, 
        # or mock the internal call.
        
        def mock_recruit_side_effect(state, skills):
            recruits = [
                {"name": "Analyst", "role": "Auditor", "recruited_for": "Security"},
                {"name": "Coder", "role": "Developer", "recruited_for": "Implementation"}
            ]
            self.swarm.participants = recruits
            return recruits

        with patch.object(self.swarm, 'recruit_experts', side_effect=mock_recruit_side_effect) as mock_recruit:
            # Use async run with a new loop for testing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                res = loop.run_until_complete(self.swarm.run_debate("Security Issue", self.state, rounds=1))
            finally:
                loop.close()
            
            # Verify generate was called with prompts reflecting the expert roles
            # We can check the call args of backend.generate
            call_args = self.swarm.backend.generate.call_args_list
            self.assertTrue(len(call_args) >= 2) # At least 2 participants
            
            # Check if prompt contains expert context
            first_call_prompt = call_args[0][0][1][0]['content'] # args -> messages -> first msg -> content
            self.assertIn("Security", first_call_prompt) # Analyst's domain
            self.assertIn("Auditor", first_call_prompt)

if __name__ == '__main__':
    unittest.main()
