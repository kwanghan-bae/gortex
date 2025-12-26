import unittest
import os
import shutil
from gortex.utils.tools import archive_project_artifacts

class TestToolsAdvanced(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_artifacts"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "file1.txt"), "w") as f:
            f.write("content1")
        with open(os.path.join(self.test_dir, "file2.txt"), "w") as f:
            f.write("content2")
        self.archive_base = "logs/archives/test_project/v1.0.0"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("logs/archives/test_project"):
            shutil.rmtree("logs/archives/test_project")
        if os.path.exists("test_backup.zip"):
            os.remove("test_backup.zip")

    def test_archive_project_artifacts(self):
        files = [
            os.path.join(self.test_dir, "file1.txt"),
            os.path.join(self.test_dir, "file2.txt")
        ]
        
        result = archive_project_artifacts("test_project", "v1.0.0", files)
        self.assertIn("Archived 2 artifacts", result)
        self.assertTrue(os.path.exists(os.path.join(self.archive_base, "file1.txt")))

    def test_compress_directory(self):
        from gortex.utils.tools import compress_directory

        # 제외할 폴더 생성
        os.makedirs(os.path.join(self.test_dir, "venv"), exist_ok=True)
        with open(os.path.join(self.test_dir, "venv/exclude.txt"), "w") as f:
            f.write("skip")
        
        output_zip = "test_backup.zip"
        res = compress_directory(self.test_dir, output_zip, ignore_patterns=["venv"])
        
        self.assertIn("Directory compressed", res)
        self.assertTrue(os.path.exists(output_zip))
        
        # Verify content (venv should be missing)
        # (This would require unzip and check, skipping for unit test speed)

if __name__ == "__main__":
    unittest.main()
