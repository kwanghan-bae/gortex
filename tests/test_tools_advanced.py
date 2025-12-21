import unittest
import os
import shutil
import zipfile
from gortex.utils.tools import archive_project_artifacts, compress_directory

class TestGortexToolsAdvanced(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_artifacts"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f: f.write("content1")
        with open(os.path.join(self.test_dir, "file2.txt"), "w") as f: f.write("content2")
        self.archive_base = "logs/archives/test_project/v1.0.0"

    def tearDown(self):
        if os.path.exists(self.test_dir): shutil.rmtree(self.test_dir)
        if os.path.exists("logs/archives/test_project"): shutil.rmtree("logs/archives/test_project")
        if os.path.exists("test_backup.zip"): os.remove("test_backup.zip")

    def test_archive_project_artifacts(self):
        """파일 아카이빙 로직이 정확한 경로로 파일을 이동시키는지 테스트"""
        files = [os.path.join(self.test_dir, "file1.txt"), os.path.join(self.test_dir, "file2.txt")]
        res = archive_project_artifacts("test_project", "v1.0.0", files)
        
        self.assertIn("Archived 2 artifacts", res)
        self.assertTrue(os.path.exists(os.path.join(self.archive_base, "file1.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.archive_base, "file2.txt")))

    def test_compress_directory(self):
        """디렉토리 압축 기능 및 제외 패턴(ignore) 정상 작동 테스트"""
        # 제외할 폴더 생성
        os.makedirs(os.path.join(self.test_dir, "venv"), exist_ok=True)
        with open(os.path.join(self.test_dir, "venv/exclude.txt"), "w") as f: f.write("skip")
        
        output_zip = "test_backup.zip"
        res = compress_directory(self.test_dir, output_zip, ignore_patterns=["venv"])
        
        self.assertIn("✅", res)
        self.assertTrue(os.path.exists(output_zip))
        
        # 압축 파일 내용 확인
        with zipfile.ZipFile(output_zip, 'r') as zipf:
            file_list = zipf.namelist()
            self.assertIn("file1.txt", file_list)
            self.assertNotIn("venv/exclude.txt", file_list)

if __name__ == '__main__':
    unittest.main()
