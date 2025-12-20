import unittest
from gortex.utils.token_counter import count_tokens, estimate_cost

class TestGortexTokenCounter(unittest.TestCase):
    def test_count_tokens_basic(self):
        text = "Hello world"
        tokens = count_tokens(text)
        # "Hello world" -> chars=11, words=2 -> (11*0.5) + 2 = 7.5 -> 7
        self.assertGreater(tokens, 0)

    def test_count_tokens_korean(self):
        text = "안녕하세요 반가워요"
        tokens = count_tokens(text)
        self.assertGreater(tokens, 0)

    def test_estimate_cost(self):
        cost = estimate_cost(1_000_000, model="flash")
        self.assertAlmostEqual(cost, 0.075)
        
        cost_pro = estimate_cost(1_000_000, model="pro")
        self.assertAlmostEqual(cost_pro, 3.5)

if __name__ == '__main__':
    unittest.main()
