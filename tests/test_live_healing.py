import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import analyst_node
from gortex.agents.manager import manager_node
from gortex.agents.swarm import swarm_node_async
from gortex.core.state import GortexState

class TestLiveHealingWorkflow(unittest.TestCase):
    def setUp(self):
        self.state: GortexState = {
            "messages": [("ai", "I wrote some code.")],
            "agent_energy": 100,
            "agent_economy": {},
            "awaiting_review": True,
            "review_target": "utils/math.py",
            "next_node": "analyst",
            "is_recovery_mode": False,
            "active_constraints": []
        }

    @patch("gortex.agents.analyst.AnalystAgent.perform_peer_review")
    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    def test_full_healing_transition(self, mock_factory, mock_review):
        """에러 발생부터 Swarm 이송, 복구 계획 수립까지의 전이 과정을 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # 1. Analyst가 에러 감지 및 Swarm 이송
        mock_review.return_value = {
            "score": 40,
            "comment": "Security risk: hardcoded API key found.",
            "is_approved": False
        }
        
        result_analyst = analyst_node(self.state)
        
        self.assertEqual(result_analyst["next_node"], "swarm")
        self.assertIn("CRITICAL ERROR DETECTED", result_analyst["current_issue"])
        self.assertIn("hardcoded API key", result_analyst["current_issue"])
        
        # 2. Swarm이 RCA 리포트를 바탕으로 합의안 도출 시뮬레이션
        swarm_consensus = {
            "final_decision": "Replace hardcoded key with os.getenv.",
            "action_plan": ["Step 1: apply_patch to remove key", "Step 2: run security scan"]
        }
        
        self.state.update(result_analyst)
        self.state["debate_result"] = swarm_consensus
        
        # 3. Manager가 합의안을 복구 계획으로 변환
        result_manager = manager_node(self.state)
        
        self.assertEqual(result_manager["next_node"], "coder")
        self.assertEqual(len(result_manager["plan"]), 2)
        self.assertTrue(result_manager.get("is_recovery_mode"))
        self.assertIn("긴급 복구 모드", result_manager["messages"][0][1])
        
        # 4. 최종 복구 성공 시 보상 확인
        self.state.update(result_manager)
        self.state["awaiting_review"] = True
        self.state["messages"].append(("ai", "I fixed the key using os.getenv."))
        
        # 승인 결과 모킹
        mock_review.return_value = {
            "score": 95,
            "comment": "Perfect fix.",
            "is_approved": True
        }
        
        final_result = analyst_node(self.state)
        
        # 보상 확인: 복구 모드이므로 고득점(3배 난이도) 반영 확인
        coder_eco = final_result["agent_economy"].get("coder", {})
        # 보상 계산: (10 * 0.95 * 3.0) = 28.5 추가
        self.assertGreater(coder_eco.get("points", 0), 120)

if __name__ == "__main__":
    unittest.main()