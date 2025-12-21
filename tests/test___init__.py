import unittest
import gortex.core.llm as llm_package

class TestLLMPackage(unittest.TestCase):
    def test_package_import(self):
        """core/llm 패키지가 정상적으로 임포트되는지 확인"""
        self.assertIsNotNone(llm_package)

if __name__ == "__main__":
    unittest.main()
