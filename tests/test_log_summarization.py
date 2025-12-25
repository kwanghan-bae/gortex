import unittest
import os
from gortex.utils.log_summarizer import LogSummarizer

class TestLogSummarization(unittest.TestCase):
    def setUp(self):
        self.log_path = "tests/temp_logs.jsonl"
        self.summary_path = "tests/temp_summary.json"
        with open(self.log_path, "w") as f:
            f.write('{"timestamp": "2024-01-01T12:00:00", "event": "start"}\n')

        self.summarizer = LogSummarizer(log_path=self.log_path, summary_path=self.summary_path)

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.summary_path):
            os.remove(self.summary_path)
        # Archive dir cleanup is risky, let's just leave it or clean specifically

    def test_summarize(self):
        self.summarizer.summarize()
        self.assertTrue(os.path.exists(self.summary_path))

    def test_archive_logs(self):
        archive_path = self.summarizer.archive_logs()
        self.assertTrue(os.path.exists(archive_path))
        
        # Cleanup archive
        if os.path.exists(archive_path):
            os.remove(archive_path)

if __name__ == '__main__':
    unittest.main()
