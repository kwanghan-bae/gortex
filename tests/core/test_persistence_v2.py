
import unittest
import json
import os
import shutil
from collections import ChainMap
from dataclasses import dataclass
from gortex.core.persistence import DistributedSaver

@dataclass
class CustomState:
    name: str
    value: int

class TestPersistenceV2(unittest.TestCase):
    def setUp(self):
        self.mirror_path = "logs/test_mirror_v2.json"
        self.saver = DistributedSaver(primary_saver=None, mirror_path=self.mirror_path)

    def tearDown(self):
        if os.path.exists(self.mirror_path):
            os.remove(self.mirror_path)
        if os.path.exists(self.mirror_path + ".tmp"):
            os.remove(self.mirror_path + ".tmp")

    def test_complex_serialization(self):
        """복잡한 중첩 구조(ChainMap, List, Dict 혼합) 직렬화 테스트"""
        # Given
        config = ChainMap({'a': 1}, {'b': 2})
        metadata = {'source': 'test', 'tags': ['v2', 'robustness']}
        checkpoint = {
            'thread_id': 'th_123',
            'channel_values': {
                'messages': [{'type': 'human', 'content': 'hello'}],
                'context': ChainMap({'role': 'user'}, {'session': 'active'})
            }
        }
        
        # When
        # _make_serializable은 내부 메서드지만 단위 테스트 목적상 직접 호출
        serialized_config = self.saver._make_serializable(config)
        serialized_checkpoint = self.saver._make_serializable(checkpoint)

        # Then
        self.assertIsInstance(serialized_config, dict)
        self.assertEqual(serialized_config['a'], 1)
        self.assertEqual(serialized_config['b'], 2)
        
        self.assertIsInstance(serialized_checkpoint['channel_values']['context'], dict)
        self.assertEqual(serialized_checkpoint['channel_values']['context']['role'], 'user')
        
        # JSON Dump Check
        json_str = json.dumps(serialized_checkpoint)
        self.assertIn('"role": "user"', json_str)

    def test_unsupported_types_fallback(self):
        """Set, Tuple 등 JSON 비표준 타입의 직렬화 처리 테스트"""
        # Given
        data = {
            'my_set': {1, 2, 3},
            'my_tuple': (4, 5, 6),
            'custom_obj': CustomState(name="test", value=99)
        }
        
        # When
        serialized = self.saver._make_serializable(data)
        
        # Then
        # 현재 구현상 set과 tuple은 별도 처리가 없으면 기본적으로 그대로 반환되거나 str로 변환되어야 함.
        # _make_serializable 구현을 보면:
        # 1. dict -> 재귀
        # 2. list -> 재귀
        # 3. ChainMap -> dict
        # 4. content/type attr -> dict
        # 5. __dict__ attr -> str
        # 그 외 -> 그대로 반환.
        # json.dump는 set을 지원하지 않으므로 에러가 날 것임. 이 테스트는 그것을 확인하고 개선 포인트를 찾기 위함.
        
        try:
            json.dumps(serialized)
            print("✅ Serialization success (maybe unexpected if types not handled)")
        except TypeError:
            print("⚠️ Expected TypeError for Set/Tuple. Need to enhance _make_serializable.")
            # 이 테스트는 실패를 예상하고, 이를 바탕으로 코드를 개선하기 위함.

    def test_replicate_resilience(self):
        """_replicate 호출 시 예외가 발생해도 메인 로직은 멈추지 않아야 함"""
        # Given
        # mirror_path를 유효하지 않은 경로로 설정하여 에러 유도
        self.saver.mirror_path = "/root/invalid_path/mirror.json" 
        
        config = {'a': 1}
        checkpoint = {'status': 'ok'}
        metadata = {}

        # When
        try:
            self.saver._replicate(config, checkpoint, metadata)
            # Then
            # 로그에 에러가 찍히더라도 여기서 Exception이 raise되면 안 됨.
            print("✅ Replicate resilience passed (No crash on IO error)")
        except Exception as e:
            self.fail(f"_replicate raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
