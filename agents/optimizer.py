import json
import os
import logging
import re
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
                lines = f.readlines()
                for line in lines[-limit:]:
                    logs.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
        return logs

    def analyze_performance(self) -> Optional[Dict[str, Any]]:
        """로그 분석 및 개선 제안 도출"""
        logs = self._read_recent_logs()
        if not logs:
            return {"analysis": "분석할 로그 데이터가 충분하지 않습니다. 개선 제안: 로그 축적 필요", "improvement_task": None, "priority": "low"}

        compact_logs = []
        for l in logs:
            compact_logs.append({
                "agent": l.get("agent"),
                "event": l.get("event"),
                "latency": l.get("latency_ms"),
                "error": l.get("payload") if l.get("event") == "error" else None
            })

        prompt = f"""너는 Gortex v1.0의 성능 최적화 전문가다.
아래의 최근 시스템 로그(JSON)를 분석하여 개선안을 도출하라.
[Recent Logs]
{json.dumps(compact_logs, ensure_ascii=False, indent=2)}

결과는 반드시 다음 JSON 형식을 따라라:
{{
    "analysis": "문제점 분석 결과. 개선 제안: 상세 내용",
    "improvement_task": "구체적인 작업 지시문",
    "priority": "high/medium/low"
}}
"""
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {
                "response_mime_type": "application/json"
            })
            json_text = response.text
            json_match = re.search(r'{{.*}}', json_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"analysis": f"분석: {json_text}. 개선 제안: 모니터링 강화", "improvement_task": None, "priority": "medium"}
        except Exception as e:
            logger.error(f"Optimizer analysis failed: {e}")
            return {"analysis": f"오류 발생: {e}. 개선 제안: API 키 점검", "improvement_task": None, "priority": "low"}

    def detect_stuck_state(self, messages: List[Any]) -> bool:
        """에이전트가 동일한 행동을 3회 이상 반복하는지 감지"""
        if not messages or len(messages) < 6:
            return False
        
        tool_calls = []
        for m in messages[-6:]:
            try:
                content = m[1] if isinstance(m, tuple) else m.content
                if "Executed" in str(content):
                    tool_calls.append(str(content))
            except:
                continue
                
        if len(tool_calls) >= 3:
            # 최근 3개가 완전히 동일한지 확인
            if tool_calls[-1] == tool_calls[-2] == tool_calls[-3]:
                return True
        return False

def optimizer_node(state: GortexState) -> Dict[str, Any]:
    """Optimizer 노드 엔트리 포인트"""
    agent = OptimizerAgent()
    
    # 교착 상태 감지
    if agent.detect_stuck_state(state["messages"]):
        logger.warning("🔄 Stuck state detected! Triggering Mental Reboot...")
        return {
            "thought": "에이전트 교착 상태 감지. 시스템 재부팅(Mental Reboot) 수행.",
            "messages": [("system", "⚠️ [MENTAL REBOOT] 에이전트의 반복적 교착 상태가 감지되어 내부 사고 상태를 재설정합니다. 기존의 해결 방식을 버리고 새로운 관점에서 접근하십시오.")],
            "next_node": "summarizer"
        }

    res = agent.analyze_performance()
    updates = {
        "thought": f"시스템 로그 분석 결과: {res.get('analysis')}",
        "messages": [("ai", f"🚀 [System Optimization Report]\n\n{res.get('analysis')}")],
        "next_node": "manager"
    }
    if res.get("improvement_task"):
        updates["messages"].append(("system", f"최적화 전문가의 제안: {res.get('improvement_task')}"))
    return updates
