import unittest
from gortex.core.registry import registry
from gortex.agents.planner import PlannerAgent
from gortex.agents.coder import CoderAgent
from gortex.agents.analyst import AnalystAgent

class TestV3Migration(unittest.TestCase):
    def test_core_agents_registration(self):
        """핵심 에이전트들이 레지스트리에 정상 등록되었는지 테스트"""
        self.assertIn("planner", registry.list_agents())
        self.assertIn("coder", registry.list_agents())
        self.assertIn("analyst", registry.list_agents())

    def test_planner_v3_standard(self):
        """Planner가 v3 표준(BaseAgent)을 따르는지 테스트"""
        planner = registry.get_agent("Planner")()
        self.assertEqual(planner.metadata.name, "Planner")
        self.assertTrue(callable(planner))

    def test_coder_v3_standard(self):
        """Coder가 v3 표준을 따르는지 테스트"""
        coder = registry.get_agent("Coder")()
        self.assertEqual(coder.metadata.name, "Coder")
        self.assertTrue(callable(coder))

if __name__ == '__main__':
    unittest.main()
