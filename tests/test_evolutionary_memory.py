import unittest
import os
import shutil
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestEvolutionaryMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_memory"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.memory = EvolutionaryMemory(base_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """초기화 시 샤드 딕셔너리가 생성되는지 확인"""
        self.assertIn("coding", self.memory.shards)
        self.assertIn("general", self.memory.shards)

    def test_save_and_load_rule(self):
        """규칙이 정상적으로 저장되고 로드되는지 확인"""
        instruction = "Always use Python 3.10+"
        patterns = ["python", "coding style"]
        rule_id = self.memory.save_rule(instruction, patterns, category="coding")
        
        shard = self.memory.shards["coding"]
        self.assertEqual(len(shard), 1)
        self.assertEqual(shard[0]["id"], rule_id)
        self.assertEqual(shard[0]["learned_instruction"], instruction)
        
        # 파일에서 다시 로드 확인
        new_memory = EvolutionaryMemory(base_dir=self.test_dir)
        new_shard = new_memory.shards["coding"]
        self.assertEqual(len(new_shard), 1)
        self.assertEqual(new_shard[0]["id"], rule_id)

    def test_duplicate_rule_reinforcement(self):
        """동일한 지침인 경우 기존 규칙이 강화되는지 확인"""
        instruction = "Duplicate Test"
        self.memory.save_rule(instruction, ["pattern1"], category="general")
        
        # 동일 지침으로 재저장
        rule_id = self.memory.save_rule(instruction, ["pattern2"], category="general")
        
        shard = self.memory.shards["general"]
        self.assertEqual(len(shard), 1)
        self.assertEqual(shard[0]["id"], rule_id)
        self.assertIn("pattern2", shard[0]["trigger_patterns"])
        self.assertEqual(shard[0]["reinforcement_count"], 2)

    def test_get_active_constraints(self):
        """컨텍스트에 맞는 활성 제약 조건만 반환하는지 확인"""
        self.memory.save_rule("Python Rule", ["python"], category="coding")
        self.memory.save_rule("JS Rule", ["javascript"], category="coding")
        
        # 'python' 키워드가 있으므로 coding 샤드 검색 -> Python Rule 매칭
        active = self.memory.get_active_constraints("I am writing python code")
        self.assertIn("Python Rule", active)
        self.assertNotIn("JS Rule", active)

    def test_record_rule_outcome(self):
        """규칙 성과 기록 및 자동 승격(Certification) 테스트"""
        rule_id = self.memory.save_rule("Test Rule", ["test"], category="general")
        
        # 10회 성공 시뮬레이션
        for _ in range(10):
            self.memory.record_rule_outcome(rule_id, success=True)
            
        shard = self.memory.shards["general"]
        rule = shard[0]
        self.assertEqual(rule["usage_count"], 10)
        self.assertEqual(rule["success_count"], 10)
        self.assertTrue(rule["is_certified"], "10회 성공 시 공인 지혜로 승격되어야 함")

    def test_prune_memory(self):
        """메모리 가지치기(LLM 호출) 테스트 - Mocking"""
        self.memory.save_rule("Rule 1", ["p1"], category="general")
        self.memory.save_rule("Rule 2", ["p2"], category="general")
        
        with patch('gortex.core.llm.factory.LLMFactory.get_default_backend') as mock_factory:
            mock_backend = MagicMock()
            # LLM이 통합된 JSON을 반환한다고 가정
            mock_backend.generate.return_value = json.dumps([
                {"instruction": "Merged Rule", "trigger_patterns": ["p1", "p2"], "severity": 3}
            ])
            mock_factory.return_value = mock_backend
            
            self.memory.prune_memory()
            
            shard = self.memory.shards["general"]
            self.assertEqual(len(shard), 1)
            self.assertEqual(shard[0]["learned_instruction"], "Merged Rule")

    def test_super_rule_priority_and_survival(self):
        """Super Rule의 우선순위 정렬 및 생존 가치(Survival Value) 보존 테스트"""
        # 1. 일반 규칙과 Super Rule 저장
        self.memory.save_rule("Normal Rule", ["test"], category="general", is_super_rule=False)
        self.memory.save_rule("Super Rule", ["test"], category="general", is_super_rule=True)
        
        # 2. 정렬 순서 확인 (Super Rule이 먼저 나와야 함)
        active = self.memory.get_active_constraints("running test context")
        self.assertEqual(active[0], "Super Rule")
        self.assertEqual(active[1], "Normal Rule")
        
        # 3. 생존 가치 확인 (Super Rule은 항상 100.0)
        shard = self.memory.shards["general"]
        super_rule = next(r for r in shard if r["learned_instruction"] == "Super Rule")
        normal_rule = next(r for r in shard if r["learned_instruction"] == "Normal Rule")
        
        self.assertEqual(self.memory.calculate_rule_value(super_rule), 100.0)
        
        # Normal Rule은 생성한지 얼마 안됐으므로 90.0 (기본 로직)
        self.assertEqual(self.memory.calculate_rule_value(normal_rule), 90.0)

if __name__ == '__main__':
    unittest.main()