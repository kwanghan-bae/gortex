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

    def calculate_model_scores(self) -> Dict[str, float]:
        """
        각 모델의 종합 점수를 계산합니다 (0~100).
        성공률(60%) + 응답 속도(20%) + 비용 효율(20%)
        """
        summary = self.get_summary(days=30)
        scores = {}
        
        for model, stats in summary.items():
            # 1. 성공률 점수 (60점 만점)
            success_score = stats["success_rate"] * 0.6
            
            # 2. 레이턴시 점수 (20점 만점, 낮을수록 좋음)
            # 기준: 2초 이내면 만점, 10초 이상이면 0점
            latency = stats["avg_latency"]
            latency_score = max(0, 20 * (1 - (latency - 2000) / 8000)) if latency > 2000 else 20
            
            # 3. 가성비 점수 (20점 만점, 토큰당 성공 여부)
            # 클라우드 모델(Gemini)은 토큰 가중치를 더 높게 줌
            is_local = "ollama" in model.lower()
            token_weight = 1.0 if is_local else 5.0
            efficiency = (stats["successes"] * 1000) / (stats["total_tokens"] * token_weight + 1)
            # 정규화 (대략적인 수치)
            cost_score = min(20, efficiency * 2)
            
            scores[model] = round(success_score + latency_score + cost_score, 2)
            
        return scores

    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """시스템 진화(코드 수정) 이력을 반환합니다."""
        if not os.path.exists(self.stats_path):
            return []

        history = []
        try:
            with open(self.stats_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    if data.get("agent") == "evolution" and data.get("success"):
                        history.append(data)
            return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"Failed to get evolution history: {e}")
            return []

    def apply_immediate_feedback(self, model_id: str, success: bool, weight: float = 1.0):
        """
        작업 성공/실패 시 해당 모델의 평판에 즉각적인 가중치를 부여합니다. (RLHF-lite)
        가상의 로그를 생성하여 다음 점수 계산 시 즉시 반영되도록 합니다.
        """
        # 아주 큰 토큰 값이나 레이턴시를 페널티/보상으로 사용하여 점수 조정 유도
        penalty_tokens = 50000 if not success else 0
        self.record_interaction(
            agent_name="feedback_loop",
            model_id=model_id,
            success=success,
            tokens=int(penalty_tokens * weight),
            latency_ms=10000 if not success else 0,
            metadata={"type": "immediate_feedback"}
        )
