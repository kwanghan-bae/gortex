import unittest
import json
import os
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import analyst_node
from gortex.agents.manager import manager_node
from gortex.agents.coder import coder_instance, coder_node
from gortex.core.state import GortexState
from gortex.utils.tools import read_file, write_file

class TestLiveHealingExecution(unittest.TestCase):
    def setUp(self):
        # 1. 취약한 파일 생성
        self.target_file = "gortex/utils/math_engine_test.py"
        os.makedirs(os.path.dirname(self.target_file), exist_ok=True)
        write_file(self.target_file, "def divide(a, b):\n    return a / b")
        
        # 2. 경제 시스템 초기화 및 권한 부여 (Coder에게 Coding 500점 부여)
        economy = {
            "coder": {
                "points": 1000,
                "level": "Journeyman",
                "skill_points": {"Coding": 600}
            }
        }
        
        self.state: GortexState = {
            "messages": [("user", "Fix divide by zero")],
            "agent_energy": 100,
            "agent_economy": economy,
            "working_dir": ".",
            "file_cache": {},
            "active_constraints": []
        }

    def tearDown(self):
        if os.path.exists(self.target_file):
            os.remove(self.target_file)

    @patch("gortex.agents.analyst.AnalystAgent.perform_peer_review")
    def test_full_healing_execution(self, mock_review):
        """장애 감지부터 실제 코드 패치 적용까지의 전 과정을 검증"""
        
        # 1. Manager의 백엔드 모킹
        with patch("gortex.agents.manager.LLMFactory.get_default_backend") as mock_mgr_factory:
            mock_mgr_backend = MagicMock()
            mock_mgr_factory.return_value = mock_mgr_backend
            
            # 2. Swarm 결과 시뮬레이션
            self.state["debate_result"] = {
                "final_decision": "Add zero check",
                "action_plan": [f"Step 1: apply_patch to {self.target_file} to add if b == 0: return 0"]
            }
            
            # 3. Manager가 합의안을 계획으로 변환
            res_manager = manager_node(self.state)
            self.state.update(res_manager)
            
            # 4. Coder의 백엔드 직접 모킹
            original_backend = coder_instance.backend
            coder_instance.backend = MagicMock()
            
            coder_instance.backend.generate.return_value = json.dumps({
                "thought": "Applying zero check patch.",
                "action": "apply_patch",
                "action_input": {
                    "path": self.target_file,
                    "start_line": 2,
                    "end_line": 2,
                    "new_content": "    if b == 0: return 0\n    return a / b"
                },
                "status": "in_progress"
            })
            
            try:
                # Coder 노드 실행 (이제 권한이 있으므로 성공해야 함)
                coder_node(self.state)
                
                # 5. 파일 내용 확인
                patched_content = read_file(self.target_file)
                self.assertIn("if b == 0: return 0", patched_content)
                print("\n✅ Successfully verified code patch via healing loop with proper permissions.")
            finally:
                coder_instance.backend = original_backend

if __name__ == "__main__":
    unittest.main()