import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.agents.analyst.base import AnalystAgent

class TestConflictResolution(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_memory_conflicts"
        os.makedirs(self.test_dir, exist_ok=True)
        self.memory = EvolutionaryMemory(base_dir=self.test_dir)
        self.analyst = AnalystAgent()
        self.analyst.memory = self.memory
        self.analyst.backend = MagicMock()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("experience.json"): os.remove("experience.json")

    def test_cross_shard_conflict_detection(self):
        """서로 다른 샤드 간의 충돌 감지 테스트"""
        # 1. coding 샤드에 규칙 추가
        self.memory.save_rule("Use tabs for indentation", ["formatting"], category="coding")
        # 2. general 샤드에 상충되는 규칙 추가
        self.memory.save_rule("Use spaces for indentation", ["formatting"], category="general")
        
        # 3. 감지 실행
        conflicts = self.memory.detect_cross_shard_conflicts()
        
        self.assertGreater(len(conflicts), 0)
        self.assertEqual(conflicts[0]["type"], "trigger_overlap")
        self.assertIn("formatting", conflicts[0]["overlap"])

    def test_auto_resolution_by_performance(self):
        """성과 지표에 따른 자동 갈등 해결 테스트"""
        # Rule A: 초보자 규칙 (성공 0)
        rule_a = {"id": "A", "learned_instruction": "A", "success_count": 0, "reinforcement_count": 1, "category": "coding"}
        # Rule B: 숙련된 규칙 (성공 10)
        rule_b = {"id": "B", "learned_instruction": "B", "success_count": 10, "reinforcement_count": 2, "category": "general"}
        
        conflict = {"rule_a": rule_a, "rule_b": rule_b}
        
        result = self.analyst.resolve_knowledge_conflict(conflict)
        
        # 성과가 월등한 rule_b가 선택되어야 함
        self.assertEqual(result["id"], "B")

    def test_semantic_synthesis_resolution(self):
        """LLM을 통한 의미론적 통합 해결 테스트"""
        rule_a = {"id": "A", "learned_instruction": "Python 3.8 style", "success_count": 1, "category": "coding", "trigger_patterns": ["py"]}
        rule_b = {"id": "B", "learned_instruction": "Python 3.10 style", "success_count": 1, "category": "coding", "trigger_patterns": ["py"]}
        
        conflict = {"rule_a": rule_a, "rule_b": rule_b}
        
        # LLM 응답 모킹
        mock_res = {"instruction": "Use latest Python features", "target_category": "coding", "trigger_patterns": ["py"], "severity": 5}
        self.analyst.backend.generate.return_value = json.dumps(mock_res)
        
        result = self.analyst.resolve_knowledge_conflict(conflict)
        
        self.assertEqual(result["learned_instruction"], "Use latest Python features")
        self.assertEqual(result["severity"], 5)

if __name__ == '__main__':
    unittest.main()
