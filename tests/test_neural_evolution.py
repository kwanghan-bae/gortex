import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from gortex.core.llm.trainer import GortexTrainer
from gortex.core.registry import registry, AgentMetadata
from gortex.ui.dashboard import DashboardUI
from rich.console import Console

class TestNeuralEvolution(unittest.TestCase):
    def setUp(self):
        # 레지스트리에 테스트 에이전트 등록
        self.agent_name = "Coder"
        registry.register(self.agent_name, MagicMock, AgentMetadata(
            name=self.agent_name,
            role="Developer",
            description="Test Coder",
            tools=["test_tool"],
            version="3.0.0"
        ))
        
        self.trainer = GortexTrainer()
        self.job_id = "JOB_TEST_EVO"
        
        # 임시 학습 잡 설정
        job_dir = os.path.join(self.trainer.jobs_dir, self.job_id)
        os.makedirs(job_dir, exist_ok=True)
        with open(os.path.join(job_dir, "config.json"), "w") as f:
            json.dump({"status": "completed"}, f)

    def tearDown(self):
        if os.path.exists(os.path.join(self.trainer.jobs_dir, self.job_id)):
            shutil.rmtree(os.path.join(self.trainer.jobs_dir, self.job_id))

    @patch("gortex.core.auth.GortexAuth.generate")
    def test_agent_model_upgrade_flow(self, mock_gen):
        """학습 완료 후 에이전트가 커스텀 모델로 업그레이드되는 전 과정 테스트"""
        
        # 1. 커스텀 모델 등록 실행
        success = self.trainer.register_custom_model(self.job_id, self.agent_name)
        self.assertTrue(success)
        
        # 2. 레지스트리 메타데이터 갱신 확인
        upgraded_meta = registry.get_metadata(self.agent_name)
        self.assertIn("+slm", upgraded_meta.version)
        
        # 3. UI 렌더링 확인
        console = Console(width=80)
        ui = DashboardUI(console)
        ui.current_agent = self.agent_name
        
        status_panel = ui._render_status_panel()
        # Rich Panel의 renderable에서 텍스트 추출 검증
        self.assertIn("💎", str(status_panel.renderable))

if __name__ == "__main__":
    unittest.main()