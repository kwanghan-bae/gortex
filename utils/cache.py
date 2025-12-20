import os
import hashlib
import json
import redis
import logging
from typing import Optional, Any

logger = logging.getLogger("GortexCache")

class GortexCache:
    """
    Redis를 사용한 싱글톤 캐시 매니저.
    Redis 연결 실패 시 로컬 메모리(dict)로 폴백합니다.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexCache, cls).__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            logger.info(f"✅ Redis connected at {redis_url}")
            self.is_redis = True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed ({e}). Falling back to local memory.")
            self.client = {}
            self.is_redis = False

    def _get_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def set(self, prefix: str, key: str, value: Any, expire: int = 86400):
        """데이터를 캐시에 저장 (기본 24시간)"""
        full_key = f"gortex:{prefix}:{self._get_hash(key)}"
        json_val = json.dumps(value, ensure_ascii=False)
        
        if self.is_redis:
            self.client.setex(full_key, expire, json_val)
        else:
            self.client[full_key] = json_val

    def get(self, prefix: str, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        full_key = f"gortex:{prefix}:{self._get_hash(key)}"
        
        if self.is_redis:
            val = self.client.get(full_key)
        else:
            val = self.client.get(full_key)
            
        if val:
            try:
                return json.loads(val)
            except Exception:
                return val
        return None
