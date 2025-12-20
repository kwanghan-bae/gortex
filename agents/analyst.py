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
        사용자와 AI의 최근 대화를 분석하여 시스템의 행동을 영구적으로 개선할 '지능형 규칙'을 추출하라.

        분석 가이드라인:
        1. 사용자가 AI의 특정 행동(코딩 스타일, 도구 사용, 답변 언어 등)에 대해 명확한 불만이나 수정을 요구했는가?
        2. 단순한 한 번의 수정을 넘어, 앞으로 모든 상황에서 지켜야 할 '범용적인 원칙'으로 정의할 수 있는가?
        3. 규칙은 '항상 X하라' 또는 '절대 Y하지 마라'와 같이 명확하고 강제성 있는 문장이어야 한다.
        4. 이 규칙을 활성화할 트리거 키워드를 정밀하게 선정하라. (예: Python 코딩 시, 주석 작성 시 등)

        추출 기준 예시:
        - "타입 힌트 좀 넣어" -> "모든 Python 함수 정의 시 반드시 명시적 타입 힌트를 포함할 것."
        - "주석은 한글로 써줘" -> "코드 내 모든 주석과 문서는 한국어로 작성할 것."
        - "파일 지우지 마" -> "파일 시스템 조작 시 rm 명령어를 사용하기 전 사용자에게 반드시 재확인할 것."

        결과는 반드시 다음 JSON 형식을 따라라:
        {
            "feedback_detected": true/false,
            "instruction": "AI가 앞으로 영구적으로 지켜야 할 범용적인 지침",
            "trigger_patterns": ["규칙을 활성화할 핵심 키워드/상황 1", "키워드 2"],
            "severity": 1~5 (사용자의 불만 강도),
            "reason": "이 규칙을 추출한 구체적인 근거"
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
