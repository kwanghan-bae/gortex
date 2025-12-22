import unittest
from gortex.core.registry import AgentRegistry, AgentMetadata
from gortex.agents.base import BaseAgent

class MockAgent(BaseAgent):
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="MockBot",
            role="Testing",
            description="Used for unit tests",
            tools=["test_tool"],
            version="1.0.0"
        )
    def run(self, state):
        return {"status": "ok"}

class TestAgentRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = AgentRegistry()

    def test_register_and_get(self):
        """에이전트 등록 및 조회 테스트"""
        agent_cls = MockAgent
        meta = agent_cls().metadata
        
        self.registry.register("MockBot", agent_cls, meta)
        
        # 1. 클래스 조회
        retrieved_cls = self.registry.get_agent("MockBot")
        self.assertEqual(retrieved_cls, agent_cls)
        
        # 2. 메타데이터 조회
        retrieved_meta = self.registry.get_metadata("MockBot")
        self.assertEqual(retrieved_meta.role, "Testing")
        
        # 3. 능력(Capability) 탐색
        capable = self.registry.discover_capability("test_tool")
        self.assertIn("mockbot", capable)

if __name__ == '__main__':
    unittest.main()
