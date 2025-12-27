from abc import ABC, abstractmethod
from typing import Optional, List, Any
import time
import os
import sqlite3
import glob
import logging

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger("Storage")

class StorageProvider(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set(self, key: str, value: str, ex: Optional[int] = None, nx: bool = False) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def keys(self, pattern: str) -> List[str]:
        pass

class RedisStorage(StorageProvider):
    def __init__(self, client=None, url: str = "redis://localhost:6379/0"):
        if client:
            self.client = client
        elif redis:
            self.client = redis.from_url(url, decode_responses=True)
        else:
            raise ImportError("Redis package is not installed.")

    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None, nx: bool = False) -> bool:
        res = self.client.set(key, value, ex=ex, nx=nx)
        return bool(res)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    def keys(self, pattern: str) -> List[str]:
        return self.client.keys(pattern)

class SqliteStorage(StorageProvider):
    def __init__(self, db_path: str = ".gortex/storage.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at REAL
                )
            """)

    def _cleanup_expired(self, key: str):
        # Lazy check helper: if key exists but expired, delete it.
        # This is a bit specific to 'get', but we do it inside get query usually.
        # Here we just do it proactively if we can, but simpler to check on access.
        pass

    def get(self, key: str) -> Optional[str]:
        now = time.time()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value, expires_at FROM kv WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        if row:
            val, expires_at = row
            if expires_at and expires_at < now:
                self.delete(key)
                return None
            return val
        return None

    def set(self, key: str, value: str, ex: Optional[int] = None, nx: bool = False) -> bool:
        now = time.time()
        expires_at = (now + ex) if ex else None
        
        with self.conn:
            if nx:
                # Check existence and expiration
                cursor = self.conn.cursor()
                cursor.execute("SELECT expires_at FROM kv WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    # Exists. Check if expired.
                    existing_expires = row[0]
                    if existing_expires and existing_expires < now:
                        # Expired, so we can overwrite effectively treating it as 'not exist'
                        # But standard Redis NX might strictly fail if key exists regardless of expiry?
                        # Redis behavior: if key exists (even if expired but not yet collected), NX fails? 
                        # Actually Redis expires keys actively or lazily. If it's expired, it's treated as non-existent.
                        pass 
                    else:
                        return False # Exists and valid

            # Upsert or Insert
            # If NX passed (didn't return False), we insert/replace
            self.conn.execute("""
                INSERT OR REPLACE INTO kv (key, value, expires_at)
                VALUES (?, ?, ?)
            """, (key, value, expires_at))
            return True

    def delete(self, key: str) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM kv WHERE key = ?", (key,))

    def keys(self, pattern: str) -> List[str]:
        # Translate glob pattern to SQL LIKE?
        # Redis keys use glob-style: *, ?, [].
        # SQL LIKE uses % and _.
        # Simple conversion: * -> %
        sql_pattern = pattern.replace("*", "%").replace("?", "_")
        
        # Also clean up expired keys while scanning?
        # For now, just return valid ones.
        now = time.time()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT key FROM kv 
            WHERE key LIKE ? AND (expires_at IS NULL OR expires_at > ?)
        """, (sql_pattern, now))
        return [row[0] for row in cursor.fetchall()]
