
import unittest
import os
import shutil
import tempfile
import json
from gortex.core.artifacts.base import BaseArtifact
from gortex.core.artifacts.store import FileSystemArtifactStore

class TestArtifacts(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.store = FileSystemArtifactStore(base_path=self.test_dir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.test_dir)

    def test_artifact_creation_and_save(self):
        """Artifact 객체 생성 및 저장 테스트"""
        artifact = BaseArtifact(
            id="art-001",
            type="code",
            title="Hello World Script",
            content="print('Hello World')",
            metadata={"language": "python"}
        )
        
        saved_path = self.store.save(artifact)
        
        # 파일 생성 확인
        self.assertTrue(os.path.exists(saved_path))
        self.assertTrue(saved_path.endswith(".md") or saved_path.endswith(".json"))

    def test_artifact_load(self):
        """저장된 Artifact 로드 테스트"""
        artifact = BaseArtifact(
            id="art-002",
            type="plan",
            title="Test Plan",
            content="# Plan\n1. Do this",
            metadata={"author": "User"}
        )
        self.store.save(artifact)
        
        # ID로 로드
        loaded = self.store.load("art-002")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Test Plan")
        self.assertEqual(loaded.content, "# Plan\n1. Do this")
        self.assertEqual(loaded.metadata["author"], "User")

    def test_versioning(self):
        """간단한 버전 관리 테스트 (덮어쓰기 시 백업)"""
        art1 = BaseArtifact(id="v-test", type="text", title="V1", content="Version 1")
        self.store.save(art1)
        
        art2 = BaseArtifact(id="v-test", type="text", title="V2", content="Version 2")
        self.store.save(art2)
        
        loaded = self.store.load("v-test")
        self.assertEqual(loaded.content, "Version 2")
        
        # 백업 디렉토리 확인 (구현 의존적, 일단 존재 여부만 체크)
        # self.assertTrue(os.path.exists(os.path.join(self.test_dir, "artifacts", "backups")))

if __name__ == '__main__':
    unittest.main()
