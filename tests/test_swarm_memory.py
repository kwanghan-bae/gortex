import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch
from gortex.agents.swarm import SwarmAgent
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestSwarmMemoryIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_memory_swarm"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # EvolutionaryMemory가 base_dir를 인자로 받지만, 
        # SwarmAgent 내부에서 기본 생성자를 사용하므로 patch가 필요할 수 있음.
        # 하지만 여기서는 save_rule이 호출되는지만 확인하면 됨.
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("logs/debates"):
             # Clean up debate logs if needed
             pass

    @patch('gortex.core.evolutionary_memory.EvolutionaryMemory.save_rule')
    @patch('gortex.core.llm.factory.LLMFactory.get_default_backend')
    def test_synthesize_consensus_saves_super_rule(self, mock_backend_factory, mock_save_rule):
        # 1. Mock LLM Setup
        mock_backend = MagicMock()
        mock_backend.supports_structured_output.return_value = False
        # 합의안에 unified_rule이 포함된 가짜 응답
        mock_backend.generate.return_value = json.dumps({
            "final_decision": "Implement X",
            "rationale": "Better performance",
            "unified_rule": {
                "instruction": "Authoritative Rule from Swarm",
                "trigger_patterns": ["swarm", "rule"],
                "severity": 4,
                "category": "coding"
            },
            "action_plan": ["Step 1"]
        })
        mock_backend_factory.return_value = mock_backend
        
        # 2. SwarmAgent 실행
        agent = SwarmAgent()
        topic = "Test Topic"
        history = [{"role": "innovation", "content": "Let's do X", "round": 1}]
        
        consensus = agent.synthesize_consensus(topic, history)
        
        # 3. 검증
        self.assertEqual(consensus["final_decision"], "Implement X")
        
        # save_rule이 호출되었는지 확인
        mock_save_rule.assert_called_once()
        args, kwargs = mock_save_rule.call_args
        self.assertEqual(kwargs["instruction"], "Authoritative Rule from Swarm")
        self.assertTrue(kwargs["is_super_rule"])
        self.assertEqual(kwargs["source_session"], "swarm_debate")

if __name__ == "__main__":
    unittest.main()
