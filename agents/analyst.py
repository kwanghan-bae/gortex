import logging
import json
import pandas as pd
import os
from typing import Dict, Any, List, Optional
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexAnalyst")

class AnalystAgent:
    """
    데이터 분석 및 자가 진화 피드백 분석을 담당하는 에이전트.
    """
    def __init__(self):
        self.auth = GortexAuth()
        self.memory = EvolutionaryMemory()

    def analyze_data(self, file_path: str) -> str:
        """Pandas를 사용하여 데이터 파일 분석"""
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"

            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                df = pd.read_json(file_path)
            else:
                return f"Error: Unsupported file format {ext}"

            # 기초 통계 및 정보 추출
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "head": df.head(5).to_dict(),
                "describe": df.describe(include='all').to_dict()
            }
            
            return json.dumps(summary, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return f"Error analyzing data: {e}"

    def analyze_feedback(self, history: List[Any]) -> Optional[Dict[str, Any]]:
        """사용자의 부정적 피드백을 분석하여 진화 규칙 추출"""
        # 히스토리 중 마지막 몇 개의 메시지 분석
        prompt = """
        사용자와 AI의 최근 대화를 분석하여 다음을 수행하라:
        1. 사용자가 AI의 행동에 대해 명확히 거부하거나 수정을 요구했는가? ("아니", "틀렸어", "다시 해줘" 등)
        2. 만약 그렇다면, AI가 앞으로 영구적으로 지켜야 할 새로운 '규칙(Constraint)'은 무엇인가?
        3. 이 규칙을 유발하는 키워드(trigger patterns)는 무엇인가?

        결과는 반드시 다음 JSON 형식을 따라라:
        {
            "feedback_detected": true/false,
            "instruction": "AI가 지켜야 할 명확한 지침 (예: 항상 타입 힌트를 넣어줘)",
            "trigger_patterns": ["관련 키워드 1", "관련 키워드 2"],
            "severity": 1~5
        }
        """
        
        config = types.GenerateContentConfig(
            system_instruction=prompt,
            temperature=0.0,
            response_mime_type="application/json"
        )
        
        response = self.auth.generate("gemini-1.5-flash", history, config)
        try:
            res_data = json.loads(response.text)
            if res_data.get("feedback_detected"):
                return res_data
            return None
        except Exception as e:
            logger.error(f"Feedback analysis parsing failed: {e}")
            return None

def analyst_node(state: GortexState) -> Dict[str, Any]:
    """Analyst 노드 엔트리 포인트"""
    agent = AnalystAgent()
    last_msg = state["messages"][-1].content

    # 1. 의도 판단 (Data Analysis vs Feedback Analysis)
    # Manager가 이미 이 노드로 보냈으므로, 여기서는 세부 분기 수행
    
    # 데이터 파일 언급이 있는지 확인 (단순 체크)
    data_files = [f for f in last_msg.split() if f.endswith(('.csv', '.xlsx', '.json'))]
    
    if data_files:
        # Data Mode
        result = agent.analyze_data(data_files[0])
        return {
            "messages": [("ai", f"데이터 분석 결과입니다:\n{result}")],
            "next_node": "manager"
        }
    else:
        # Evolution Mode (Feedback Analysis)
        feedback = agent.analyze_feedback(state["messages"])
        if feedback:
            agent.memory.save_rule(
                instruction=feedback["instruction"],
                trigger_patterns=feedback["trigger_patterns"],
                severity=feedback["severity"]
            )
            return {
                "messages": [("ai", f"새로운 규칙을 학습했습니다: '{feedback['instruction']}'")],
                "next_node": "manager"
            }
        
        return {
            "messages": [("ai", "요청하신 내용을 분석했으나 특이사항을 발견하지 못했습니다.")],
            "next_node": "manager"
        }
