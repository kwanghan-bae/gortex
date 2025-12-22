import unittest
import os
import json
from rich.console import Console
from gortex.core.observer import GortexObserver
from gortex.ui.dashboard import DashboardUI

class TestCollaborationViz(unittest.TestCase):
    def setUp(self):
        self.log_path = "tests/test_trace.jsonl"
        self.observer = GortexObserver(log_path=self.log_path)
        self.console = Console()
        self.ui = DashboardUI(self.console)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_observer_matrix_calculation(self):
        """인과 관계 로그를 통한 협업 매트릭스 계산 테스트"""
        # 1. 가상의 연쇄 호출 로그 기록
        # Event 1: Manager (Root)
        e1 = self.observer.log_event("manager", "start", {"task": "test"})
        # Event 2: Planner (caused by Manager)
        e2 = self.observer.log_event("planner", "plan", {"steps": []}, cause_id=e1)
        # Event 3: Coder (caused by Planner)
        e3 = self.observer.log_event("coder", "code", {"file": "a.py"}, cause_id=e2)
        # Event 4: Coder again (caused by Planner)
        e4 = self.observer.log_event("coder", "code", {"file": "b.py"}, cause_id=e2)
        
        # 2. 매트릭스 추출
        matrix = self.observer.get_collaboration_matrix()
        
        # 3. 검증
        self.assertEqual(matrix["manager"]["planner"], 1)
        self.assertEqual(matrix["planner"]["coder"], 2)
        self.assertNotIn("coder", matrix) # Coder가 누군가를 호출하지는 않음

    def test_dashboard_heatmap_rendering(self):
        """히트맵 시각화 렌더링 테스트"""
        mock_matrix = {
            "manager": {"planner": 5, "researcher": 2},
            "planner": {"coder": 10},
            "coder": {"analyst": 3}
        }
        
        # 에러 없이 렌더링되는지 확인
        self.ui.update_collaboration_heatmap(mock_matrix)
        renderable = self.ui.render()
        self.assertIsNotNone(renderable)

if __name__ == '__main__':
    unittest.main()
