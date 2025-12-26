import unittest
import os
import json
import shutil
from unittest.mock import patch
from gortex.agents.analyst import analyst_node
from gortex.core.state import GortexState

class TestAutonomousTraining(unittest.TestCase):
    def setUp(self):
        self.state: GortexState = {
            "messages": [("user", "Evolution check")],
            "agent_energy": 95,
            "agent_economy": {},
            "next_node": "analyst",
            "active_constraints": []
        }
        self.test_dir = "tests/test_training"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("gortex.core.llm.distiller.NeuralDistiller.prepare_training_dataset")
    @patch("gortex.core.llm.trainer.GortexTrainer.create_training_job")
    def test_training_trigger_on_large_dataset(self, mock_create_job, mock_prepare):
        """데이터셋이 임계치를 넘었을 때 학습 잡이 생성되는지 테스트"""
        
        # 1. 가짜 데이터셋 생성 (50라인 이상)
        dataset_path = os.path.join(self.test_dir, "large_dataset.jsonl")
        with open(dataset_path, "w") as f:
            for i in range(55):
                f.write(json.dumps({"sample": i}) + "\n")
        
        mock_prepare.return_value = dataset_path
        mock_create_job.return_value = "JOB_123"
        
        # 시간 조건을 맞추기 위해 datetime.now() 모킹 (12시 정각 가정)
        from datetime import datetime
        mock_now = datetime(2025, 12, 26, 12, 0, 0)
        
        with patch("gortex.agents.analyst.datetime") as mock_dt:
            mock_dt.now.return_value = mock_now
            # mock_dt.fromisoformat = datetime.fromisoformat # 필요시 추가
            
            result = analyst_node(self.state)
            
            # 2. 검증
            self.assertTrue(mock_create_job.called)
            self.assertIn("자가 학습 개시", result["messages"][-1][1])
            self.assertIn("JOB_123", result["messages"][-1][1])

if __name__ == "__main__":
    unittest.main()
