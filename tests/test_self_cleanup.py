import unittest
import os
import time
import shutil
from unittest import mock
from gortex.agents.analyst.base import AnalystAgent
from gortex.utils.tools import safe_bulk_delete

class TestSelfCleanup(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_logs"
        self.backup_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 노후 파일 생성 (10일 전)
        self.old_file = os.path.join(self.backup_dir, "old_backup.bak")
        with open(self.old_file, "w") as f: f.write("dummy data")
        # 수정 시간 강제 변경
        ten_days_ago = time.time() - (10 * 24 * 60 * 60)
        os.utime(self.old_file, (ten_days_ago, ten_days_ago))
        
        # 2. 보호 대상 파일 생성
        self.protected_file = os.path.join(self.test_dir, "experience_shard.json")
        with open(self.protected_file, "w") as f: f.write("{}")

        self.analyst = AnalystAgent()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_evaluate_artifact_value(self):
        """노후 파일 감지 로직 테스트"""
        candidates = self.analyst.evaluate_artifact_value(directory=self.test_dir)
        paths = [c["path"] for c in candidates]
        self.assertIn(self.old_file, paths)
        self.assertNotIn(self.protected_file, paths)

    def test_safe_bulk_delete_protection(self):
        """핵심 파일 보호 기능 테스트"""
        files = [self.old_file, self.protected_file]
        result = safe_bulk_delete(files)
        
        self.assertIn(self.old_file, result["success"])
        self.assertIn(self.protected_file, result["protected"])
        self.assertTrue(os.path.exists(self.protected_file))

    def test_perform_autonomous_cleanup(self):
        """통합 청소 루틴 실행 테스트"""
        # Analyst가 test_dir를 바라보도록 환경 설정
        with mock.patch.object(self.analyst, 'evaluate_artifact_value', 
                               return_value=[{"path": self.old_file, "size_kb": 1.0}]):
            res = self.analyst.perform_autonomous_cleanup()
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["deleted_count"], 1)
            self.assertFalse(os.path.exists(self.old_file))

if __name__ == '__main__':
    unittest.main()