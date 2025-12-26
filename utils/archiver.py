import os
import json
import zipfile
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("GortexArchiver")

class IntelligenceArchiver:
    """
    Gortex의 모든 지능 자산(지식, 도구, 모델 설정)을 
    영구히 보존하고 상속 가능한 패키지로 변환함.
    """
    def __init__(self, archive_dir: str = "logs/archives/intelligence"):
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)

    def create_neural_seed(self, version: str) -> str:
        """현재 시스템의 모든 지능을 하나의 'Neural Seed' ZIP 파일로 패키징함"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_path = os.path.join(self.archive_dir, f"Gortex_Seed_{version}_{timestamp}.zip")
        
        # 패키징 대상 목록
        assets = {
            "memory": "logs/memory",
            "tools": "core/tools/forged.py",
            "agents": "agents/auto_spawned_",
            "registry": "logs/system_config.json",
            "constitution": "docs/CONSTITUTION.md"
        }
        
        try:
            with zipfile.ZipFile(seed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 1. 지식 샤드 (Experience Shards)
                if os.path.exists("logs/memory"):
                    for f in os.listdir("logs/memory"):
                        if f.endswith(".json"):
                            zipf.write(os.path.join("logs/memory", f), arcname=f"memory/{f}")
                
                # 2. 제작된 도구 (Forged Tools)
                if os.path.exists("gortex/core/tools/forged.py"):
                    zipf.write("gortex/core/tools/forged.py", arcname="tools/forged.py")
                
                # 3. 자가 증식된 에이전트들
                if os.path.exists("agents"):
                    for f in os.listdir("agents"):
                        if f.startswith("auto_spawned_") and f.endswith(".py"):
                            zipf.write(os.path.join("agents", f), arcname=f"agents/{f}")
                
                # 4. 메타데이터 및 헌장
                if os.path.exists("docs/CONSTITUTION.md"):
                    zipf.write("docs/CONSTITUTION.md", arcname="constitution.md")
                
                # 5. 시드 매니페스트 생성
                manifest = {
                    "origin_version": version,
                    "generated_at": datetime.now().isoformat(),
                    "total_rules": self._count_rules(),
                    "total_tools": self._count_tools()
                }
                zipf.writestr("manifest.json", json.dumps(manifest, indent=2))
                
            logger.info(f"🌌 Intelligence Seed created: {seed_path}")
            return seed_path
        except Exception as e:
            logger.error(f"Archiving failed: {e}")
            return ""

    def _count_rules(self) -> int:
        from gortex.core.evolutionary_memory import EvolutionaryMemory
        return len(EvolutionaryMemory().memory)

    def _count_tools(self) -> int:
        from gortex.core.tools.registry import tool_registry
        return len(tool_registry.list_tools())

# 글로벌 인스턴스
archiver = IntelligenceArchiver()
