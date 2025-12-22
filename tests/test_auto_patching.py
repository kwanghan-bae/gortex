import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst.reflection import ReflectionAnalyst
from gortex.utils.tools import verify_patch_integrity

class TestAutoPatching(unittest.TestCase):
    def test_bug_diagnosis(self):
        """버그 진단 로직 테스트"""
        analyst = ReflectionAnalyst()
        analyst.backend = MagicMock()
        
        # 1. Mock LLM Response
        mock_res = {
            "bug_type": "ZeroDivisionError",
            "target_file": "core/engine.py",
            "line_number": 42,
            "fix_instruction": "Add check for zero before division",
            "is_patchable": True
        }
        analyst.backend.generate.return_value = json.dumps(mock_res)
        
        # 2. Run Diagnosis
        error_log = "ZeroDivisionError: division by zero in core/engine.py line 42"
        diagnosis = analyst.diagnose_bug(error_log)
        
        self.assertEqual(diagnosis["bug_type"], "ZeroDivisionError")
        self.assertTrue(diagnosis["is_patchable"])

    def test_verify_patch_integrity_syntax_error(self):
        """구문 오류 패치 감지 테스트"""
        bad_file = "broken.py"
        with open(bad_file, "w") as f:
            f.write("def broken_func(:") # Syntax Error
            
        result = verify_patch_integrity(bad_file)
        self.assertFalse(result["success"])
        self.assertIn("Syntax Error", result["reason"])
        
        if os.path.exists(bad_file): os.remove(bad_file)

    @patch("gortex.utils.tools.execute_shell")
    def test_verify_patch_integrity_success(self, mock_shell):
        """정상 패치 검증 테스트"""
        good_file = "good.py"
        with open(good_file, "w") as f:
            f.write("def ok(): return True")
            
        mock_shell.return_value = "OK" # Test pass simulation
        
        # Create a dummy test file to trigger test execution
        test_file = "tests/test_good.py"
        os.makedirs("tests", exist_ok=True)
        with open(test_file, "w") as f: f.write("import unittest")

        result = verify_patch_integrity(good_file)
        self.assertTrue(result["success"])
        
        if os.path.exists(good_file): os.remove(good_file)
        if os.path.exists(test_file): os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
