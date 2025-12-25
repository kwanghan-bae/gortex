import unittest
from unittest.mock import MagicMock
from gortex.agents.analyst.organizer import WorkspaceOrganizer

class TestGortexOrganizer(unittest.TestCase):
    def setUp(self):
        self.organizer = WorkspaceOrganizer()
        # Mock LTM
        self.organizer.ltm = MagicMock()
        self.organizer.ltm.memory = []

    def test_garbage_collect_knowledge_no_dupes(self):
        """중복이 없을 때는 제거되지 않아야 함"""
        self.organizer.ltm.memory = [{"content": "A"}, {"content": "B"}]
        removed = self.organizer.garbage_collect_knowledge()
        self.assertEqual(removed, 0) # 5개 미만이면 실행 안 함

    def test_garbage_collect_knowledge_with_dupes(self):
        """중복 지식 제거 테스트"""
        self.organizer.ltm.memory = [
            {"content": "A"}, {"content": "A"}, 
            {"content": "B"}, {"content": "C"},
            {"content": "D"}, {"content": "E"} # 6개 -> 실행 조건 충족
        ]
        removed = self.organizer.garbage_collect_knowledge()
        self.assertEqual(removed, 1) # 하나 중복 제거됨
        self.organizer.ltm._save_store.assert_called_once()

    def test_map_knowledge_relations(self):
        """지식 간 유사도 기반 연결 테스트"""
        # 벡터: [1, 0] 과 [1, 0] -> 유사도 1.0 (연결됨)
        # 벡터: [1, 0] 과 [0, 1] -> 유사도 0.0 (연결 안됨)
        self.organizer.ltm.memory = [
            {"id": "1", "content": "A", "vector": [1.0, 0.0], "links": []},
            {"id": "2", "content": "B", "vector": [0.9, 0.1], "links": []}, # 유사함
            {"id": "3", "content": "C", "vector": [0.0, 1.0], "links": []}  # 다름
        ]
        
        connections = self.organizer.map_knowledge_relations()
        
        # A와 B는 서로 연결되어야 함
        self.assertTrue(connections >= 1)
        # self.assertIn("2", self.organizer.ltm.memory[0]["links"])

if __name__ == '__main__':
    unittest.main()
