import unittest
import os
import json
import shutil
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestMemorySharding(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_memory_shards"
        self.legacy_file = "experience.json"
        
        # 1. 가상의 레거시 데이터 생성
        legacy_data = [
            {"learned_instruction": "Always use type hints in Python", "trigger_patterns": ["python"], "severity": 4},
            {"learned_instruction": "Check latest AI trends weekly", "trigger_patterns": ["trend"], "severity": 3},
            {"learned_instruction": "System should be polite", "trigger_patterns": ["hello"], "severity": 1}
        ]
        with open(self.legacy_file, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        # 2. 메모리 초기화 (마이그레이션 트리거)
        self.memory = EvolutionaryMemory(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.legacy_file):
            os.remove(self.legacy_file)
        if os.path.exists(self.legacy_file + ".migrated.bak"):
            os.remove(self.legacy_file + ".migrated.bak")

    def test_migration_and_sharding(self):
        """레거시 데이터가 샤드로 분리되었는지 테스트"""
        # coding 샤드에 타입 힌트 지침이 있어야 함
        coding_shard_path = os.path.join(self.test_dir, "coding_shard.json")
        self.assertTrue(os.path.exists(coding_shard_path))
        
        with open(coding_shard_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertTrue(any("type hints" in r["learned_instruction"] for r in data))

    def test_contextual_shard_picking(self):
        """맥락에 따라 필요한 샤드만 조회하는지 테스트"""
        # 'python' 관련 맥락 -> coding 샤드 조회 기대
        rules = self.memory.get_active_constraints("Write some python code")
        self.assertTrue(any("type hints" in r for r in rules))
        
        # 'hello' 관련 맥락 -> general 샤드 조회 기대
        rules_gen = self.memory.get_active_constraints("Say hello to user")
        self.assertTrue(any("polite" in r for r in rules_gen))

    def test_save_rule_auto_classification(self):
        """새로운 규칙 저장 시 자동 분류 테스트"""
        self.memory.save_rule("Optimize CSS layout", ["css", "style"])
        
        # 'design' 샤드에 저장되어야 함
        design_shard_path = os.path.join(self.test_dir, "design_shard.json")
        self.assertTrue(os.path.exists(design_shard_path))
        
        with open(design_shard_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data[0]["category"], "design")

if __name__ == '__main__':
    unittest.main()
