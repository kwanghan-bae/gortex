import unittest
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import analyst_instance, analyst_node
from gortex.core.state import GortexState

class TestVisualHealingIntegration(unittest.TestCase):
    def setUp(self):
        self.state: GortexState = {
            "messages": [("user", "The UI looks broken and the dashboard is glitching")],
            "agent_energy": 100,
            "agent_economy": {},
            "next_node": "manager",
            "active_constraints": []
        }

    @patch("gortex.utils.multimodal.capture_ui_screenshot", return_value="logs/screenshots/test.png")
    def test_analyst_triggers_visual_diagnosis(self, mock_capture):
        """시각적 이상 키워드 감지 시 Analyst가 스크린샷 분석 모드로 진입하는지 테스트"""
        
        result = analyst_node(self.state)
        
        # 1. 스크린샷 캡처 도구 호출 확인
        self.assertTrue(mock_capture.called)
        
        # 2. 결과 상태 검증
        self.assertEqual(result["next_node"], "analyst")
        self.assertTrue(result["awaiting_visual_diagnosis"])
        self.assertIn("image:logs/screenshots/test.png", result["handoff_instruction"])

    def test_analyst_performs_multimodal_analysis(self):
        """awaiting_visual_diagnosis 상태에서 실제 멀티모달 분석을 수행하는지 테스트"""
        
        # 전역 인스턴스의 백엔드 직접 모킹
        original_backend = analyst_instance.backend
        analyst_instance.backend = MagicMock()
        analyst_instance.backend.generate.return_value = "The dashboard layout is overlapping at the sidebar."
        
        try:
            self.state["awaiting_visual_diagnosis"] = True
            self.state["handoff_instruction"] = "Analyze this image:logs/screenshots/test.png"
            
            result = analyst_node(self.state)
            
            # 1. LLM 호출 확인
            analyst_instance.backend.generate.assert_called()
            
            # 2. 분석 결과 수신 및 모드 해제
            self.assertEqual(result["next_node"], "manager")
            self.assertFalse(result["awaiting_visual_diagnosis"])
            self.assertIn("overlapping", result["messages"][0][1])
        finally:
            # 백엔드 원복
            analyst_instance.backend = original_backend

if __name__ == "__main__":
    unittest.main()