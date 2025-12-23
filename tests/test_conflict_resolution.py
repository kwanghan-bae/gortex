import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.agents.swarm import SwarmAgent
from gortex.agents.analyst.base import AnalystAgent

class TestConflictResolution(unittest.TestCase):
    def setUp(self):
        self.test_mem_dir = "tests/test_memory_conflict"
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)
        self.memory = EvolutionaryMemory(base_dir=self.test_mem_dir)
        self.analyst = AnalystAgent()
        self.analyst.memory = self.memory # 테스트용 메모리 주입

    def tearDown(self):
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)

    def test_detect_global_conflicts(self):
        """샤드 간 트리거 중첩 및 갈등 감지 테스트"""
        # 1. 상충되는 규칙들 강제 주입
        self.memory.save_rule("Use snake_case for all functions.", ["function_naming"], category="coding")
        self.memory.save_rule("Use CamelCase for all functions.", ["function_naming"], category="general")
        
        # 2. 갈등 감지 실행
        conflicts = self.memory.detect_global_conflicts()
        
        # 3. 결과 검증
        self.assertTrue(len(conflicts) > 0)
        self.assertEqual(conflicts[0]["type"], "semantic_conflict")
        self.assertIn("function_naming", conflicts[0]["overlap"])

    def test_apply_consensus_and_lineage(self):
        """합의안 적용 및 지식 계보 형성 테스트"""
        rule_a = {"id": "RULE_A", "learned_instruction": "Instruction A", "category": "coding"}
        rule_b = {"id": "RULE_B", "learned_instruction": "Instruction B", "category": "general"}
        
        # 1. Swarm 합의 결과 모킹
        mock_debate_result = {
            "final_decision": "Unified approach chosen.",
            "rationale": "Better consistency",
            "unified_rule": {
                "instruction": "Use PEP8 standard snake_case for Python functions.",
                "trigger_patterns": ["function_naming", "pep8"],
                "severity": 5,
                "category": "coding"
            }
        }
        
        # 2. 합의안 적용
        self.analyst.apply_consensus_result(mock_debate_result, [rule_a, rule_b])
        
        # 3. 통합 규칙 생성 및 계보 확인
        shard = self.memory._load_shard("coding")
        unified_rule = next(r for r in shard if "PEP8" in r["learned_instruction"])
        
        self.assertEqual(unified_rule["severity"], 5)
        self.assertIn("RULE_A", unified_rule["parent_rules"])
        self.assertIn("RULE_B", unified_rule["parent_rules"])
        self.assertTrue(unified_rule.get("is_super_rule"))

if __name__ == '__main__':
    unittest.main()