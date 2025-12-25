import unittest
import os
from datetime import datetime, timedelta
from unittest.mock import patch
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestEvolutionaryMemory(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_experience.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.memory = EvolutionaryMemory(file_path=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_empty_memory(self):
        """파일이 없을 때 빈 리스트를 로드하는지 확인"""
        self.assertEqual(self.memory.memory, [])

    def test_save_and_load_rule(self):
        """규칙이 정상적으로 저장되고 로드되는지 확인"""
        instruction = "Always use Python 3.10+"
        patterns = ["python", "coding style"]
        self.memory.save_rule(instruction, patterns)
        
        self.assertEqual(len(self.memory.memory), 1)
        self.assertEqual(self.memory.memory[0]["learned_instruction"], instruction)
        
        # 파일에서 다시 로드 확인
        new_memory = EvolutionaryMemory(file_path=self.test_file)
        self.assertEqual(len(new_memory.memory), 1)
        self.assertEqual(new_memory.memory[0]["learned_instruction"], instruction)

    def test_duplicate_rule_reinforcement(self):
        """동일한 지침인 경우 기존 규칙이 강화되는지 확인"""
        instruction = "Duplicate Test"
        self.memory.save_rule(instruction, ["pattern1"])
        first_id = self.memory.memory[0]["id"]
        
        # 동일 지침으로 재저장
        self.memory.save_rule(instruction, ["pattern2"])
        
        self.assertEqual(len(self.memory.memory), 1)
        self.assertEqual(self.memory.memory[0]["id"], first_id)
        self.assertIn("pattern2", self.memory.memory[0]["trigger_patterns"])
        self.assertEqual(self.memory.memory[0]["reinforcement_count"], 2)

    def test_conflict_warning(self):
        """트리거 패턴이 유사할 때 충돌 경고가 발생하는지 확인"""
        self.memory.save_rule("Rule A", ["very", "similar", "patterns"])
        # 유사도 0.7 이상 (3개 중 3개 겹침)
        self.memory.save_rule("Rule B", ["very", "similar", "patterns"])
        
        # Rule B는 새로 추가되지만 Rule A에 conflict_warning이 붙음 (현재 로직상)
        # 소스 코드 확인 결과: CASE B에서 existing["conflict_warning"] = True 설정 후 루프 계속됨
        self.assertTrue(self.memory.memory[0].get("conflict_warning"))
        self.assertEqual(self.memory.memory[0].get("potential_contradiction"), "Rule B")

    def test_promote_efficient_pattern(self):
        """효율적인 패턴이 규칙으로 승격되는지 확인"""
        # 80점 미만은 스킵
        self.memory.promote_efficient_pattern("Slow pattern", 50.0)
        self.assertEqual(len(self.memory.memory), 0)
        
        # 95점 (severity 3), context 단어 3개 초과하여 키워드 추출 확인
        self.memory.promote_efficient_pattern("Fast pattern", 95.0, context="Optimization test with multiple words")
        self.assertEqual(len(self.memory.memory), 1)
        self.assertEqual(self.memory.memory[0]["severity"], 3)
        self.assertIn("Optimization", self.memory.memory[0]["trigger_patterns"])

    def test_persist_exception(self):
        """저장 중 예외 발생 시 로그가 기록되는지 확인"""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            with self.assertLogs("GortexEvolutionaryMemory", level="ERROR") as cm:
                self.memory._persist()
                self.assertTrue(any("Failed to persist" in output for output in cm.output))

    def test_macro_management(self):
        """매크로 저장 및 조회가 정상인지 확인"""
        steps = ["step1", "step2"]
        self.memory.save_macro("test_macro", steps, "A test macro")
        
        macros = self.memory.get_macros()
        self.assertEqual(len(macros), 1)
        self.assertEqual(macros[0]["name"], "test_macro")
        self.assertEqual(macros[0]["steps"], steps)
        
        # get_active_constraints에서 매크로는 제외되는지 확인
        constraints = self.memory.get_active_constraints("test_macro")
        self.assertEqual(len(constraints), 0)

    def test_get_active_constraints(self):
        """컨텍스트에 맞는 활성 제약 조건만 반환하는지 확인"""
        self.memory.save_rule("Python Rule", ["python"])
        self.memory.save_rule("JS Rule", ["javascript"])
        
        active = self.memory.get_active_constraints("I am writing python code")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0], "Python Rule")
        self.assertEqual(self.memory.memory[0]["usage_count"], 1)

    def test_gc_rules(self):
        """오래되고 사용되지 않는 규칙이 정리되는지 확인"""
        now = datetime.now()
        # 40일 전 생성, 사용 0회 -> 삭제 대상
        old_rule = {
            "id": "OLD",
            "trigger_patterns": ["old"],
            "learned_instruction": "Old Instruction",
            "created_at": (now - timedelta(days=40)).isoformat(),
            "usage_count": 0
        }
        # 40일 전 생성, 사용 5회 -> 유지 대상
        active_old_rule = {
            "id": "ACTIVE_OLD",
            "trigger_patterns": ["active"],
            "learned_instruction": "Active Old Instruction",
            "created_at": (now - timedelta(days=40)).isoformat(),
            "usage_count": 5
        }
        # 최근 생성 -> 유지 대상
        new_rule = {
            "id": "NEW",
            "trigger_patterns": ["new"],
            "learned_instruction": "New Instruction",
            "created_at": now.isoformat(),
            "usage_count": 0
        }
        
        self.memory.memory = [old_rule, active_old_rule, new_rule]
        self.memory.gc_rules(min_usage=1, max_age_days=30)
        
        self.assertEqual(len(self.memory.memory), 2)
        ids = [r["id"] for r in self.memory.memory]
        self.assertNotIn("OLD", ids)
        self.assertIn("ACTIVE_OLD", ids)
        self.assertIn("NEW", ids)

    def test_load_corrupted_json(self):
        """손상된 JSON 파일 처리 확인"""
        with open(self.test_file, 'w') as f:
            f.write("{ invalid json")
        
        # 생성자에서 _load_memory 호출 시 에러 핸들링 확인
        mem = EvolutionaryMemory(file_path=self.test_file)
        self.assertEqual(mem.memory, [])

if __name__ == '__main__':
    unittest.main()
