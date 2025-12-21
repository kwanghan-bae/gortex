import logging
from typing import Dict, List, Any
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.translator import SynapticTranslator
from gortex.utils.vector_store import LongTermMemory

logger = logging.getLogger("GortexManager")

def manager_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 중앙 관제소(Manager) 노드.
    사용자의 의도를 분석하고 적절한 에이전트로 라우팅합니다.
    """
    auth = GortexAuth()
    log_search = SemanticLogSearch()
    translator = SynapticTranslator()
    ltm = LongTermMemory()
    
    # 1. 언어 감지 및 번역 (다국어 지원)
    last_msg_obj = state["messages"][-1]
    raw_input = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    lang_info = translator.detect_and_translate(raw_input)
    
    # 내부 처리는 한국어 맥락을 포함한 원문 활용
    internal_input = lang_info.get("translated_text", raw_input) if not lang_info.get("is_korean") else raw_input

    # 2. 장기 기억 소환 (Recall)
    long_term_knowledge = ltm.recall(internal_input)
    ltm_context = ""
    if long_term_knowledge:
        ltm_context = "\n[RECALLED LONG-TERM KNOWLEDGE]\n" + "\n".join([f"- {k}" for k in long_term_knowledge])

    # 3. 과거 유사 사례 검색 (CBR)
    past_cases = log_search.search_similar_cases(internal_input)
    
    case_context = ""
    if past_cases:
        case_context = "\n[PAST SIMILAR CASES (FOR REFERENCE)]\n"
        for i, case in enumerate(past_cases):
            case_context += f"Case {i+1}: {case.get('agent')} encountered {case.get('event')}. Payload: {json.dumps(case.get('payload'))}\n"

    # 4. 시스템 프롬프트 구성
    base_instruction = f"""너는 Gortex v1.0 시스템의 수석 매니저(Manager)다.
사용자의 요청을 분석하여 다음 중 가장 적합한 에이전트에게 작업을 배분하라.
{ltm_context}
{case_context}

[Speculative Reasoning Rules]
사용자의 요청이 복잡하거나 해결 방법이 여러 가지인 경우, 'swarm' 노드를 통해 병렬 검토하라.

[Agent Factory Rules]
만약 현재 가용한 에이전트(planner, researcher, analyst)로 처리하기에 지나치게 전문화된 영역(예: 양자역학 분석, 특정 게임 엔진 튜닝 등)이 반복적으로 요청된다면, 새로운 전문 에이전트의 생성을 결정하라. 
이 경우 'thought'에 사유를 적고 'next_node'를 'planner'로 지정하여 신규 에이전트 코드를 작성하게 하라.

에이전트 역할:
- planner: 코드 작성, 버그 수정, 에이전트 자가 생성(Agent Factory) 등 모든 개발 관련 작업.
- researcher: 최신 정보 검색, 기술 조사.
- analyst: 데이터 분석, 피드백 분석.
- swarm: 병렬 추론 및 분산 처리.
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
        system_instruction=base_instruction + "\n\n[Thought Tree Rules]\n사고 과정을 논리적인 트리 구조로 세분화하라. 루트 노드에서 시작하여 분석, 판단, 결론으로 이어지는 노드 리스트를 생성하라.\n\n[Self-Consistency Rules]\n최종 결정을 내리기 전, 반드시 'internal_critique' 단계에서 자신의 논리적 모순이나 위험 요소를 비판적으로 재검토하라.",
        temperature=0.0,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought": {"type": "STRING", "description": "전체 사고 요약"},
                "internal_critique": {"type": "STRING", "description": "자신의 추론 과정에 대한 비판적 재검토"},
                "thought_tree": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "parent_id": {"type": "STRING", "nullable": True},
                            "text": {"type": "STRING"},
                            "type": {"type": "STRING", "enum": ["analysis", "reasoning", "decision"]},
                            "priority": {"type": "INTEGER", "description": "1~5 (낮음~높음)"},
                            "certainty": {"type": "NUMBER", "description": "0.0~1.0 (확신도)"}
                        },
                        "required": ["id", "text", "type", "priority", "certainty"]
                    }
                },
                "next_node": {
                    "type": "STRING", 
                    "enum": ["planner", "researcher", "analyst", "swarm", "__end__"]
                },
                "parallel_tasks": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "next_node가 'swarm'일 때 병렬로 처리할 하위 작업 리스트"
                },
                "response_to_user": {"type": "STRING", "description": "사용자에게 직접 답할 내용"}
            },
            "required": ["thought", "internal_critique", "thought_tree", "next_node"]
        }
    )

    # 2. Gemini 호출을 통한 의도 분석 및 라우팅 결정
    # 최근 API 호출 빈도에 따라 모델 선택 (Adaptive Throttling)
    call_count = state.get("api_call_count", 0)
    if call_count > 10:
        model_id = "gemini-2.5-flash-lite"
        logger.warning(f"⚠️ High API usage ({call_count}). Throttling to {model_id}")
    else:
        # 설정된 기본 모델 사용
        from gortex.core.config import GortexConfig
        model_id = GortexConfig().get("default_model", "gemini-1.5-flash")

    response = auth.generate(
        model_id=model_id,
        contents=state["messages"],
        config=config
    )


    # JSON 응답 파싱
    try:
        res_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        
        logger.info(f"Manager Thought: {res_data.get('thought')}")
        logger.info(f"Critique: {res_data.get('internal_critique')}")
        
        updates = {
            "thought": res_data.get("thought"),
            "internal_critique": res_data.get("internal_critique"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": res_data.get("next_node", "__end__")
        }
        
        if res_data.get("parallel_tasks"):
            updates["plan"] = res_data["parallel_tasks"] # Swarm을 위한 임시 계획 주입
            logger.info(f"📦 Parallel tasks detected: {len(res_data['parallel_tasks'])} items.")

        
        # 사용자에게 전달할 메시지가 있다면 추가
        if res_data.get("response_to_user"):
            updates["messages"] = [("ai", res_data["response_to_user"])]
            
        return updates

    except Exception as e:
        logger.error(f"Error parsing manager response: {e}")
        return {"next_node": "__end__", "messages": [("ai", "죄송합니다. 요청을 분석하는 중에 오류가 발생했습니다.")]}
