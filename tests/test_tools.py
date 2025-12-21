import os
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from gortex.utils.tools import (
    archive_project_artifacts,
    apply_patch,
    compress_directory,
    deep_integrity_check,
    execute_shell,
    get_changed_files,
    get_file_hash,
    list_files,
    read_file,
    write_file,
    write_file_with_hash,
)

class TestGortexTools(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_tool_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Hello World\n" * 10)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists("test_write.txt"):
            os.remove("test_write.txt")
        for cache_dir in ("logs/backups", "logs/versions", "logs/archives"):
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)

    def test_execute_shell_blacklist(self):
        """블랙리스트 명령어 차단 테스트"""
        result = execute_shell("rm -rf /")
        self.assertIn("Security Alert", result)
        self.assertIn("Execution blocked", result)

    def test_read_file_limit(self):
        """파일 읽기 라인 제한 테스트"""
        # 10줄 파일, limit 5 -> 5줄 + truncated msg
        content = read_file(self.test_file, limit=5)
        # truncated 메시지가 추가되므로 라인 수는 5보다 클 수 있음
        self.assertTrue(len(content.splitlines()) >= 5)
        self.assertIn("(truncated)", content)

    def test_read_file_offset(self):
        """파일 읽기 오프셋 테스트"""
        content = read_file(self.test_file, offset=5, limit=5)
        self.assertEqual(len(content.splitlines()), 5)

    def test_write_file_atomic(self):
        """원자적 파일 쓰기 테스트"""
        status = write_file("test_write.txt", "New Content")
        self.assertIn("Success", status)
        with open("test_write.txt", "r") as f:
            self.assertEqual(f.read(), "New Content")

    def test_list_files_ignore(self):
        """파일 목록 조회 및 무시 패턴 테스트"""
        files = list_files(".")
        self.assertNotIn(".git", files)
        self.assertIn(self.test_file, files)

    def test_execute_shell_success_with_truncation(self):
        """execute_shell이 stdout과 파일 시스템 변화를 보고"""
        mock_result = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        with patch("gortex.utils.tools.subprocess.run", return_value=mock_result), \
             patch("gortex.utils.tools.os.listdir", side_effect=[[], []]):
            output = execute_shell("echo hi")
        self.assertIn("Exit Code: 0", output)
        self.assertIn("STDOUT", output)
        self.assertNotIn("Error", output)

    def test_execute_shell_timeout(self):
        """서브프로세스 타임아웃을 검증"""
        with patch("gortex.utils.tools.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="sleep", timeout=1)):
            output = execute_shell("sleep 10", timeout=1)
        self.assertIn("timed out", output)

    def test_archive_project_artifacts_moves_files(self):
        """로그 아카이브 폴더로 파일 이동"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "artifact.txt")
        with open(file_path, "w") as f:
            f.write("data")
        result = archive_project_artifacts("testproj", "v1", [file_path])
        self.assertIn("Archived 1 artifacts", result)
        self.assertFalse(os.path.exists(file_path))
        shutil.rmtree(temp_dir)
        shutil.rmtree(os.path.join("logs", "archives", "testproj"), ignore_errors=True)

    def test_compress_directory_creates_zip(self):
        """디렉토리를 압축하고 ignore 패턴은 건너뜀"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "data.txt")
        with open(file_path, "w") as f:
            f.write("content")
        output_zip = os.path.join(temp_dir, "archive.zip")
        result = compress_directory(temp_dir, output_zip, ignore_patterns=["ignore_me"])
        self.assertIn("compressed to", result)
        self.assertTrue(os.path.exists(output_zip))
        shutil.rmtree(temp_dir)

    def test_archive_missing_files(self):
        """존재하지 않는 파일이라도 에러 없이 처리"""
        result = archive_project_artifacts("testproj", "v1", ["missing.txt"])
        self.assertIn("Archived 0 artifacts", result)

    def test_compress_respects_ignore(self):
        """ignore 패턴 이름을 가진 파일은 압축에서 제외"""
        temp_dir = tempfile.mkdtemp()
        ignored = os.path.join(temp_dir, "ignore_me.txt")
        kept = os.path.join(temp_dir, "keep.txt")
        with open(ignored, "w") as f:
            f.write("skip")
        with open(kept, "w") as f:
            f.write("keep")
        output_zip = os.path.join(temp_dir, "archive2.zip")
        result = compress_directory(temp_dir, output_zip, ignore_patterns=["ignore_me"])
        self.assertTrue(os.path.exists(output_zip))
        import zipfile as zf
        with zf.ZipFile(output_zip) as archive:
            members = archive.namelist()
        self.assertIn("keep.txt", members)
        self.assertNotIn("ignore_me.txt", members)
        shutil.rmtree(temp_dir)


    def test_get_file_hash_computes_value(self):
        path = "hash_test.txt"
        with open(path, "w") as f:
            f.write("hash-me")
        file_hash = get_file_hash(path)
        self.assertEqual(len(file_hash), 32)
        os.remove(path)

    def test_write_file_with_hash_records_hash(self):
        path = "hash_output.txt"
        status, new_hash = write_file_with_hash(path, "content")
        self.assertIn("Successfully", status)
        self.assertEqual(get_file_hash(path), new_hash)
        os.remove(path)

    def test_deep_integrity_check_finds_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate = os.path.join(tmpdir, "track.txt")
            with open(candidate, "w") as f:
                f.write("track")
            updated_cache, changed = deep_integrity_check(tmpdir, {})
            rel_path = os.path.relpath(candidate, tmpdir)
            self.assertIn(rel_path, changed)
            self.assertEqual(updated_cache[rel_path], get_file_hash(candidate))

    def test_get_changed_files_detects_modification(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "mod.txt")
            with open(target, "w") as f:
                f.write("old")
            rel_path = os.path.relpath(target, tmpdir)
            cache = {rel_path: get_file_hash(target)}
            with open(target, "w") as f:
                f.write("new")
            changed = get_changed_files(tmpdir, cache)
            self.assertIn(rel_path, changed)

    def test_apply_patch_replaces_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "file.txt")
            with open(target, "w") as f:
                f.write("line1\nline2\nline3\n")
            result = apply_patch(target, 2, 2, "patched")
            self.assertIn("Successfully", result)
            with open(target, "r") as f:
                lines = f.read().splitlines()
            self.assertEqual(lines[1], "patched")


if __name__ == '__main__':
    unittest.main()
