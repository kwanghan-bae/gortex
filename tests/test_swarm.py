import unittest
import asyncio
from unittest.mock import MagicMock, patch
from gortex.agents.swarm import SwarmAgent, swarm_node_async

class TestGortexSwarm(unittest.TestCase):
    def setUp(self):
        self.agent = SwarmAgent()
        self.agent.backend = MagicMock()
        self.agent.prompts = MagicMock()
        self.agent.prompts.get.return_value = "Persona Prompt"

    def test_synthesize_consensus(self):
        """합의 도출 로직 테스트"""
        self.agent.backend.supports_structured_output.return_value = False
        self.agent.backend.generate.return_value = '''
        {
            "final_decision": "Consensus",
            "rationale": "Reason",
            "action_plan": ["Step 1"]
        }
        '''
        history = [{"role": "innovation", "content": "A"}, {"role": "stability", "content": "B"}]
        result = self.agent.synthesize_consensus("Topic", history)
        
        self.assertEqual(result["final_decision"], "Consensus")
        self.assertIn("Step 1", result["action_plan"])

    @patch('gortex.agents.swarm.SwarmAgent')
    def test_swarm_node_async(self, MockSwarmAgent):
        """Swarm 노드 실행 흐름 테스트"""
        
        async def run_test():
            mock_instance = MockSwarmAgent.return_value
            # Inside the loop, we can create a Future that belongs to it
            f = asyncio.Future()
            f.set_result({"final_decision": "Done", "rationale": "Test", "action_plan": []})
            mock_instance.run_debate.return_value = f
            
            state = {"current_issue": "Test Debate"}
            return await swarm_node_async(state)

        result = asyncio.run(run_test())
        
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("Consensus Reached", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()