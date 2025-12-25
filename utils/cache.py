import os
import hashlib
import json
import logging
from typing import Optional, Any, Dict

logger = logging.getLogger("GortexCache")

class GortexCache:
    """
    파일 기반의 단순 JSON 캐시 매니저 (Redis 의존성 제거됨).
    'logs/cache.json' 파일에 데이터를 영구 저장합니다.
    """
    _instance = None
    _CACHE_FILE = "logs/cache.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexCache, cls).__new__(cls)
            cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        self.memory: Dict[str, Any] = {}
        
        # 캐시 디렉토리 확보
        os.makedirs(os.path.dirname(self._CACHE_FILE), exist_ok=True)
        
        # 파일에서 로드
        if os.path.exists(self._CACHE_FILE):
            try:
                with open(self._CACHE_FILE, "r", encoding="utf-8") as f:
                    self.memory = json.load(f)
                logger.info(f"✅ Loaded cache from {self._CACHE_FILE} ({len(self.memory)} items)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load cache file: {e}")
                self.memory = {}
        else:
            logger.info("🆕 Created new local cache instance")

    def _save_to_disk(self):
        """캐시 내용을 파일에 저장 (Atomic Write 권장되나 여기선 단순 구현)"""
        try:
            with open(self._CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save cache to disk: {e}")

    def _get_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def set(self, prefix: str, key: str, value: Any, expire: int = 86400):
        """데이터를 캐시에 저장 (expire는 파일 기반이라 무시됨)"""
        full_key = f"gortex:{prefix}:{self._get_hash(key)}"
        self.memory[full_key] = value
        self._save_to_disk()

    def get(self, prefix: str, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        full_key = f"gortex:{prefix}:{self._get_hash(key)}"
        return self.memory.get(full_key)
