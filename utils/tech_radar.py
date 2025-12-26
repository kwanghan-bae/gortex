import json
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger("GortexTechRadar")

class TechRadar:
    """
    Gortex 시스템이 사용하는 기술(라이브러리, 모델, 패턴)의 
    성과를 추적하고 장기적인 채택/폐기 여부를 결정함.
    """
    def __init__(self, radar_path: str = "tech_radar.json"):
        self.radar_path = radar_path
        self.technologies = self._load_radar()

    def _load_radar(self) -> Dict[str, Any]:
        if os.path.exists(self.radar_path):
            with open(self.radar_path, "r", encoding='utf-8') as f:
                return json.load(f)
        return {"technologies": {}, "adoption_candidates": []}

    def _save_radar(self):
        with open(self.radar_path, "w", encoding='utf-8') as f:
            json.dump(self.technologies, f, ensure_ascii=False, indent=2)

    def record_tech_usage(self, tech_name: str, success: bool, performance_score: float):
        """특정 기술의 사용 성과를 기록함"""
        if tech_name not in self.technologies["technologies"]:
            self.technologies["technologies"][tech_name] = {
                "first_seen": datetime.now().isoformat(),
                "use_count": 0,
                "success_rate": 1.0,
                "avg_performance": performance_score,
                "status": "assess" # assess, trial, adopt, hold
            }
        
        tech = self.technologies["technologies"][tech_name]
        tech["use_count"] += 1
        # 지수 이동 평균으로 성공률 및 성능 갱신
        alpha = 0.2
        tech["success_rate"] = (1 - alpha) * tech["success_rate"] + alpha * (1.0 if success else 0.0)
        tech["avg_performance"] = (1 - alpha) * tech["avg_performance"] + alpha * performance_score
        
        # 상태 자동 전이 로직
        if tech["use_count"] > 20 and tech["success_rate"] > 0.9:
            tech["status"] = "adopt"
        elif tech["success_rate"] < 0.4:
            tech["status"] = "hold"
            
        self._save_radar()

    def get_strategic_advice(self) -> str:
        """현재 테크 레이더 상태를 기반으로 전략적 제언 생성"""
        adopts = [name for name, info in self.technologies["technologies"].items() if info["status"] == "adopt"]
        holds = [name for name, info in self.technologies["technologies"].items() if info["status"] == "hold"]
        
        advice = "### 📡 Gortex Tech Radar Strategic Advice\n"
        advice += f"- **Adopted Standard**: {', '.join(adopts) if adopts else 'Stabilizing...'}\n"
        advice += f"- **Deprecation Warning**: {', '.join(holds) if holds else 'None'}\n"
        return advice

# 글로벌 인스턴스
radar = TechRadar()
