import unittest
import os
import json
import shutil
from datetime import datetime
from utils.efficiency_monitor import EfficiencyMonitor

class TestEfficiencyMonitorHealth(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_logs"
        self.stats_path = os.path.join(self.test_dir, "efficiency_stats.jsonl")
        self.health_path = os.path.join(self.test_dir, "health_history.jsonl")
        os.makedirs(self.test_dir, exist_ok=True)
        self.monitor = EfficiencyMonitor(stats_path=self.stats_path)
        # Manually set health_path for testing to avoid writing to real logs
        self.monitor.health_path = self.health_path 

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_record_and_retrieve_session_health(self):
        # 1. Record health scores
        self.monitor.record_session_health(85.5, session_id="sess_001")
        self.monitor.record_session_health(90.0, session_id="sess_002")
        
        # 2. Check file existence
        self.assertTrue(os.path.exists(self.health_path))
        
        # 3. Retrieve history
        history = self.monitor.get_health_history(limit=5)
        self.assertEqual(len(history), 2)
        # Assuming we implement it to return sorted by timestamp descending (newest first)
        self.assertEqual(history[0]["score"], 90.0)
        self.assertEqual(history[1]["score"], 85.5)
        self.assertEqual(history[0]["session_id"], "sess_002")
        
    def test_get_health_history_limit(self):
        for i in range(15):
            self.monitor.record_session_health(float(i), session_id=f"sess_{i}")
            
        history = self.monitor.get_health_history(limit=10)
        self.assertEqual(len(history), 10)
        # Assuming reverse order (newest first)
        self.assertEqual(history[0]["score"], 14.0)
