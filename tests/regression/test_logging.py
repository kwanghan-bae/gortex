
import unittest
import os
import shutil
import logging

class TestLoggingIntegrity(unittest.TestCase):
    def test_log_directory_and_file_creation(self):
        """test_log_directory_and_file_creation: 로그 디렉토리와 파일이 정상적으로 생성되고 쓰기 가능한지 테스트"""
        log_dir = "logs_test_regression"
        log_file = os.path.join(log_dir, "gortex_test.log")
        
        # Clean state
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir)
            
        try:
            # 1. Directory Creation
            os.makedirs(log_dir, exist_ok=True)
            self.assertTrue(os.path.exists(log_dir))
            
            # 2. File Handler Setup check
            logger = logging.getLogger("TestLogger")
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_file, encoding='utf-8')
            logger.addHandler(handler)
            
            # 3. Write Test
            test_msg = "Regression Test Log Message"
            logger.info(test_msg)
            handler.close()
            
            # 4. Verification
            self.assertTrue(os.path.exists(log_file))
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(test_msg, content)
                
        finally:
            # Cleanup
            if os.path.exists(log_dir):
                shutil.rmtree(log_dir)

if __name__ == '__main__':
    unittest.main()
