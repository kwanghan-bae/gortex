import unittest
from gortex.utils.math_engine import divide_numbers, calculate_average

class TestMathEngine(unittest.TestCase):
    def test_divide_by_zero(self):
        # 이 테스트는 현재 실패해야 함
        result = divide_numbers(10, 0)
        self.assertEqual(result, 0)

    def test_empty_average(self):
        # 이 테스트도 실패해야 함
        result = calculate_average([])
        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()
