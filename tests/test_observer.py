import unittest
from unittest.mock import MagicMock, patch
import json
import os
from gortex.core.observer import GortexObserver

class TestGortexObserver(unittest.TestCase):
    def setUp(self):
        # 테스트용 임시 로그 경로 사용
        self.test_log_path = "logs/test_trace.jsonl"
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)
        self.observer = GortexObserver(log_path=self.test_log_path)

    def tearDown(self):
        if os.path.exists(self.test_log_path):
            os.remove(self.test_log_path)

    def test_log_event_and_causality(self):
        """이벤트 로깅 및 인과 관계(causal graph) 구축 테스트"""
        event1_id = self.observer.log_event("manager", "decision", {"value": "A"})
        event2_id = self.observer.log_event("planner", "plan", {"target": "A"}, cause_id=event1_id)
        
        graph = self.observer.get_causal_graph()
        
        # 노드 존재 확인
        node_ids = [n["id"] for n in graph["nodes"]]
        self.assertIn(event1_id, node_ids)
        self.assertIn(event2_id, node_ids)
        
        # 엣지 연결 확인 (from/to)
        edge_exists = False
        for edge in graph["edges"]:
            if edge["from"] == event1_id and edge["to"] == event2_id:
                edge_exists = True
                break
        self.assertTrue(edge_exists)

    def test_log_content(self):
        """로그 파일 내용 검증"""
        self.observer.log_event("coder", "edit", {"file": "test.py"})
        
        with open(self.test_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        self.assertTrue(len(lines) > 0)
        last_log = json.loads(lines[-1])
        self.assertEqual(last_log["agent"], "coder")
        self.assertEqual(last_log["event"], "edit")

if __name__ == '__main__':
    unittest.main()