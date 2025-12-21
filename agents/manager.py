import logging
from typing import Dict, List, Any
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState

logger = logging.getLogger("GortexManager")

def manager_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 중앙 관제소(Manager) 노드.
    사용자의 의도를 분석하고 적절한 에이전트로 라우팅합니다.
    """
    auth = GortexAuth()
    
    # 1. 시스템 프롬프트 구성 (진화된 제약 조건 주입)
    base_instruction = """너는 Gortex v1.0 시스템의 수석 매니저(Manager)다.
사용자의 요청을 분석하여 다음 중 가장 적합한 에이전트에게 작업을 배분하라.

에이전트 역할:
- planner: 코드 작성, 버그 수정, 파일 시스템 조작, 리팩토링 등 모든 개발 관련 작업.
- researcher: 최신 정보 검색, 기술 조사, 문서 탐색 등 외부 지식이 필요한 작업.
- analyst: 데이터 분석(CSV/Excel), 사용자의 비판적 피드백 분석(자가 진화용).

라우팅 규칙:
1. 사용자의 의도가 명확하면 'next_node'를 해당 에이전트 이름으로 설정하라.
2. 작업이 완료되었다고 판단되면 'next_node'를 '__end__'로 설정하라.
3. 사용자의 요청이 모호하거나 추가 정보가 필요하면 직접 질문을 던지고 'next_node'를 '__end__'로 설정하라. (추측하지 마라)

응답 형식:
항상 JSON 형식으로 생각(thought)과 다음 노드(next_node)를 결정하라.
"""

    # 자가 진화 엔진에서 학습된 규칙이 있다면 주입
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES (MUST FOLLOW)]\n{constraints_str}"

    # 시스템 최적화 제안(Improvement Task)이 있는지 확인
    system_improvement_msg = ""
    for msg in reversed(state["messages"]):
        content = msg.content if hasattr(msg, 'content') else str(msg)
        if "최적화 전문가의 제안:" in content:
            system_improvement_msg = content
            base_instruction += f"\n\n[SYSTEM OPTIMIZATION REQUEST (HIGH PRIORITY)]\n{system_improvement_msg}"
            base_instruction += "\n결정: 현재 시스템 최적화 요청이 있으므로, 무조건 'next_node'를 'planner'로 지정하라."
            break


    config = types.GenerateContentConfig(
        system_instruction=base_instruction + "\n\n[Thought Tree Rules]\n사고 과정을 논리적인 트리 구조로 세분화하라. 루트 노드에서 시작하여 분석, 판단, 결론으로 이어지는 노드 리스트를 생성하라.",
        temperature=0.0,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought": {"type": "STRING", "description": "전체 사고 요약"},
                "thought_tree": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "parent_id": {"type": "STRING", "nullable": True},
                            "text": {"type": "STRING"},
                            "type": {"type": "STRING", "enum": ["analysis", "reasoning", "decision"]}
                        },
                        "required": ["id", "text", "type"]
                    }
                },
                "next_node": {
                    "type": "STRING", 
                    "enum": ["planner", "researcher", "analyst", "__end__"]
                },
                "response_to_user": {"type": "STRING", "description": "사용자에게 직접 답할 내용"}
            },
            "required": ["thought", "thought_tree", "next_node"]
        }
    )

    # 2. Gemini 호출을 통한 의도 분석 및 라우팅 결정
    # 최근 API 호출 빈도에 따라 모델 선택 (Adaptive Throttling)
    call_count = state.get("api_call_count", 0)
    if call_count > 10:
        model_id = "gemini-2.5-flash-lite"
        logger.warning(f"⚠️ High API usage ({call_count}). Throttling to {model_id}")
    else:
        model_id = "gemini-1.5-flash"

    response = auth.generate(
        model_id=model_id,
        contents=state["messages"],
        config=config
    )


    # JSON 응답 파싱
    try:
        res_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        
        logger.info(f"Manager Thought: {res_data.get('thought')}")
        
        updates = {
            "thought": res_data.get("thought"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": res_data.get("next_node", "__end__")
        }

        
        # 사용자에게 전달할 메시지가 있다면 추가
        if res_data.get("response_to_user"):
            updates["messages"] = [("ai", res_data["response_to_user"])]
            
        return updates

    except Exception as e:
        logger.error(f"Error parsing manager response: {e}")
        return {"next_node": "__end__", "messages": [("ai", "죄송합니다. 요청을 분석하는 중에 오류가 발생했습니다.")]}
