import json
import os
import logging
from typing import List, Dict, Any, Optional
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState

logger = logging.getLogger("GortexOptimizer")

class OptimizerAgent:
    """
    관측 로그(trace.jsonl)를 분석하여 시스템 성능 병목이나 반복되는 오류를 찾아내고
    개선안을 도출하는 자기 개선 에이전트.
    """
    def __init__(self, log_path: str = "logs/trace.jsonl"):
        self.log_path = log_path
        self.auth = GortexAuth()

    def _read_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """최근 로그를 읽어옴"""
        logs = []
        if not os.path.exists(self.log_path):
            return []
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                # 마지막 limit 줄만 읽기 (단순화된 방식)
                lines = f.readlines()
                for line in lines[-limit:]:
                    logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
        
        return logs

    def analyze_performance(self) -> Optional[str]:
        """로그 분석 및 개선 제안 도출"""
        logs = self._read_recent_logs()
        if not logs:
            return "분석할 로그 데이터가 충분하지 않습니다."

        # 로그 데이터를 텍스트로 요약 (용량 절약)
        compact_logs = []
        for l in logs:
            compact_logs.append({
                "agent": l.get("agent"),
                "event": l.get("event"),
                "latency": l.get("latency_ms"),
                "error": l.get("payload") if l.get("event") == "error" else None
            })

        prompt = f"""너는 Gortex v1.0의 성능 최적화 전문가다.
아래의 최근 시스템 로그(JSON)를 분석하여 다음을 수행하라:
1. 반복적으로 발생하는 오류(error) 패턴이 있는가?
2. 특정 에이전트나 도구에서 심각한 지연(latency)이 발생하는가?
3. 시스템 효율성이나 안정성을 높이기 위한 구체적인 개선 코드 또는 설정 변경안을 제시하라.

[Recent Logs]
{json.dumps(compact_logs, ensure_ascii=False, indent=2)}

응답은 한국어로 작성하고, '문제점', '원인 분석', '개선 제안'의 형식을 갖춰라.
"""

        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return response.text
        except Exception as e:
            logger.error(f"Optimizer analysis failed: {e}")
            return f"최적화 분석 중 오류 발생: {e}"

def optimizer_node(state: GortexState) -> Dict[str, Any]:
    """Optimizer 노드 엔트리 포인트"""
    agent = OptimizerAgent()
    analysis = agent.analyze_performance()
    
    return {
        "messages": [("ai", f"🚀 [System Optimization Report]\n\n{analysis}")],
        "next_node": "manager"
    }
