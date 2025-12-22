import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst.base import AnalystAgent
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestMemoryOptimization(unittest.TestCase):
    def setUp(self):
        self.memory_path = "test_experience_opt.json"
        self.memory = EvolutionaryMemory(file_path=self.memory_path)
        self.agent = AnalystAgent()
        self.agent.memory = self.memory
        self.agent.backend = MagicMock()

    def tearDown(self):
        if os.path.exists(self.memory_path): os.remove(self.memory_path)

    def test_record_rule_outcome(self):
        """성공/실패 결과 기록 기능 테스트"""
        self.memory.save_rule("Test Rule", ["pattern"])
        rule_id = self.memory.memory[0]["id"]
        
        self.memory.record_rule_outcome(rule_id, success=True)
        self.assertEqual(self.memory.memory[0]["success_count"], 1)
        self.assertEqual(self.memory.memory[0]["usage_count"], 1)

    def test_optimize_knowledge_base_merging(self):
        """유사 규칙 병합 및 최적화 테스트"""
        # 1. 유사한 규칙 5개 생성 (최적화 트리거 최소 조건)
        for i in range(5):
            self.memory.save_rule(f"Strict typing in python {i}", ["python", "typing"])
            
        # 2. LLM 응답 시뮬레이션: 5개의 규칙을 1개로 통합
        mock_merge_res = [
            {
                "instruction": "Always use strict typing in Python projects.",
                "trigger_patterns": ["python", "typing", "type hint"],
                "severity": 4
            }
        ]
        self.agent.backend.generate.return_value = json.dumps(mock_merge_res)
        
        # 3. 최적화 실행
        result = self.agent.optimize_knowledge_base()
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.memory.memory), 1) # 1개로 압축됨
        self.assertTrue(self.memory.memory[0]["is_super_rule"])
        self.assertIn("Always use strict typing", self.memory.memory[0]["learned_instruction"])

    def test_optimize_low_performance_removal(self):
        """성과 저조 규칙 삭제 테스트"""
        # 1. 충분한 수의 규칙 생성
        for i in range(4): self.memory.save_rule(f"Good rule {i}", ["ok"])
        
        self.memory.save_rule("Bad rule", ["fail"])
        bad_rule_id = self.memory.memory[-1]["id"]
        
        # 2. 성과 저조 시뮬레이션 (5회 사용 중 0회 성공 = 0%)
        for _ in range(5):
            self.memory.record_rule_outcome(bad_rule_id, success=False)
            
        # 3. LLM은 그대로 유지한다고 가정해도, 수치 필터링에서 걸러져야 함
        self.agent.backend.generate.return_value = "[]" # 병합 결과 없음
        
        result = self.agent.optimize_knowledge_base()
        
        self.assertEqual(result["removed"], 1)
        # 삭제 후 병합 로직(LLM)이 빈 리스트를 줬으므로 최종 0개 (테스트 설정상)
        self.assertEqual(len(self.memory.memory), 0)

if __name__ == '__main__':
    unittest.main()
