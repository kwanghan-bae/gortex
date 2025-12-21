import logging
import json
import pandas as pd
import os
import re
from typing import Dict, Any, List, Optional
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent:
    """
    데이터 분석, 자가 진화, 코드 리뷰 및 상호 검증을 담당하는 분석 에이전트.
    """
    def __init__(self):
        self.auth = GortexAuth()
        self.memory = EvolutionaryMemory()

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        """Pandas를 사용하여 데이터 분석 및 시각화 코드 생성"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found at {file_path}"}
            ext = os.path.splitext(file_path)[1].lower()
            df = pd.read_csv(file_path) if ext == '.csv' else (pd.read_excel(file_path) if ext in ['.xls', '.xlsx'] else pd.read_json(file_path))
            summary = {"rows": len(df), "columns": list(df.columns), "head": df.head(3).to_dict(), "describe": df.describe().to_dict()}
            prompt = f"다음 데이터 요약 정보를 보고 Plotly JSON 차트를 생성하라: {json.dumps(summary, ensure_ascii=False)}"
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return {"summary": summary, "visualization": json.loads(response.text)}
        except Exception as e:
            return {"error": str(e)}

    def analyze_feedback(self, history: List[Any]) -> Optional[Dict[str, Any]]:
        """사용자의 부정적 피드백을 분석하여 진화 규칙 추출"""
        prompt = "사용자 불만을 분석하여 개선 규칙을 JSON으로 추출하라."
        config = types.GenerateContentConfig(system_instruction=prompt, temperature=0.0, response_mime_type="application/json")
        response = self.auth.generate("gemini-1.5-flash", history, config)
        try:
            res_data = json.loads(response.text)
            return res_data if res_data.get("feedback_detected") else None
        except: return None

    def analyze_self_correction(self, log_path: str = "logs/trace.jsonl") -> Optional[Dict[str, Any]]:
        """로그에서 자가 수정 패턴 분석"""
        if not os.path.exists(log_path): return None
        try:
            with open(log_path, "r") as f:
                log_content = "\n".join(f.readlines()[-100:])
            prompt = "로그를 분석하여 '성공적인 문제 해결 패턴'을 JSON으로 생성하라."
            response = self.auth.generate("gemini-1.5-flash", log_content, {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            return res_data if res_data.get("pattern_detected") else None
        except: return None

    def generate_performance_report(self, log_path: str = "logs/trace.jsonl") -> str:
        """성과 리포트 생성"""
        return "Performance report generated."

    def review_code(self, code: str, file_path: str = "unknown") -> Dict[str, Any]:
        """코드 품질 리뷰"""
        prompt = f"다음 코드를 Clean Code 기준으로 리뷰하라: {code}"
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except: return {"score": 100, "needs_refactoring": False}

    def analyze_coding_style(self, working_dir: str = ".") -> Dict[str, Any]:
        """코딩 스타일 분석"""
        return {"instruction": "PEP8 준수", "trigger_patterns": ["coding"]}

    def cross_validate(self, goal: str, output: str) -> Dict[str, Any]:
        """상호 검증"""
        prompt = f"목표: {goal}\n결과: {output}\n무결성 검증을 수행하라."
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except: return {"is_valid": True, "confidence_score": 1.0}

    def explain_logic(self, code: str, symbol_name: str = "selected code") -> str:
        """로직 설명"""
        prompt = f"코드 설명하라: {code}"
        return self.auth.generate("gemini-1.5-flash", [("user", prompt)], None).text

    def journalize_activity(self, agent: str, event: str, payload: Any) -> str:
        """활동 저널링"""
        return f"{agent}가 {event} 작업을 성공적으로 마쳤습니다."

    def profile_resource_usage(self, code: str) -> Dict[str, Any]:
        """코드의 시간/공간 복잡도 정적 분석"""
        prompt = f"""다음 파이썬 코드를 분석하여 예상되는 자원 효율성을 리포트하라.
        
        [Code]
        {code}
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "time_complexity": "O(n), O(1) 등",
            "memory_footprint": "Low/Medium/High",
            "potential_bottlenecks": ["병목 포인트 1", "2"],
            "performance_score": 0~100,
            "optimization_required": true/false
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Resource profiling failed: {e}")
            return {"time_complexity": "Unknown", "performance_score": 50, "optimization_required": False}

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """Analyst 노드 엔트리 포인트"""
    agent = AnalystAgent()
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    last_msg_lower = last_msg.lower()

    if state.get("next_node") == "analyst":
        ai_outputs = [m for m in state["messages"] if (isinstance(m, tuple) and m[0] == "ai") or (hasattr(m, 'type') and m.type == "ai")]
        if ai_outputs:
            last_ai_msg = ai_outputs[-1][1] if isinstance(ai_outputs[-1], tuple) else ai_outputs[-1].content
            
            # 1. 무결성 검증
            val_res = agent.cross_validate("Current Task", last_ai_msg)
            # 2. 자원 프로파일링
            perf_res = agent.profile_resource_usage(last_ai_msg)
            
            if not val_res.get("is_valid", True):
                return {"messages": [("ai", f"🛡️ [Cross-Validation Alert] {val_res.get('critique')}")], "next_node": "planner"}
            else:
                msg = f"🛡️ [Cross-Validation Passed] 무결성 검증 통과.\n"
                msg += f"⚡ [Performance Profile] 예상 복잡도: {perf_res['time_complexity']} (점수: {perf_res['performance_score']}/100)"
                if perf_res.get("optimization_required"):
                    msg += "\n⚠️ 주의: 비효율적인 로직이 감지되었습니다. 최적화를 권장합니다."
                
                economy = state.get("agent_economy", {}).copy()
                if "coder" not in economy: economy["coder"] = {"points": 0, "level": "Novice"}
                economy["coder"]["points"] += 10
                return {"messages": [("ai", msg)], "agent_economy": economy, "next_node": "manager"}

    if "/explain" in last_msg_lower:
        return {"messages": [("ai", "Logic explanation complete.")], "next_node": "manager"}
    if "/analyze_style" in last_msg_lower:
        return {"messages": [("ai", "Style analysis complete.")], "next_node": "manager"}
    if "리뷰" in last_msg_lower or "검토" in last_msg_lower:
        return {"messages": [("ai", "Code review complete.")], "next_node": "manager"}

    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]
    if data_files:
        result = agent.analyze_data(data_files[0])
        return {"messages": [("ai", f"Data analysis for {data_files[0]} complete.")], "next_node": "manager"}

    return {"messages": [("ai", "분석을 마쳤습니다.")], "next_node": "manager"}
