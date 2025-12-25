import unittest
from gortex.utils.economy import EconomyManager
from gortex.utils.efficiency_monitor import EfficiencyMonitor
from gortex.utils.healing_memory import SelfHealingMemory
from gortex.utils.indexer import SynapticIndexer
from gortex.utils.log_vectorizer import SemanticLogSearch
import os
import shutil

class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_utils_test"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_economy_manager(self):
        em = EconomyManager()
        state = {"agent_economy": {}}
        em.record_success(state, "test_agent", quality_score=1.5)
        self.assertIn("test_agent", state["agent_economy"])
        self.assertGreater(state["agent_economy"]["test_agent"]["points"], 100)

    def test_efficiency_monitor(self):
        stats_path = os.path.join(self.test_dir, "stats.jsonl")
        em = EfficiencyMonitor(stats_path=stats_path)
        em.record_interaction("agent", "model", True, 100, 500)
        self.assertTrue(os.path.exists(stats_path))
        summary = em.get_summary()
        self.assertIn("model", summary)

    def test_healing_memory(self):
        mem_path = os.path.join(self.test_dir, "healing.json")
        hm = SelfHealingMemory(storage_path=mem_path)
        hm.learn("Error: fail", {"action": "retry"})
        sol = hm.find_solution("Error: fail")
        self.assertEqual(sol["action"], "retry")

    def test_indexer(self):
        # Create a dummy python file
        py_file = os.path.join(self.test_dir, "dummy.py")
        with open(py_file, "w") as f:
            f.write("def foo():\n    pass\nclass Bar:\n    pass")

        indexer = SynapticIndexer(root_dir=self.test_dir)
        indexer.index_path = os.path.join(self.test_dir, "index.json")
        indexer.scan_project()

        results = indexer.search("foo")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["name"], "foo")

    def test_log_vectorizer(self):
        log_path = os.path.join(self.test_dir, "trace.jsonl")
        with open(log_path, "w") as f:
            f.write('{"agent": "coder", "event": "error", "payload": "syntax error", "timestamp": "2023-01-01"}\n')

        searcher = SemanticLogSearch(log_path=log_path)
        searcher.load_and_index()
        results = searcher.search_similar_cases("syntax error")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["payload"], "syntax error")

if __name__ == "__main__":
    unittest.main()
