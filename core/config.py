import json
import os
import logging
from typing import Any, Dict

logger = logging.getLogger("GortexConfig")

class GortexConfig:
    """
    Gortex 시스템의 전역 설정을 동적으로 관리하는 싱글톤 클래스.
    """
    _instance = None
    _config_path = "gortex_config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexConfig, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.settings: Dict[str, Any] = {
            "log_level": "INFO",
            "default_model": "gemini-1.5-flash",
            "reasoning_model": "gemini-3-flash-preview",
            "max_coder_iterations": 30,
            "theme": "classic",
            "notifications_enabled": True,
            "api_call_limit_per_min": 15,
            "web_dashboard_port": 8000
        }
        self._load_from_disk()
        self._initialized = True

    def _load_from_disk(self):
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding='utf-8') as f:
                    disk_settings = json.load(f)
                    self.settings.update(disk_settings)
                logger.info("✅ Configuration loaded from disk.")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")

    def save(self):
        """현재 설정을 디스크에 영구 저장"""
        try:
            with open(self._config_path, "w", encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            logger.info("✅ Configuration saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        self.settings[key] = value
        self.save()

    def list_all(self) -> Dict[str, Any]:
        return self.settings.copy()
