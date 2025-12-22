import unittest
import os
import shutil
from gortex.utils.tools import backup_file_with_rotation

class TestBackupRotation(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_data.json"
        self.backup_dir = "logs/test_backups"
        with open(self.test_file, "w") as f:
            f.write('{"test": "data"}')
        os.makedirs(self.backup_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def test_rotation_limit(self):
        """백업 파일이 지정된 개수(max_versions)를 넘지 않는지 테스트"""
        max_v = 3
        for i in range(5):
            backup_file_with_rotation(self.test_file, self.backup_dir, max_versions=max_v)
            # 순식간에 돌면 timestamp가 겹칠 수 있으므로 약간의 시차 부여 (파일 이름 유니크성 확보)
            import time
            time.sleep(1.1)
            
        backups = [f for f in os.listdir(self.backup_dir) if f.startswith(self.test_file)]
        self.assertEqual(len(backups), max_v)

if __name__ == '__main__':
    unittest.main()
