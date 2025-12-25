import unittest
import os
from unittest.mock import MagicMock, patch
from gortex.core.engine import GortexEngine
from gortex.agents.analyst.base import AnalystAgent
from gortex.agents.coder import CoderAgent

class TestAutoPatching(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = GortexEngine()
        self.engine.ui = MagicMock()
        
        self.test_file = "utils/token_counter.py"
        self.test_output = "tests/test_auto_token_counter.py"

    def tearDown(self):
        if os.path.exists(self.test_output):
            os.remove(self.test_output)

    def test_identify_test_hotspots(self):
        """테스트 핫스팟 식별 기능 검증"""
        analyst = AnalystAgent()
        hotspots = analyst.identify_test_hotspots()
        if hotspots:
            self.assertIn("file", hotspots[0])
            self.assertIn("risk_score", hotspots[0])

    def test_generate_regression_test(self):
        """자율 테스트 생성 및 초기 실행 검증"""
        coder = CoderAgent()
        # 인스턴스에 직접 모킹 주입
        coder.backend = MagicMock()
        
        # Mock LLM response
        mock_test_code = """import unittest
class TestDummy(unittest.TestCase):
    def test_pass(self): self.assertTrue(True)
"""
        coder.backend.generate.return_value = f"```python\n{mock_test_code}\n```"
        
        res = coder.generate_regression_test(self.test_file, risk_info="Test Risk")
        
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(self.test_output))

    async def test_run_self_defense_cycle_integration(self):
        """방어 사이클 통합 실행 테스트 (Async)"""
        with patch('gortex.agents.analyst.base.AnalystAgent.identify_test_hotspots') as mock_hotspots, \
             patch('gortex.agents.coder.CoderAgent.generate_regression_test') as mock_gen:
            
            mock_hotspots.return_value = [{"file": "util.py", "risk_score": 100, "reason": "High Risk"}]
            mock_gen.return_value = {"status": "success", "file": "tests/test_auto_util.py"}
            
            await self.engine.run_self_defense_cycle()
            
            # UI 알림 호출 확인
            self.engine.ui.add_achievement.assert_called_with("Defense Up: test_auto_util.py")

if __name__ == '__main__':
    unittest.main()