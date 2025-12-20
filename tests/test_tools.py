import unittest
import os
import shutil
from gortex.utils.tools import write_file, execute_shell

class TestGortexTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_workspace"
        self.backup_dir = "logs/backups"
        os.makedirs(self.test_dir, exist_ok=True)
        # 백업 디렉토리 정리
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # 테스트 후 백업 디렉토리는 남겨두거나 정리 (여기서는 정리)
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

    def test_atomic_write_with_backup(self):
        """파일 덮어쓰기 시 백업 생성 확인"""
        target_file = os.path.join(self.test_dir, "test.txt")
        
        # 1. 초기 파일 생성
        write_file(target_file, "Initial Content")
        self.assertTrue(os.path.exists(target_file))
        
        # 2. 덮어쓰기
        write_file(target_file, "New Content")
        
        # 3. 내용 확인
        with open(target_file, 'r') as f:
            self.assertEqual(f.read(), "New Content")
            
        # 4. 백업 확인
        self.assertTrue(os.path.exists(self.backup_dir))
        backups = os.listdir(self.backup_dir)
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].startswith("test.txt"))

    def test_execute_shell_security(self):
        """위험한 명령어 차단 확인"""
        # rm -rf 시도
        result = execute_shell("rm -rf /")
        self.assertIn("Security Alert", result)
        self.assertIn("Execution blocked", result)
        
        # 정상 명령 시도
        result = execute_shell("echo 'Hello'")
        self.assertIn("Hello", result)
        self.assertIn("Exit Code: 0", result)

    def test_execute_shell_timeout(self):
        """타임아웃 확인 (sleep 명령 이용)"""
        # 1초 타임아웃에 2초 sleep
        result = execute_shell("sleep 2", timeout=1)
        self.assertIn("timed out", result)

    def test_file_cache_consistency(self):
        """파일 캐시 정합성(해시 비교) 테스트"""
        from gortex.utils.tools import get_file_hash
        target_file = os.path.join(self.test_dir, "cache_test.py")
        
        # 1. 파일 생성 및 해시 추출
        content = "print('hello')"
        write_file(target_file, content)
        actual_hash = get_file_hash(target_file)
        
        # 2. 캐시 상태 모사
        file_cache = {target_file: actual_hash}
        
        # 3. 파일 변경 후 정합성 깨짐 확인
        with open(target_file, 'w') as f:
            f.write("print('modified')")
        
        new_actual_hash = get_file_hash(target_file)
        self.assertNotEqual(file_cache[target_file], new_actual_hash)

if __name__ == '__main__':
    unittest.main()
