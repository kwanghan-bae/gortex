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

        [분석 대상 핵심 신호]
        1. 명시적 거부: "아니", "틀렸어", "그거 말고", "하지 마"
        2. 수정 요구: "다시 해줘", "이렇게 바꿔줘", "왜 자꾸 X를 해?"
        3. 감정적 강조: 느낌표(!), "제발", "몇 번을 말해"
        4. 반복적 수정: 사용자가 같은 라인을 2회 이상 직접 수정하거나 반복 지시함

        [규칙 생성 원칙]
        - 범용성: "main.py 10번줄 고쳐" (X) -> "파이썬 코드 작성 시 PEP8 스타일을 준수하라" (O)
        - 명확성: 행동이 즉각적으로 정의되어야 함. "항상 X하라" 또는 "절대 Y하지 마라"
        - 트리거: 규칙이 활성화되어야 할 상황을 키워드로 정의 (예: 코딩, 한글, 파일 삭제)

        [추출 사례 (Few-shot)]
        Example 1:
        User: "아니 변수명을 왜 카멜케이스로 써? 파이썬은 스네이크케이스가 기본이야."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 8,
            "instruction": "Python 코드 작성 시 모든 변수명과 함수명은 반드시 snake_case를 사용할 것.",
            "context": "Python 코딩 및 리팩토링 시",
            "trigger_patterns": ["python", "variable naming", "snake_case"],
            "severity": 4,
            "reason": "사용자가 파이썬 표준 스타일(PEP8) 준수를 강력히 요구함."
        }

        Example 2:
        User: "앞으로 모든 답변은 한국어로만 해줘. 영어 섞지 말고."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 9,
            "instruction": "사용자에게 제공하는 모든 설명과 답변은 예외 없이 한국어(Korean)로 작성할 것.",
            "context": "사용자와의 모든 대화 상황",
            "trigger_patterns": ["answer language", "korean only"],
            "severity": 5,
            "reason": "사용자가 언어 설정을 최우선순위 제약 조건으로 명시함."
        }

        Example 3:
        User: "테스트 코드 없으면 불안해서 못 쓰겠네. 항상 붙여줘."
        Result: {
            "feedback_detected": true,
            "negative_signal_score": 7,
            "instruction": "신규 기능 구현 또는 코드 수정 시 반드시 해당 로직을 검증하는 단위 테스트(pytest)를 포함할 것.",
            "context": "코드 구현 및 수정 작업 시",
            "trigger_patterns": ["coding", "test code", "unit test"],
            "severity": 3,
            "reason": "사용자가 코드의 안정성 확보를 위해 테스트 코드 작성을 의무화함."
        }

        결과는 반드시 다음 JSON 형식을 따라라:

        {
            "feedback_detected": true/false,
            "negative_signal_score": 1~10 (신호의 명확성 및 강도),
            "instruction": "AI가 앞으로 영구적으로 지켜야 할 범용적인 지침",
            "context": "이 규칙이 적용되어야 할 구체적인 상황 (예: Python 코딩 중 함수 정의 시)",
            "trigger_patterns": ["트리거 키워드 1", "키워드 2"],
            "severity": 1~5,
            "reason": "사용자의 불만 원인 분석 결과"
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
                severity=feedback["severity"],
                context=feedback.get("context")
            )
            return {

                "messages": [("ai", f"새로운 규칙을 학습했습니다: '{feedback['instruction']}'")],
                "next_node": "manager"
            }
        
        return {
            "messages": [("ai", "요청하신 내용을 분석했으나 특이사항을 발견하지 못했습니다.")],
            "next_node": "manager"
        }
