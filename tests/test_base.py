import unittest
from gortex.core.llm.base import LLMBackend

class TestLLMBase(unittest.TestCase):
    def test_subclass_enforcement(self):
        """추상 메서드 구현 강제 여부 확인"""
        with self.assertRaises(TypeError):
            class InvalidBackend(LLMBackend):
                pass
            InvalidBackend()

if __name__ == "__main__":
    unittest.main()
