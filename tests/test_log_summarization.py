import unittest
import os
import json
import shutil
from unittest.mock import MagicMock, patch
from gortex.core.observer import GortexObserver
from gortex.agents.analyst.base import AnalystAgent

class TestLogSummarization(unittest.TestCase):
    def setUp(self):
        self.log_path = "tests/test_trace_summary.jsonl"
        self.summary_path = "logs/trace_summary.md"
        self.archive_dir = "logs/archives"
        
        # 1. 테스트용 대량 로그 생성
        with open(self.log_path, "w") as f:
            for i in range(10):
                f.write(json.dumps({
                    "id": f"ev_{i}", "agent": "coder", "event": "node_complete", 
                    "payload": "Fixed a bug", "timestamp": "2025-12-23T00:00:00"
                }) + "\n")

        self.observer = GortexObserver(log_path=self.log_path)
        self.analyst = AnalystAgent()
        self.analyst.backend = MagicMock()

    def tearDown(self):
        if os.path.exists(self.log_path): os.remove(self.log_path)
        if os.path.exists(self.summary_path): os.remove(self.summary_path)
        # Archive dir cleanup is risky, let's just leave it or clean specifically
        
    def test_summarize_system_trace(self):
        """로그 요약본 생성 및 파일 저장 테스트"""
        self.analyst.backend.generate.return_value = "## Milestone: Refactoring complete."
        
        summary = self.analyst.summarize_system_trace(log_path=self.log_path)
        
        self.assertIn("Refactoring", summary)
        self.assertTrue(os.path.exists(self.summary_path))

    def test_archive_and_reset_logs(self):
        """로그 아카이빙 및 원본 리셋 테스트"""
        # 파일이 비어있지 않음을 먼저 확인
        self.assertGreater(os.path.getsize(self.log_path), 0)
        
        archive_path = self.observer.archive_and_reset_logs()
        
        # 1. 아카이브 파일(ZIP) 생성 확인
        self.assertTrue(archive_path.endswith(".zip"))
        self.assertTrue(os.path.exists(archive_path))
        
        # 2. 원본 파일 초기화 확인
        self.assertEqual(os.path.getsize(self.log_path), 0)
        
        # Cleanup archive
        if os.path.exists(archive_path): os.remove(archive_path)

if __name__ == '__main__':
    unittest.main()
