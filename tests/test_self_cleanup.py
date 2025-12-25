import unittest
import os
import time
import shutil
from gortex.agents.analyst import AnalystAgent

class TestSelfCleanup(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_cleanup"
        os.makedirs(self.test_dir, exist_ok=True)
        self.backup_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # 1. 노후 파일 생성 (10일 전)
        self.old_file = os.path.join(self.backup_dir, "old_backup.bak")
        with open(self.old_file, "w") as f:
            f.write("dummy data")
        # 수정 시간 강제 변경
        ten_days_ago = time.time() - (10 * 24 * 60 * 60)
        os.utime(self.old_file, (ten_days_ago, ten_days_ago))
        
        # 2. 보호 대상 파일 생성
        self.protected_file = os.path.join(self.test_dir, "experience_shard.json")
        with open(self.protected_file, "w") as f:
            f.write("{}")

        self.analyst = AnalystAgent()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cleanup_logic(self):
        # Mocking cleanup logic execution (since AnalystAgent might be complex)
        # Here we simulate the logic directly or call a utility function if exposed
        from gortex.utils.tools import safe_bulk_delete
        
        # Simulate detection of old files
        to_delete = [self.old_file]
        res = safe_bulk_delete(to_delete)

        self.assertFalse(os.path.exists(self.old_file))
        self.assertIn(self.old_file, res["success"])

    def test_protection_logic(self):
        from gortex.utils.tools import safe_bulk_delete
        res = safe_bulk_delete([self.protected_file])
        self.assertTrue(os.path.exists(self.protected_file))
        self.assertIn(self.protected_file, res["protected"])

if __name__ == "__main__":
    unittest.main()
