import unittest
import os
from gortex.utils.cache import GortexCache

class TestGortexCache(unittest.TestCase):
    def test_singleton(self):
        """싱글톤 패턴 확인"""
        cache1 = GortexCache()
        cache2 = GortexCache()
        self.assertIs(cache1, cache2)

    def test_set_get_fallback(self):
        """로컬 메모리 폴백 동작 확인"""
        cache = GortexCache()
        # Redis가 없다고 가정 (또는 실제 Redis가 있어도 동작함)
        cache.set("test", "hello", {"data": 123})
        val = cache.get("test", "hello")
        self.assertEqual(val["data"], 123)

    def test_hash_collision_avoidance(self):
        """다른 키에 대해 다른 해시가 생성되는지 간접 확인"""
        cache = GortexCache()
        cache.set("test", "key1", "val1")
        cache.set("test", "key2", "val2")
        self.assertEqual(cache.get("test", "key1"), "val1")
        self.assertEqual(cache.get("test", "key2"), "val2")

if __name__ == '__main__':
    unittest.main()
