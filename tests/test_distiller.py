import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from gortex.core.llm.distiller import NeuralDistiller
from gortex.core.evolutionary_memory import EvolutionaryMemory

class TestNeuralDistiller(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_distill_memory"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    def test_wisdom_distillation(self, mock_factory):
        """고성과 규칙들이 하나의 원칙으로 증류되는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        mock_backend.generate.return_value = "Always prioritize asynchronous MQ for long tasks."
        
        # 패치 이후에 인스턴스 생성
        distiller = NeuralDistiller()
        # 테스트용 메모리 설정
        with patch.object(distiller.memory, '__init__', return_value=None):
            distiller.memory.base_dir = self.test_dir
            distiller.memory.shards = {"coding": [], "general": []}
        
        # 1. 3개의 공인 지식 주입
        for i in range(3):
            distiller.memory.shards["coding"].append({
                "id": f"RULE_{i}",
                "learned_instruction": f"Rule number {i}",
                "usage_count": 10,
                "success_count": 10,
                "is_certified": True
            })
            
        # 2. 증류 실행
        wisdom = distiller.distill_wisdom("coding")
        
        # 3. 검증
        self.assertEqual(wisdom, "Always prioritize asynchronous MQ for long tasks.")
        self.assertTrue(mock_backend.generate.called)

    def test_dataset_preparation(self):
        """성공 사례들이 학습용 JSONL로 올바르게 변환되는지 테스트"""
        distiller = NeuralDistiller()
        # 테스트용 메모리 수동 주입
        distiller.memory.shards = {"coding": [], "general": []}
        
        # 1. 지식 데이터 주입
        distiller.memory.shards["coding"].append({
            "context": "File not found error in production.",
            "learned_instruction": "Use os.path.abspath before opening files.",
            "category": "coding"
        })
        
        # 2. 데이터셋 생성
        output_path = distiller.prepare_training_dataset(output_dir=self.test_dir)
        
        # 3. 검증
        self.assertIsNotNone(output_path)
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
            self.assertIn("Gortex Agent", data["instruction"])
            self.assertEqual(data["input"], "File not found error in production.")
            self.assertEqual(data["output"], "Use os.path.abspath before opening files.")

if __name__ == "__main__":
    unittest.main()