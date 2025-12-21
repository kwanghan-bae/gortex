import unittest
import asyncio
from unittest.mock import MagicMock
from gortex.core.engine import GortexEngine

class TestGortexEconomy(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        self.observer = MagicMock()
        self.vocal = MagicMock()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.state_vars = {
            "agent_economy": {"coder": {"points": 10}},
            "token_credits": {"coder": 100.0},
            "session_cache": {},
            "last_event_id": None
        }

    def test_economy_update_sync(self):
        """에이전트 출력에 담긴 경제 데이터가 state_vars에 정확히 병합되는지 테스트"""
        output = {
            "agent_economy": {"coder": {"points": 20, "level": "Expert"}},
            "token_credits": {"coder": 110.0}
        }
        
        asyncio.run(self.engine.process_node_output("analyst", output, self.state_vars))
        
        # 병합 결과 확인
        self.assertEqual(self.state_vars["agent_economy"]["coder"]["points"], 20)
        self.assertEqual(self.state_vars["agent_economy"]["coder"]["level"], "Expert")
        self.assertEqual(self.state_vars["token_credits"]["coder"], 110.0)

if __name__ == '__main__':
    unittest.main()
