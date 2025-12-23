import unittest
import os
import shutil
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.agents.analyst.base import AnalystAgent

class TestMemoryOptimization(unittest.TestCase):
    def setUp(self):
        self.test_mem_dir = "tests/test_memory_gc"
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)
        self.memory = EvolutionaryMemory(base_dir=self.test_mem_dir)
        self.analyst = AnalystAgent()
        self.analyst.memory = self.memory

    def tearDown(self):
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)

    def test_calculate_rule_value_logic(self):
        """규칙 가치 산출 로직 검증"""
        # 1. 고가치 규칙 (Certified)
        cert_rule = {"is_certified": True, "usage_count": 100, "success_count": 95}
        self.assertEqual(self.memory.calculate_rule_value(cert_rule), 100.0)
        
        # 2. 신규 규칙 (2일 전 생성)
        new_date = (datetime.now() - timedelta(days=2)).isoformat()
        new_rule = {"created_at": new_date, "usage_count": 0, "success_count": 0}
        self.assertGreaterEqual(self.memory.calculate_rule_value(new_rule), 90.0)
        
        # 3. 저가치 노후 규칙 (20일 전 생성, 0% 성공률)
        old_date = (datetime.now() - timedelta(days=20)).isoformat()
        bad_rule = {"created_at": old_date, "usage_count": 5, "success_count": 0}
        # (0*70) + (5/10*30) = 15점 -> 30점 미만
        val = self.memory.calculate_rule_value(bad_rule)
        self.assertLess(val, 30.0)

    def test_garbage_collect_knowledge_pruning(self):
        """가치 기반 지식 소거 통합 테스트"""
        old_date = (datetime.now() - timedelta(days=20)).isoformat()
        
        # 1. 보존될 규칙
        self.memory.save_rule("Good instruction", ["pattern1"], category="general")
        
        # 2. 삭제될 규칙 (강제 주입하여 점수 낮춤)
        bad_rule_id = self.memory.save_rule("Bad instruction", ["pattern2"], category="general")
        
        # 메모리 캐시와 파일 모두 업데이트
        for cat in self.memory.shards:
            for r in self.memory.shards[cat]:
                if r["id"] == bad_rule_id:
                    r["created_at"] = old_date
                    r["usage_count"] = 10
                    r["success_count"] = 0
        self.memory._persist_shard("general")
        
        # 3. GC 실행
        report = self.analyst.garbage_collect_knowledge()
        
        # 4. 결과 검증
        self.assertEqual(report["removed"], 1, f"Expected 1 removal, got {report['removed']}. Report: {report}")
        updated_shard = self.memory._load_shard("general")
        ids = [r["id"] for r in updated_shard]
        self.assertNotIn(bad_rule_id, ids)
        self.assertIn("Good instruction", [r["learned_instruction"] for r in updated_shard])

if __name__ == '__main__':
    unittest.main()