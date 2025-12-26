import unittest
import os
import shutil
from gortex.utils.tools import (
    write_file, get_file_hash, read_file, execute_shell,
    verify_patch_integrity, safe_bulk_delete
)

class TestTools(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_test_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        self.backup_dir = "logs/backups"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # Clean up backup if created during test
        if os.path.exists(self.backup_dir):
            for f in os.listdir(self.backup_dir):
                if "test_file.txt" in f:
                    os.remove(os.path.join(self.backup_dir, f))

    def test_write_read_file(self):
        content = "Hello, Gortex!"
        write_file(self.test_file, content)

        self.assertTrue(os.path.exists(self.test_file))
        read_content = read_file(self.test_file)
        self.assertEqual(read_content, content)

    def test_file_hash(self):
        content = "Hash me"
        write_file(self.test_file, content)

        hash1 = get_file_hash(self.test_file)
        self.assertTrue(len(hash1) > 0)

        write_file(self.test_file, "New content")
        hash2 = get_file_hash(self.test_file)
        self.assertNotEqual(hash1, hash2)

    def test_execute_shell(self):
        output = execute_shell("echo 'hello shell'")
        self.assertIn("hello shell", output)
        self.assertIn("Exit Code: 0", output)

    def test_execute_shell_forbidden(self):
        output = execute_shell("rm -rf /")
        self.assertIn("Security Alert", output)

    def test_verify_patch_integrity_syntax_error(self):
        py_file = os.path.join(self.test_dir, "bad.py")
        write_file(py_file, "def bad_func():\nprint('missing indent')")

        result = verify_patch_integrity(py_file)
        self.assertFalse(result["success"])
        self.assertIn("Syntax Error", result["reason"])

    def test_safe_bulk_delete(self):
        f1 = os.path.join(self.test_dir, "f1.txt")
        f2 = os.path.join(self.test_dir, "experience.json") # Protected
        write_file(f1, "data")
        write_file(f2, "protected data")

        result = safe_bulk_delete([f1, f2])

        self.assertFalse(os.path.exists(f1))
        self.assertTrue(os.path.exists(f2))
        self.assertIn(f1, result["success"])
        self.assertIn(f2, result["protected"])

if __name__ == "__main__":
    unittest.main()
