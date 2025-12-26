import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.manager import ManagerAgent
from gortex.agents.swarm import SwarmAgent
from gortex.core.state import GortexState

class TestSelfHealingLoop(unittest.TestCase):
    def setUp(self):
        self.manager = ManagerAgent()
        self.swarm = SwarmAgent()
        self.state: GortexState = {
            "messages": [("user", "Start")],
            "agent_energy": 100,
            "agent_economy": {},
            "debate_result": None
        }

    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    def test_manager_translates_swarm_consensus_to_plan(self, mock_factory):
        """Manager가 Swarm의 합의안을 수신했을 때 Coder를 위한 실행 계획으로 전환하는지 테스트"""
        
        # 1. 시뮬레이션된 Swarm 합의 결과
        consensus_data = {
            "final_decision": "Add input validation to prevent ZeroDivisionError.",
            "action_plan": [
                "Step 1: Check if denominator is zero in utils/math.py",
                "Step 2: Run pytest tests/test_math.py"
            ]
        }
        
        self.state["debate_result"] = consensus_data
        
        # 2. Manager 실행
        result = self.manager.run(self.state)
        
        # 3. 검증
        self.assertEqual(result["next_node"], "coder")
        self.assertIn("plan", result)
        self.assertEqual(len(result["plan"]), 2)
        
        plan_step_1 = json.loads(result["plan"][0])
        self.assertEqual(plan_step_1["action"], "apply_patch") # 기본값
        self.assertIn("Check if denominator", plan_step_1["description"])
        
        plan_step_2 = json.loads(result["plan"][1])
        self.assertEqual(plan_step_2["action"], "execute_shell") # 'run' 키워드 매칭
        
        self.assertIn("긴급 복구 모드", result["messages"][0][1])

    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    async def test_swarm_debug_mode_consensus_structure(self, mock_factory):
        """Swarm이 디버그 모드에서 기술적인 합의안 구조를 생성하는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # Swarm 합의 도출용 프롬프트 응답 모킹
        mock_response = {
            "final_decision": "Fix the path handling in persistence.py",
            "rationale": "Relative paths are causing IOErrors in the swarm environment.",
            "unified_rule": {
                "instruction": "ALWAYS_USE_ABSOLUTE_PATHS_FOR_PERSISTENCE",
                "trigger_patterns": ["path", "file", "save"],
                "severity": 4
            },
            "action_plan": ["Step 1: Use os.path.abspath", "Step 2: run tests"]
        }
        mock_backend.generate.return_value = json.dumps(mock_response)
        
        # 토론 히스토리 시뮬레이션
        history = [
            {"role": "Analyst", "content": "Found IOError at line 45 due to relative path."},
            {"role": "Coder", "content": "I can change it to abspath."}
        ]
        
        # synthesize_consensus 직접 호출 (is_debug=True)
        consensus = self.swarm.synthesize_consensus("IOError in persistence.py", history, is_debug=True)
        
        self.assertEqual(consensus["final_decision"], "Fix the path handling in persistence.py")
        self.assertIn("unified_rule", consensus)
        self.assertEqual(len(consensus["action_plan"]), 2)

if __name__ == "__main__":
    unittest.main()
