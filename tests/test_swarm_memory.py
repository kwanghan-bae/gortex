import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch
from gortex.agents.swarm import SwarmAgent
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestSwarmMemoryIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_swarm_memory"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    def test_consensus_to_super_rule_persistence(self, mock_factory):
        """Swarm 합의안이 EvolutionaryMemory에 Super Rule로 저장되는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # 합의안 도출 시뮬레이션 (unified_rule 포함)
        mock_response = {
            "final_decision": "Use strict typing for all new modules.",
            "rationale": "To prevent runtime type errors in the swarm.",
            "unified_rule": {
                "instruction": "ALWAYS_USE_STRICT_TYPING",
                "trigger_patterns": ["typing", "new_module", "class"],
                "severity": 5,
                "category": "coding"
            },
            "action_plan": ["Add type hints", "Enable mypy"]
        }
        mock_backend.generate.return_value = json.dumps(mock_response)
        
        # SwarmAgent 인스턴스 생성 (패치 이후)
        swarm = SwarmAgent()
        history = [{"role": "innovation", "content": "Let's use types!"}]
        
        with patch("gortex.agents.swarm.EvolutionaryMemory") as mock_evo_class:
            mock_evo_instance = mock_evo_class.return_value
            swarm.synthesize_consensus("Strict Typing Debate", history)
            
            # save_rule이 is_super_rule=True로 호출되었는지 확인
            mock_evo_instance.save_rule.assert_called()
            _, kwargs = mock_evo_instance.save_rule.call_args
            self.assertTrue(kwargs.get("is_super_rule"))
            self.assertEqual(kwargs.get("instruction"), "ALWAYS_USE_STRICT_TYPING")

    def test_super_rule_retrieval_priority(self):
        """Super Rule이 일반 규칙보다 우선적으로 반환되는지 테스트"""
        memory = EvolutionaryMemory(base_dir=self.test_dir)
        # 1. 일반 규칙 저장
        memory.save_rule("Normal Rule", ["test"], is_super_rule=False)
        # 2. Super Rule 저장 (동일 패턴)
        memory.save_rule("Priority Super Rule", ["test"], is_super_rule=True)
        
        # 3. 조회 및 순서 확인
        constraints = memory.get_active_constraints("running a test")
        
        self.assertEqual(constraints[0], "Priority Super Rule", "Super Rule이 목록의 최상단에 와야 함")
        self.assertIn("Normal Rule", constraints)

if __name__ == "__main__":
    unittest.main()
