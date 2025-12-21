import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger("GortexEfficiency")

class EfficiencyMonitor:
    """
    Gortex 시스템의 효율성을 추적하고 분석하는 모듈.
    모델별 토큰 비용, 응답 속도, 작업 성공률 등을 기록합니다.
    """
    def __init__(self, stats_path: str = "logs/efficiency_stats.jsonl"):
        self.stats_path = stats_path
        os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)

    def record_interaction(self, 
                           agent_name: str, 
                           model_id: str, 
                           success: bool, 
                           tokens: int, 
                           latency_ms: int, 
                           energy_consumed: int = 5,
                           metadata: Dict[str, Any] = None):
        """단일 상호작용 데이터를 기록합니다."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "model": model_id,
            "success": success,
            "tokens": tokens,
            "latency_ms": latency_ms,
            "energy_consumed": energy_consumed,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.stats_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to record efficiency data: {e}")

    def get_summary(self, days: int = 7) -> Dict[str, Any]:
        """최근 N일간의 성능 요약을 계산합니다."""
        if not os.path.exists(self.stats_path):
            return {}

        summary = {} # model -> stats
        cutoff = datetime.now() - timedelta(days=days)
        
        try:
            with open(self.stats_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    ts = datetime.fromisoformat(data["timestamp"])
                    if ts < cutoff:
                        continue
                    
                    m = data["model"]
                    if m not in summary:
                        summary[m] = {"calls": 0, "successes": 0, "total_tokens": 0, "total_latency": 0}
                    
                    summary[m]["calls"] += 1
                    if data["success"]:
                        summary[m]["successes"] += 1
                    summary[m]["total_tokens"] += data["tokens"]
                    summary[m]["total_latency"] += data["latency_ms"]

            # 평균값 계산
            for m in summary:
                s = summary[m]
                s["success_rate"] = (s["successes"] / s["calls"]) * 100 if s["calls"] > 0 else 0
                s["avg_latency"] = s["total_latency"] / s["calls"] if s["calls"] > 0 else 0
                s["avg_tokens"] = s["total_tokens"] / s["calls"] if s["calls"] > 0 else 0
                
            return summary
        except Exception as e:
            logger.error(f"Failed to analyze efficiency stats: {e}")
            return {}
