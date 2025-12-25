import unittest
from gortex.core.observer import GortexObserver
from gortex.utils.collaboration_viz import CollaborationVisualizer

class TestCollaborationViz(unittest.TestCase):
    def setUp(self):
        self.observer = GortexObserver()
        self.viz = CollaborationVisualizer(self.observer)
        # Clear log for test
        self.observer.log_path = "tests/temp_trace.jsonl"
        with open(self.observer.log_path, "w") as f:
            f.write("")

    def tearDown(self):
        import os
        if os.path.exists(self.observer.log_path):
            os.remove(self.observer.log_path)

    def test_matrix_generation(self):
        # 1. 인과 관계가 있는 로그 생성
        # Event 1: User (root)
        e1 = self.observer.log_event("user", "chat", {"msg": "fix bug"})
        # Event 2: Planner (caused by User)
        e2 = self.observer.log_event("planner", "plan", {"steps": []}, cause_id=e1)
        # Event 3: Coder (caused by Planner)
        self.observer.log_event("coder", "code", {"file": "a.py"}, cause_id=e2)
        # Event 4: Coder again (caused by Planner)
        self.observer.log_event("coder", "code", {"file": "b.py"}, cause_id=e2)
        
        # 2. 매트릭스 추출
        matrix = self.viz.generate_matrix()
        
        # planner -> coder 호출이 2회 있어야 함
        self.assertEqual(matrix["planner"]["coder"], 2)
        # user -> planner 호출이 1회
        self.assertEqual(matrix["user"]["planner"], 1)

if __name__ == "__main__":
    unittest.main()
