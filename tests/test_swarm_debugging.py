import unittest
import asyncio
from unittest.mock import MagicMock, patch
from gortex.core.graph import route_coder
from gortex.agents.swarm import SwarmAgent
from gortex.agents.analyst.base import AnalystAgent

class TestSwarmDebugging(unittest.IsolatedAsyncioTestCase):
    def test_route_coder_escalation(self):
        """Coder 반복 실패 시 Swarm으로 에스컬레이션되는지 테스트"""
        state = {
            "messages": [("ai", "I failed again.")],
            "coder_iteration": 4,
            "next_node": "coder"
        }
        # 3회 초과 실패 시 swarm 반환 기대
        self.assertEqual(route_coder(state), "swarm")

    async def test_swarm_debug_debate_flow(self):
        """Swarm의 디버그 토론 실행 테스트"""
        agent = SwarmAgent()
        agent.backend = MagicMock()
        # 토론 결과 모킹
        agent.backend.generate.return_value = '{"final_decision": "Fix A", "action_plan": ["Step 1"]}'
        
        # 디버그 모드로 토론 실행
        result = await agent.run_debate("ZeroDivisionError in core/engine.py", is_debug=True)
        
        self.assertEqual(result["final_decision"], "Fix A")
        self.assertIn("Step 1", result["action_plan"])

    def test_analyst_debug_synthesis(self):
        """Analyst의 디버그 결과 종합 테스트"""
        analyst = AnalystAgent()
        analyst.backend = MagicMock()
        mock_synthesis = {
            "diagnosis": "Missing zero check",
            "action_plan": ["Add if x != 0:"]
        }
        analyst.backend.generate.return_value = json.dumps(mock_synthesis)
        
        debate_history = [{"role": "innovation", "content": "use try-except"}, {"role": "stability", "content": "use if-check"}]
        result = analyst.synthesize_debug_consensus("ZeroDivisionError", debate_history)
        
        self.assertEqual(result["diagnosis"], "Missing zero check")
        self.assertEqual(result["action_plan"][0], "Add if x != 0:")

import json
if __name__ == '__main__':
    unittest.main()
