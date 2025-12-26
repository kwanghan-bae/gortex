import unittest
import json
import os
import shutil
from unittest.mock import MagicMock
from gortex.utils.economy import get_economy_manager
from gortex.agents.analyst.reflection import ReflectionAnalyst
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.core.state import GortexState

class TestPrecisionFeedback(unittest.TestCase):
    def setUp(self):
        self.economy = get_economy_manager()
        self.state: GortexState = {"agent_economy": {}, "messages": [], "achievements": []}
        self.analyst = ReflectionAnalyst()
        self.analyst.backend = MagicMock()
        
        # 테스트용 메모리 경로 설정
        self.test_mem_dir = "tests/test_memory_feedback"
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)
        self.memory = EvolutionaryMemory(base_dir=self.test_mem_dir)

    def tearDown(self):
        if os.path.exists(self.test_mem_dir):
            shutil.rmtree(self.test_mem_dir)

    def test_weighted_reward_calculation(self):
        """난이도 기반 가중 보상 테스트"""
        # Normal task: quality 1.0, diff 1.0 -> 10 pts
        reward_normal = self.economy.calculate_weighted_reward(quality_score=1.0, difficulty=1.0)
        self.assertEqual(reward_normal, 10)
        
        # Hard & High Quality: quality 1.5, diff 3.0 -> 10 * 1.5 * 3 = 45 pts
        reward_epic = self.economy.calculate_weighted_reward(quality_score=1.5, difficulty=3.0)
        self.assertEqual(reward_epic, 45)

    def test_failure_diagnosis_and_penalty(self):
        """실패 원인 판별 및 페널티 적용 테스트"""
        # 1. 에이전트 실수 시나리오 (Intelligence Issue)
        self.analyst.backend.generate.return_value = json.dumps({
            "root_cause": "INTELLIGENCE", "penalty_factor": 1.0, "explanation": "Logic error"
        })
        diag = self.analyst.analyze_failure_reason("ZeroDivisionError", {})
        penalty = self.economy.record_failure(self.state, "Coder", penalty_factor=diag["penalty_factor"])
        self.assertEqual(penalty, 5) # 기본 페널티 (10 * 0.5 * 1.0)

        # 2. 리소스 부족 시나리오 (Resource Constraint)
        self.analyst.backend.generate.return_value = json.dumps({
            "root_cause": "RESOURCE", "penalty_factor": 0.2, "explanation": "API Quota exceeded"
        })
        diag_res = self.analyst.analyze_failure_reason("QuotaExceeded", {})
        penalty_res = self.economy.record_failure(self.state, "Coder", penalty_factor=diag_res["penalty_factor"])
        self.assertEqual(penalty_res, 1) # 경감된 페널티 (10 * 0.5 * 0.2)

    def test_wisdom_certification_and_prioritization(self):
        """공인 지혜 승격 및 우선순위 정렬 테스트"""
        # 1. 규칙 생성 시 ID가 반환되지 않으므로, 샤드를 비우고 하나씩 생성하며 캡처
        self.memory.shards["general"] = []
        
        self.memory.save_rule("Rule Normal", ["random_pattern"], severity=5)
        normal_id = self.memory.shards["general"][-1]["id"]
        
        self.memory.save_rule("Rule Certified", ["random_pattern"], severity=1)
        certified_id = self.memory.shards["general"][-1]["id"]
        
        # 2. Rule Certified에 대해서만 11회 성공 기록
        for i in range(1, 12):
            self.memory.record_rule_outcome(certified_id, True)
            
        # 3. 상태 검증
        final_shard = self.memory._load_shard("general")
        cert_rule = next(r for r in final_shard if r["id"] == certified_id)
        norm_rule = next(r for r in final_shard if r["id"] == normal_id)
        
        self.assertTrue(cert_rule.get("is_certified"), f"Rule Certified should be certified. Data: {cert_rule}")
        self.assertFalse(norm_rule.get("is_certified"), "Rule Normal should NOT be certified")
        
        # 4. 맥락 조회 시 정렬 확인
        new_mem = EvolutionaryMemory(base_dir=self.test_mem_dir)
        active_rules = new_mem.get_active_constraints("random_pattern match")
        
        self.assertEqual(active_rules[0], "Rule Certified", f"Certified rule should be first. Results: {active_rules}")
        self.assertEqual(active_rules[1], "Rule Normal")

if __name__ == '__main__':
    unittest.main()