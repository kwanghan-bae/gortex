import unittest
import os
import shutil
from unittest.mock import MagicMock, patch
from gortex.agents.analyst.base import AnalystAgent
from gortex.agents.coder import CoderAgent
from gortex.core.registry import registry

class TestAgentGeneration(unittest.TestCase):
    def setUp(self):
        self.analyst = AnalystAgent()
        self.coder = CoderAgent()
        
        # Mocking LLMs
        self.analyst.backend = MagicMock()
        self.coder.backend = MagicMock()
        
        # 임시 에이전트 폴더 생성 방지 (테스트용)
        self.test_agent_file = "agents/auto_clouddeployeragent.py"

    def tearDown(self):
        if os.path.exists(self.test_agent_file):
            os.remove(self.test_agent_file)

    def test_end_to_end_agent_spawning(self):
        """명세 제안부터 코드 생성 및 등록까지의 전 과정 테스트"""
        
        # 1. Analyst가 결핍을 인지하고 명세를 제안함
        mock_spec = {
            "agent_name": "CloudDeployerAgent",
            "role": "Cloud Specialist",
            "description": "Deploys apps to AWS/GCP",
            "required_tools": ["aws_cli", "terraform"],
            "version": "1.0.0",
            "logic_strategy": "Use terraform to deploy resources"
        }
        self.analyst.backend.generate.return_value = json.dumps(mock_spec)
        
        spec = self.analyst.identify_capability_gap(unresolved_task="Deploy this app to AWS")
        self.assertEqual(spec["agent_name"], "CloudDeployerAgent")

        # 2. Coder가 명세를 바탕으로 코드를 생성함
        # 실제 BaseAgent를 상속받는 유효한 코드를 모킹
        generated_code = """
from gortex.agents.base import BaseAgent
from gortex.core.registry import AgentMetadata, registry

class CloudDeployerAgent(BaseAgent):
    @property
    def metadata(self):
        return AgentMetadata(name="CloudDeployerAgent", role="Cloud", description="Test", tools=["aws"], version="1.0.0")
    def run(self, state):
        return {"status": "deployed"}

# Register
registry.register("CloudDeployerAgent", CloudDeployerAgent, CloudDeployerAgent().metadata)
"""
        self.coder.backend.generate.return_value = generated_code
        
        # 3. 에이전트 생성 및 동적 로드 실행
        result = self.coder.generate_new_agent(spec)
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(result["file"]))
        
        # 4. 레지스트리에 실제 등록되었는지 확인
        self.assertIn("clouddeployeragent", registry.list_agents())
        metadata = registry.get_metadata("CloudDeployerAgent")
        self.assertEqual(metadata.role, "Cloud")

import json
if __name__ == '__main__':
    unittest.main()
