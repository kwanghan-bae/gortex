import json
import os
import tempfile
import unittest
from gortex.utils.log_vectorizer import SemanticLogSearch

class TestSemanticLogSearch(unittest.TestCase):
    def setUp(self):
        self.log_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.jsonl')
        entries = [
            {"timestamp": "t1", "event": "error", "agent": "coder", "payload": {"msg": "Fail"}},
            {"timestamp": "t2", "event": "info", "agent": "planner", "payload": {"msg": "Skip"}},
            {"timestamp": "t3", "event": "node_complete", "agent": "manager", "payload": {"msg": "Done"}}
        ]
        for entry in entries:
            self.log_file.write(json.dumps(entry) + "\n")
        self.log_file.flush()
        self.log_path = self.log_file.name

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def test_load_and_index_and_search(self):
        searcher = SemanticLogSearch(log_path=self.log_path)
        searcher.load_and_index()
        self.assertEqual(len(searcher.index), 2)
        results = searcher.search_similar_cases("manager node")
        self.assertTrue(any(item["agent"] == "manager" for item in results))

if __name__ == '__main__':
    unittest.main()
