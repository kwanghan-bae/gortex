import unittest
import os
import json
import pandas as pd
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import AnalystAgent, analyst_node
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestGortexAnalyst(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_data.csv"
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df.to_csv(self.test_csv, index=False)
        self.memory_path = "test_experience.json"
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)

    def test_analyze_data_csv(self):
        """CSV 파일 분석 기능 테스트"""
        agent = AnalystAgent()
        result_json = agent.analyze_data(self.test_csv)
        result = json.loads(result_json)
        self.assertEqual(result["rows"], 2)
        self.assertIn("A", result["columns"])

    @patch('gortex.agents.analyst.GortexAuth')
    def test_analyze_feedback(self, mock_auth_cls):
        """부정 피드백 분석 및 규칙 추출 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "feedback_detected": True,
            "instruction": "항상 snake_case를 사용하라",
            "trigger_patterns": ["naming", "변수명"],
            "severity": 4
        })
        mock_auth.generate.return_value = mock_res

        agent = AnalystAgent()
        result = agent.analyze_feedback([MagicMock(content="변수명 왜 이래? snake_case로 해")])
        
        self.assertIsNotNone(result)
        self.assertEqual(result["instruction"], "항상 snake_case를 사용하라")

    def test_evolutionary_memory_save_and_get(self):
        """학습된 규칙 저장 및 로드 테스트"""
        mem = EvolutionaryMemory(file_path=self.memory_path)
        mem.save_rule("Test Rule", ["test", "trigger"])
        
        rules = mem.get_active_constraints("This is a test message")
        self.assertIn("Test Rule", rules)
        
        # persistence 확인
        mem2 = EvolutionaryMemory(file_path=self.memory_path)
        self.assertEqual(len(mem2.memory), 1)

if __name__ == '__main__':
    unittest.main()
