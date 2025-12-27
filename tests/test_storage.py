import unittest
import os
import json
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch
from core.storage import StorageProvider, SqliteStorage, RedisStorage

class TestSqliteStorage(unittest.TestCase):
    def setUp(self):
        # Create a temp file for sqlite db
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.storage = SqliteStorage(db_path=self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_set_get(self):
        """Test basic set and get operations."""
        self.storage.set("test:key", "test_value")
        val = self.storage.get("test:key")
        self.assertEqual(val, "test_value")

    def test_get_nonexistent(self):
        """Test getting a non-existent key."""
        val = self.storage.get("non:existent")
        self.assertIsNone(val)

    def test_delete(self):
        """Test delete operation."""
        self.storage.set("test:del", "val")
        self.storage.delete("test:del")
        self.assertIsNone(self.storage.get("test:del"))

    def test_keys(self):
        """Test keys pattern matching (simple prefix)."""
        self.storage.set("prefix:1", "v1")
        self.storage.set("prefix:2", "v2")
        self.storage.set("other:1", "v3")
        
        # SQLite GLOB or LIKE can be used. 
        # For simplicity, our abstraction might assume glob-style '*'
        keys = self.storage.keys("prefix:*")
        self.assertIn("prefix:1", keys)
        self.assertIn("prefix:2", keys)
        self.assertNotIn("other:1", keys)

    def test_set_nx(self):
        """Test set with nx=True (Not Exist)."""
        # First set should succeed
        res1 = self.storage.set("lock:1", "1", nx=True)
        self.assertTrue(res1)
        
        # Second set should fail
        res2 = self.storage.set("lock:1", "2", nx=True)
        self.assertFalse(res2)
        
        # Value should remain "1"
        self.assertEqual(self.storage.get("lock:1"), "1")

class TestRedisStorage(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        self.storage = RedisStorage(client=self.mock_redis)

    def test_set_get(self):
        self.storage.set("key", "val")
        self.mock_redis.set.assert_called()
        
        self.storage.get("key")
        self.mock_redis.get.assert_called_with("key")

    def test_set_nx(self):
        self.storage.set("key", "val", nx=True)
        self.mock_redis.set.assert_called_with("key", "val", ex=None, nx=True)
