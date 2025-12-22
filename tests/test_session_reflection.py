import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from gortex.agents.analyst.reflection import ReflectionAnalyst

class TestSessionReflection(unittest.TestCase):
    def setUp(self):
        self.session_dir = "docs/sessions"
        os.makedirs(self.session_dir, exist_ok=True)
        self.test_file = os.path.join(self.session_dir, "session_9999.md")
        
        content = """# Session 9999
## 📝 Activities
- Fixed API 404 error by changing model to gemini-2.0-flash.
## 🔍 Issues & Resolutions
- Issue: Model gemini-1.5-flash not found.
- Resolution: Use gemini-2.0-flash instead.
"""
        with open(self.test_file, "w") as f:
            f.write(content)
            
        self.agent = ReflectionAnalyst()
        self.agent.backend = MagicMock()
        self.agent.memory = MagicMock()

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_reflect_on_session_docs(self):
        """세션 문서로부터 규칙 추출 및 저장 테스트"""
        # Mock LLM Response
        mock_rule = {
            "instruction": "Use gemini-2.0-flash for high availability.",
            "trigger_patterns": ["404", "model not found"],
            "severity": 4
        }
        self.agent.backend.generate.return_value = json.dumps([mock_rule])
        
        # Run
        result = self.agent.reflect_on_session_docs(session_id="9999")
        
        # Verify
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["instruction"], mock_rule["instruction"])
        # Verify save_rule call
        self.agent.memory.save_rule.assert_called_once()

if __name__ == '__main__':
    unittest.main()
