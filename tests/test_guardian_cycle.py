import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import analyst_node
from gortex.agents.manager import manager_node
from gortex.core.state import GortexState

class TestGuardianCycle(unittest.TestCase):
    def setUp(self):
        self.state: GortexState = {
            "messages": [("user", "System heartbeat check")],
            "agent_energy": 90, # 85 이상으로 설정하여 가디언 모드 유도
            "agent_economy": {},
            "next_node": "manager"
        }

    @patch("gortex.agents.analyst.AnalystAgent.propose_proactive_refactoring")
    def test_analyst_triggers_guardian_mode(self, mock_propose):
        """에너지가 높을 때 Analyst가 선제적 최적화(Guardian Mode)를 제안하는지 테스트"""
        
        # 1. 고위험 리팩토링 제안 모킹
        mock_propose.return_value = [{
            "target_file": "core/engine.py",
            "reason": "Deep nesting in process_node_output.",
            "action_plan": ["Step 1: Extract truncate function", "Step 2: Run engine tests"],
            "risk_level": "Medium",
            "expected_gain": "Better readability"
        }]
        
        # 2. Analyst 노드 실행
        result = analyst_node(self.state)
        
        # 3. 검증
        self.assertTrue(result.get("is_guardian_mode"))
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("🛡️ **가디언 모드 활성화**", result["messages"][0][1])
        self.assertIn("action_plan", result["debate_result"])

    def test_manager_translates_guardian_plan(self):
        """Manager가 가디언 제안을 수신했을 때 Coder를 위한 실행 계획으로 변환하는지 테스트"""
        
        # 1. 시뮬레이션된 가디언 결과 주입
        self.state["is_guardian_mode"] = True
        self.state["debate_result"] = {
            "final_decision": "Refactor engine logic",
            "action_plan": ["Apply patch to engine", "Run full tests"]
        }
        
        # 2. Manager 실행
        result = manager_node(self.state)
        
        # 3. 검증
        self.assertEqual(result["next_node"], "coder")
        self.assertEqual(len(result["plan"]), 2)
        self.assertTrue(result["is_guardian_mode"])
        self.assertIn("선제적 가디언 모드", result["messages"][0][1])
        
        # 계획 내용 확인
        plan_step_2 = json.loads(result["plan"][1])
        self.assertEqual(plan_step_2["action"], "execute_shell") # 'Run' 키워드 매칭

if __name__ == "__main__":
    unittest.main()
