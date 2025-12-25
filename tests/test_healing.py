import unittest
import os
from gortex.utils.healing_memory import SelfHealingMemory

class TestSelfHealingMemory(unittest.TestCase):
    def setUp(self):
        self.path = "logs/test_healing.json"
        if os.path.exists(self.path):
            os.remove(self.path)
        self.memory = SelfHealingMemory(storage_path=self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_learn_and_find(self):
        """에러 학습 및 검색 테스트"""
        error = "ModuleNotFoundError: No module named 'pandas'"
        solution = {"action": "pip install pandas"}
        
        self.memory.learn(error, solution)
        
        # 정확히 같은 에러
        found = self.memory.find_solution(error)
        self.assertEqual(found, solution)
        
        # 경로가 포함된 유사 에러 (정규화 테스트)
        error_with_path = "ModuleNotFoundError: No module named 'pandas' in /user/home/script.py"
        found = self.memory.find_solution(error_with_path)
        self.assertEqual(found, solution)

    def test_get_solution_hint(self):
        """힌트 텍스트 반환 테스트"""
        self.memory.learn("Error A", {"action": "Fix A", "target": "File A"})
        
        hint = self.memory.get_solution_hint("Error A")
        self.assertIn("Try this", hint)
        self.assertIn("Fix A", hint)

if __name__ == '__main__':
    unittest.main()
