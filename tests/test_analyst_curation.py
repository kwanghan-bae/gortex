import unittest
import os
import json
import shutil
from agents.analyst.base import AnalystAgent

class TestAnalystCuration(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_analyst"
        os.makedirs(self.test_dir, exist_ok=True)
        self.dataset_path = os.path.join(self.test_dir, "evolution.jsonl")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_curate_evolution_data(self):
        # 1. Prepare dummy data
        dummy_memories = [
            {
                "trigger_context": "ImportError: No module named 'xyz'", 
                "failed_solution": "import xyz", 
                "learned_instruction": "Check if module is installed or use local import", 
                "severity": 5, 
                "session": "s1"
            },
            {
                "trigger_context": "Infinite Loop in Coder", 
                "failed_solution": "while True: pass", 
                "learned_instruction": "Add max_iterations break condition", 
                "severity": 3, 
                "session": "s2"
            }
        ]
        
        # 2. Init Agent and Inject Memory
        agent = AnalystAgent()
        # Directly injecting into the memory list for testing purposes
        agent.memory.memory = dummy_memories 
        
        # 3. Run curation with custom output path
        result = agent.curate_evolution_data(output_path=self.dataset_path)
        
        # 4. Verify
        self.assertTrue(os.path.exists(self.dataset_path))
        self.assertIn("Curated 2 items", result)
        
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            
            # Check format suitable for fine-tuning
            entry1 = json.loads(lines[0])
            self.assertIn("messages", entry1)
            # System message is at 0
            # User message should contain context/problem
            self.assertIn("ImportError", entry1["messages"][1]["content"])
            # Assistant message should contain the learned rule/solution
            self.assertIn("Check if module is installed", entry1["messages"][2]["content"])
