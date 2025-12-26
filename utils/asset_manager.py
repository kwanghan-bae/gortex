import json
import os
import logging

logger = logging.getLogger("GortexAssetManager")

class SynapticAssetManager:
    """
    아이콘, 메시지 템플릿, 테마 정보 등 정적 에셋을 중앙 관리하는 시스템.
    """
    _instance = None
    _asset_path = "assets.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SynapticAssetManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        # 기본 에셋 데이터
        self.assets = {
            "icons": {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "💡",
                "robot": "🤖",
                "user": "👤",
                "security": "🛡️",
                "achievement": "🏆",
                "rocket": "🚀",
                "honey_bee": "🐝"
            },
            "agent_labels": {
                "manager": "SUPERVISOR",
                "coder": "DEVELOPER",
                "planner": "ARCHITECT",
                "analyst": "STRATEGIST",
                "researcher": "INVESTIGATOR"
            },
            "templates": {
                "reboot": "[MENTAL REBOOT] 에이전트의 사고가 재설정되었습니다.",
                "deploy_start": "🚀 원격 배포 파이프라인을 가동합니다..."
            }
        }
        self._load_from_disk()
        self._initialized = True

    def _load_from_disk(self):
        if os.path.exists(self._asset_path):
            try:
                with open(self._asset_path, "r", encoding='utf-8') as f:
                    disk_assets = json.load(f)
                    self.assets.update(disk_assets)
            except Exception as e:
                logger.error(f"Failed to load assets: {e}")

    def save(self):
        """현재 에셋을 디스크에 저장"""
        try:
            with open(self._asset_path, "w", encoding='utf-8') as f:
                json.dump(self.assets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save assets: {e}")

    def get_icon(self, key: str, default: str = "") -> str:
        return self.assets["icons"].get(key, default)

    def get_agent_label(self, agent_name: str) -> str:
        return self.assets["agent_labels"].get(agent_name.lower(), agent_name.upper())

    def get_template(self, key: str) -> str:
        return self.assets["templates"].get(key, "")
