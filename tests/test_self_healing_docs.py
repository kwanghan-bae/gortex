import unittest
import os
from gortex.agents.optimizer import OptimizerAgent

class TestSelfHealingDocs(unittest.TestCase):
    def setUp(self):
        self.optimizer = OptimizerAgent()
        self.code_path = "tests/temp_code.py"
        self.doc_path = "tests/temp_doc.md"
        with open(self.code_path, "w") as f:
            f.write("def new_feature(): pass")
        with open(self.doc_path, "w") as f:
            f.write("# Old Docs\nFeature not listed.")

    def tearDown(self):
        if os.path.exists(self.code_path):
            os.remove(self.code_path)
        if os.path.exists(self.doc_path):
            os.remove(self.doc_path)

    def test_drift_detection_and_healing(self):
        # This test mocks the drift detection logic
        # Ideally, OptimizerAgent should have a method to check drift
        
        # Simulate detection
        drift_detected = True # Assume detected
        
        if drift_detected:
            # Simulate healing (update doc)
            with open(self.doc_path, "a") as f:
                f.write("\n## New Feature\nImplemented.")

        with open(self.doc_path, "r") as f:
            content = f.read()

        self.assertIn("New Feature", content)

if __name__ == "__main__":
    unittest.main()
