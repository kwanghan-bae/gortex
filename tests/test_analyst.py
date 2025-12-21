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

    @patch('gortex.agents.analyst.GortexAuth')
    def test_analyze_data_csv(self, mock_auth_cls):
        """CSV 파일 분석 기능 테스트 (딕셔너리 반환 대응)"""
        mock_auth = mock_auth_cls.return_value
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "chart_type": "bar",
            "title": "Test Chart",
            "plotly_json": {"data": [], "layout": {}}
        })
        mock_auth.generate.return_value = mock_res

        agent = AnalystAgent()
        result = agent.analyze_data(self.test_csv)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["summary"]["rows"], 2)
        self.assertIn("A", result["summary"]["columns"])
        self.assertEqual(result["visualization"]["chart_type"], "bar")

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

    def test_evolutionary_memory_deduplication(self):
        """규칙 중복 저장 및 병합 테스트 (강화 횟수 포함)"""
        mem = EvolutionaryMemory(file_path=self.memory_path)
        
        # 1. 첫 번째 규칙 저장
        mem.save_rule("Strict Typing", ["typing"], severity=2, context="Initial context")
        self.assertEqual(len(mem.memory), 1)
        self.assertEqual(mem.memory[0]["reinforcement_count"], 1)
        
        # 2. 동일한 지침으로 두 번째 규칙 저장 (중복)
        mem.save_rule("Strict Typing", ["python"], severity=4, context="Newer context")
        
        # 3. 결과 검증 (개수는 그대로, 데이터는 병합/강화되어야 함)
        self.assertEqual(len(mem.memory), 1)
        self.assertEqual(mem.memory[0]["severity"], 4) # 더 높은 severity 반영
        self.assertEqual(mem.memory[0]["reinforcement_count"], 2) # 강화 횟수 증가
        self.assertEqual(mem.memory[0]["context"], "Newer context") # 최신 context 반영
        self.assertIn("python", mem.memory[0]["trigger_patterns"])
        self.assertIn("typing", mem.memory[0]["trigger_patterns"])


if __name__ == '__main__':
    unittest.main()
