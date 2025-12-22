import unittest
from unittest.mock import MagicMock, patch
from gortex.core.registry import registry, AgentMetadata
from gortex.agents.manager import manager_node
from gortex.agents.base import BaseAgent

class MockDeployer(BaseAgent):
    @property
    def metadata(self):
        return AgentMetadata(name="Deployer", role="DevOps", description="Deploys to cloud", tools=["cloud_deploy"], version="1.0.0")
    def run(self, state): return {"status": "deployed"}

class TestDynamicOrchestration(unittest.TestCase):
    def setUp(self):
        # 1. 새로운 에이전트 등록
        self.deployer = MockDeployer()
        registry.register("Deployer", MockDeployer, self.deployer.metadata)

    @patch("gortex.agents.manager.LLMFactory.get_default_backend")
    @patch("gortex.agents.manager.SemanticLogSearch")
    @patch("gortex.agents.manager.SynapticTranslator")
    @patch("gortex.agents.manager.LongTermMemory")
    @patch("gortex.agents.manager.EfficiencyMonitor")
    def test_discovery_routing(self, mock_monitor, mock_ltm, mock_trans, mock_log, mock_factory):
        """Manager가 레지스트리를 통해 새로운 에이전트를 찾아내는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # LLM이 'cloud_deploy' 능력이 필요하다고 응답하도록 설정
        mock_backend.generate.return_value = '{"thought": "Need deployment", "required_capability": "cloud_deploy"}'
        
        # 기본 모니터 설정
        mock_monitor.return_value.get_daily_cumulative_cost.return_value = 0.0
        
        state = {
            "messages": [("user", "deploy my app")],
            "agent_energy": 100,
            "agent_economy": {}
        }
        
        result = manager_node(state)
        
        # 결과 확인: next_node가 'deployer'여야 함
        self.assertEqual(result["next_node"], "deployer")

if __name__ == '__main__':
    unittest.main()
