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
1. 반복적으로 발생하는 오류(error) 패턴이 있는가? 특히 '429 Quota Exhausted'나 타임아웃을 확인하라.
2. 특정 에이전트나 도구에서 심각한 지연(latency)이 발생하는가?
3. 시스템 효율성이나 안정성을 높이기 위한 구체적인 개선 코드 또는 설정 변경안을 제시하라.

[분석 가이드라인]
- 만약 API 할당량 초과가 잦다면: "core/auth.py의 switch_account 메서드 내 wait_time 범위를 10~20초로 늘리거나, 특정 노드에서 더 가벼운 모델(flash-lite)을 쓰도록 수정하라"와 같은 구체적인 태스크를 생성하라.
- 만약 특정 도구에서 에러가 반복된다면: 해당 도구의 예외 처리 로직을 보강하는 태스크를 생성하라.

[태스크 생성 사례 (Few-shot)]
- 사례 1: 429 에러 빈발 시
  "improvement_task": "core/auth.py 파일을 수정하여 switch_account 함수의 wait_time 지터 범위를 random.uniform(10.0, 20.0)으로 상향 조정하라."
- 사례 2: 파일 읽기 권한 에러 반복 시
  "improvement_task": "utils/tools.py의 read_file 함수에 PermissionError 예외 처리 로직을 추가하고 에러 발생 시 사용자에게 chmod 제안 메시지를 출력하도록 수정하라."

[Recent Logs]

{json.dumps(compact_logs, ensure_ascii=False, indent=2)}

결과는 반드시 다음 JSON 형식을 따라라:
{{
    "analysis": "문제점 및 원인 분석 결과 (한국어)",
    "improvement_task": "에이전트가 즉시 수행할 수 있는 구체적인 파일 기반 작업 지시문 (예: 'core/auth.py의 switch_account 메서드 내 wait_time 범위를 10~20초로 조정')",
    "priority": "high/medium/low"
}}
"""


        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {
                "response_mime_type": "application/json"
            })
            
            # 응답에서 JSON 추출 시도 (강화된 로직)
            json_text = response.text
            json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 파싱 실패 시 기본값
            return {
                "analysis": json_text,
                "improvement_task": None,
                "priority": "medium"
            }
        except Exception as e:
            logger.error(f"Optimizer analysis failed: {e}")
            return {
                "analysis": f"최적화 분석 중 오류 발생: {e}",
                "improvement_task": None,
                "priority": "low"
            }

import re


def optimizer_node(state: GortexState) -> Dict[str, Any]:
    """Optimizer 노드 엔트리 포인트"""
    agent = OptimizerAgent()
    res = agent.analyze_performance()
    
    updates = {
        "thought": f"시스템 로그 분석 결과: {res.get('analysis')}",
        "messages": [("ai", f"🚀 [System Optimization Report]\n\n{res.get('analysis')}")],
        "next_node": "manager"
    }
    
    # 개선 작업이 있다면 메시지에 추가하여 Manager가 다음 태스크로 인식하게 함
    if res.get("improvement_task"):
        updates["messages"].append(("system", f"최적화 전문가의 제안: {res.get('improvement_task')}"))
        
    return updates

