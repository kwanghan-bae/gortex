import unittest
import json
import os
from unittest.mock import MagicMock, patch
from gortex.agents.evolution_node import EvolutionNode, evolution_node

class TestGortexEvolution(unittest.TestCase):
    def setUp(self):
        self.test_file = "evolution_test.py"
        with open(self.test_file, "w") as f:
            f.write("def old_func(): pass")
        
        self.radar_file = "tech_radar.json"
        self.radar_backup = None
        if os.path.exists(self.radar_file):
            with open(self.radar_file, "r") as f:
                self.radar_backup = f.read()
        
        with open(self.radar_file, "w") as f:
            json.dump({
                "adoption_candidates": [
                    {"tech": "Type Hinting", "target_file": self.test_file, "reason": "Better clarity"}
                ]
            }, f)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if self.radar_backup:
            with open(self.radar_file, "w") as f:
                f.write(self.radar_backup)
        elif os.path.exists(self.radar_file):
            os.remove(self.radar_file)

    @patch('gortex.agents.evolution_node.LLMFactory')
    @patch('gortex.agents.evolution_node.execute_shell')
    def test_evolution_flow_success(self, mock_shell, mock_factory):
        """진화 프로세스가 성공적으로 코드를 수정하고 검증하는지 테스트"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "```python\ndef old_func() -> None: pass\n```"
        mock_factory.get_default_backend.return_value = mock_backend
        
        mock_shell.return_value = "Ready to commit"
        
        state = {"assigned_model": "test-model"}
        result = evolution_node(state)
        
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("자가 진화 완료", result["messages"][0][1])
        
        with open(self.test_file, "r") as f:
            content = f.read()
            self.assertIn("-> None", content)

    @patch('gortex.agents.evolution_node.LLMFactory')
    @patch('gortex.agents.evolution_node.execute_shell')
    def test_evolution_rollback_on_failure(self, mock_shell, mock_factory):
        """검증 실패 시 코드가 원복되는지 테스트"""
        mock_backend = MagicMock()
        mock_backend.generate.return_value = "broken code"
        mock_factory.get_default_backend.return_value = mock_backend
        
        mock_shell.return_value = "Syntax Error!"
        
        state = {"assigned_model": "test-model"}
        result = evolution_node(state)
        
        self.assertIn("롤백되었습니다", result["messages"][0][1])
        
        with open(self.test_file, "r") as f:
            content = f.read()
            self.assertEqual(content, "def old_func(): pass")

if __name__ == '__main__':
    unittest.main()
