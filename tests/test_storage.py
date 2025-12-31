import unittest
import os
import json
import asyncio
import shutil
from typing import Any, Dict
from unittest.mock import MagicMock, patch
from tests.contracts import BaseStorageContract
from gortex.core.storage import SqliteStorage, RedisStorage

try:
    import redis
except ImportError:
    redis = None

class TestSqliteStorage(BaseStorageContract, unittest.TestCase):
    def setUp(self):
        self.db_path = "/tmp/test_gortex_sqlite.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.storage = SqliteStorage(db_path=self.db_path)

    def tearDown(self):
        # Close connection to allow file deletion
        self.storage.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def get_storage(self):
        return self.storage

    def test_langgraph_serialization(self):
        """
        Verify that complex nested objects (simulating LangGraph state)
        can be serialized/deserialized without data loss.
        """
        complex_state = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi", "metadata": {"tokens": 10}}
            ],
            "agent_state": {
                "memory": {"short_term": ["a", "b"], "long_term": {"k": "v"}},
                "active": True
            },
            "steps": 10,
            "cost": 0.005
        }
        
        # Serialize
        serialized = json.dumps(complex_state)
        self.storage.set("state:complex", serialized)
        
        # Deserialize
        retrieved = self.storage.get("state:complex")
        assert retrieved is not None
        deserialized = json.loads(retrieved)
        
        self.assertEqual(deserialized, complex_state)
        self.assertEqual(deserialized["messages"][1]["metadata"]["tokens"], 10)

    async def _async_access(self, key, val):
        self.storage.set(key, val)
        await asyncio.sleep(0.01)
        return self.storage.get(key)

    def test_async_concurrency(self):
        """
        Test concurrent access to SqliteStorage via asyncio.
        Although SqliteStorage is sync, it might be called from async context.
        """
        async def run_test():
            tasks = []
            for i in range(10):
                tasks.append(self._async_access(f"concurrent:{i}", str(i)))

            results = await asyncio.gather(*tasks)
            for i, res in enumerate(results):
                self.assertEqual(res, str(i))

        asyncio.run(run_test())

@unittest.skipIf(redis is None, "Redis not installed")
class TestRedisStorage(BaseStorageContract, unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        # Mock Redis dictionary-like behavior for get/set/delete
        self._data = {}

        def mock_get(key):
            return self._data.get(key)
        
        def mock_set(key, value, ex=None):
            self._data[key] = value
            return True

        def mock_delete(key):
            if key in self._data:
                del self._data[key]
            return 1

        def mock_keys(pattern):
            # Simple wildcard implementation for mocking
            import fnmatch
            return fnmatch.filter(self._data.keys(), pattern)

        self.mock_redis.get.side_effect = mock_get
        self.mock_redis.set.side_effect = mock_set
        self.mock_redis.delete.side_effect = mock_delete
        self.mock_redis.keys.side_effect = mock_keys

        self.storage = RedisStorage(client=self.mock_redis)

    def get_storage(self):
        return self.storage

if __name__ == "__main__":
    unittest.main()
