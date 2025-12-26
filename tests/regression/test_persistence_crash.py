
import unittest
import json
import os
import shutil
from collections import ChainMap
from gortex.core.persistence import DistributedSaver

class UnserializableObject:
    """JSON 직렬화가 불가능한 객체 흉내 (Runtime 등)"""
    def __repr__(self):
        return "<BAD_OBJECT>"

class TestPersistenceCrashRegression(unittest.TestCase):
    def setUp(self):
        self.mirror_path = "logs/test_crash_mirror.json"
        self.saver = DistributedSaver(mirror_path=self.mirror_path)

    def tearDown(self):
        if os.path.exists(self.mirror_path):
            os.remove(self.mirror_path)
        if os.path.exists(self.mirror_path + ".tmp"):
            os.remove(self.mirror_path + ".tmp")

    def test_runtime_object_survival(self):
        """test_runtime_object_survival: Runtime 객체가 들어와도 죽지 않고 문자열로 저장되어야 함"""
        bad_obj = UnserializableObject()
        config = {"configurable": {"thread_id": "1"}}
        
        # 주입: 체크포인트 데이터 내부에 직렬화 불가능한 객체 포함
        checkpoint = {
            "v": 1,
            "ts": "2024-01-01",
            "channel_values": {
                "some_key": "some_value",
                "dangerous_field": bad_obj  # <--- CRASH POINT
            }
        }
        
        # 실행: _replicate 호출 (내부적으로 json.dump 수행)
        try:
            self.saver._replicate(config, checkpoint, {})
        except Exception as e:
            self.fail(f"Persistent layer crashed with unserializable object: {e}")

        # 검증: 파일이 생성되었고, bad_obj가 문자열로 변환되어 저장되었는지 확인
        self.assertTrue(os.path.exists(self.mirror_path))
        with open(self.mirror_path, 'r') as f:
            data = json.load(f)
            saved_bad_obj = data['checkpoint']['channel_values']['dangerous_field']
            self.assertIn("BAD_OBJECT", saved_bad_obj) # __repr__ or str() result
            
    def test_scalar_type_preservation(self):
        """test_scalar_type_preservation: 기본 타입(int)은 문자열로 변환되지 않아야 함 (이전 버그 회귀 방지)"""
        checkpoint = {
            "v": 1,
            "integer_val": 123,
            "float_val": 3.14,
            "bool_val": True
        }
        self.saver._replicate({}, checkpoint, {})
        
        with open(self.mirror_path, 'r') as f:
            data = json.load(f)
            saved_checkpoint = data['checkpoint']
            self.assertIsInstance(saved_checkpoint['integer_val'], int)
            self.assertEqual(saved_checkpoint['integer_val'], 123)
            self.assertIsInstance(saved_checkpoint['bool_val'], bool)

if __name__ == '__main__':
    unittest.main()
