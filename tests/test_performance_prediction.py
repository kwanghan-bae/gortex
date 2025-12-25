import unittest
import os
from gortex.utils.efficiency_monitor import EfficiencyMonitor

class TestPerformancePrediction(unittest.TestCase):
    def setUp(self):
        self.stats_path = "tests/temp_perf_stats.jsonl"
        self.monitor = EfficiencyMonitor(stats_path=self.stats_path)
        # Seed data
        self.monitor.record_interaction("coder", "gemini", True, 1000, 2000)
        self.monitor.record_interaction("coder", "gemini", True, 1200, 2200)

    def tearDown(self):
        if os.path.exists(self.stats_path):
            os.remove(self.stats_path)
        health_path = self.stats_path.replace("stats.jsonl", "health_history.jsonl")
        if os.path.exists(health_path):
            os.remove(health_path)

    def test_predict_resource_usage(self):
        pred = self.monitor.predict_resource_usage("coder")
        self.assertAlmostEqual(pred["avg_tokens"], 1100, delta=100)
        self.assertAlmostEqual(pred["avg_latency_ms"], 2100, delta=100)

    def test_health_history(self):
        self.monitor.record_session_health(95.0)
        hist = self.monitor.get_health_history()
        self.assertGreaterEqual(len(hist), 1)
        self.assertEqual(hist[0]["score"], 95.0)

if __name__ == "__main__":
    unittest.main()
