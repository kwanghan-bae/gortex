import unittest
from gortex.utils.prompt_loader import PromptLoader

class TestHandoffInstruction(unittest.TestCase):
    def setUp(self):
        self.loader = PromptLoader()

    def test_handoff_injection(self):
        prompt = self.loader.get_prompt("coder", handoff_instruction="CHECK_SYNTAX")
        self.assertIn("CHECK_SYNTAX", prompt)
        
    def test_format_kwargs(self):
        # Assuming template has {goal}
        kwargs = {"goal": "Fix Bugs", "handoff_instruction": "USE_STRICT_MODE"}
        # Mock template for test
        self.loader.templates = {"test_agent": {"instruction": "Goal: {goal}"}}
        
        prompt = self.loader.get_prompt("test_agent", **kwargs)
        self.assertIn("Goal: Fix Bugs", prompt)
        self.assertIn("USE_STRICT_MODE", prompt)

if __name__ == "__main__":
    unittest.main()
