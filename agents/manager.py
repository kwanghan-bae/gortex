import logging
import json
import os
from typing import Dict, List, Any
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.evolutionary_memory import EvolutionaryMemory
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
    evo_mem = EvolutionaryMemory()
    
    # 1. 언어 감지 및 번역 (다국어 지원)
    last_msg_obj = state["messages"][-1]
    raw_input = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    lang_info = translator.detect_and_translate(raw_input)
    
    # 내부 처리는 한국어 맥락을 포함한 원문 활용
    internal_input = lang_info.get("translated_text", raw_input) if not lang_info.get("is_korean") else raw_input

    # 에너지 상태 조기 획득 (전역 참조용)
    energy = state.get("agent_energy", 100)

    # [Persona Lab] 상황별 페르소나 선택 전략
    recommended_personas = ["Innovation", "Stability"]
    if any(k in internal_input.lower() for k in ["보안", "security", "취약점", "auth"]):
        recommended_personas.append("Security Expert")
    if any(k in internal_input.lower() for k in ["ui", "ux", "디자인", "dashboard", "화면"]):
        recommended_personas.append("UX Specialist")
    
    persona_context = f"현재 요청의 성격에 따라 다음 페르소나 중 2개 이상을 선택하여 토론을 구성하라: {', '.join(recommended_personas)}"

    # 2. 장기 기억 소환 (Recall)
    # 현재 작업 디렉토리를 네임스페이스로 사용하여 샤딩된 지식 소환
    namespace = os.path.basename(state.get("working_dir", "global"))
    recalled_items = ltm.recall(internal_input, namespace=namespace)
    
    # 만약 프로젝트 전용 지식이 부족하면 글로벌 샤드에서도 추가 검색
    if len(recalled_items) < 2:
        recalled_items += ltm.recall(internal_input, namespace="global", limit=2)
    
    ltm_context = ""
    knowledge_lineage = []
    
    if recalled_items:
        texts = [item["content"] for item in recalled_items]
        ltm_context = "\n[RECALLED LONG-TERM KNOWLEDGE]\n" + "\n".join([f"- {t}" for t in texts])
        if any("최신" in k or "신규" in k for k in texts):
            ltm_context += "\n(참고: 위 정보에는 최신 기술 트렌드가 포함되어 있습니다. 이를 계획 수립에 적극 반영하십시오.)"
        
        # 지식 계보 데이터 구성
        for item in recalled_items:
            knowledge_lineage.append({
                "source": item["metadata"].get("source", "Unknown"),
                "score": item["score"],
                "content_preview": item["content"][:50] + "..."
            })

    # 3. 과거 유사 사례 검색 (CBR)
    past_cases = log_search.search_similar_cases(internal_input)
    
    case_context = ""
    if past_cases:
        case_context = "\n[PAST SIMILAR CASES (FOR REFERENCE)]\n"
        for i, case in enumerate(past_cases):
            case_context += f"Case {i+1}: {case.get('agent')} encountered {case.get('event')}. Payload: {json.dumps(case.get('payload'))}\n"

    # 4. 학습된 매크로 확인
    macros = evo_mem.get_macros()
    macro_context = ""
    if macros:
        macro_context = "\n[Learned Macros (User-Defined Skills)]\n"
        for m in macros:
            macro_context += f"- Command: '{m['name']}' -> Steps: {m['steps']}\n"

    # 5. 시스템 프롬프트 구성
    base_instruction = f"""너는 Gortex v1.0 시스템의 수석 매니저(Manager)다.
사용자의 요청을 분석하여 다음 중 가장 적합한 에이전트에게 작업을 배분하라.
{ltm_context}
{case_context}
{macro_context}

[Interactive Decision Rules]
만약 사용자의 주관적인 취향이 중요하거나, 여러 기술적 선택지 중 트레이드오프가 뚜렷한 상황이라면 독단적으로 결정하지 마라.
이 경우 `requires_user_input`을 true로 설정하고, `question_to_user`에 선택지의 장단점을 포함한 정중한 질문을 작성하라. 사용자의 답변은 시스템의 장기적인 선호도 규칙으로 학습될 것이다.

[Adaptive UI Rules]
현재 수행할 작업의 성격에 맞춰 `ui_mode`를 설정하라.
- coding: 복잡한 코드 작성 또는 리팩토링 시 (시뮬레이션 패널 강조)
- research: 웹 검색 및 최신 기술 조사 시 (검색 결과 및 지식 그래프 강조)
- debugging: 테스트 실패 분석 및 오류 수정 시 (로그 및 성찰 리포트 강조)
- analyst: 데이터 분석 및 시각화 시 (차트 및 성과 리포트 강조)
- standard: 일반적인 대화 및 복합 작업 시

[User Intent Projection Rules]
사용자의 입력을 분석하여 그들이 머릿속에 그리는 최종적인 '큰 그림(big_picture)'과 이를 달성하기 위한 '단계별 의도(intent_nodes)'를 추출하라.
- 사용자가 "결국 X를 만들고 싶어"라고 하면 X를 `big_picture`로 설정하고, 필요한 구성 요소들을 노드로 분해하라.
- 각 노드의 상태(status)를 판단하여 현재 진행 상황을 시각화하라.

[Speculative Reasoning Rules]
사용자의 요청이 복잡하거나 해결 방법이 여러 가지인 경우, 'swarm' 노드를 통해 병렬 검토하라. 
만약 작업의 위험도가 높거나(Risk > 0.7), 시스템의 핵심 구조를 변경하는 요청인 경우 반드시 **'토론 모드(Debate Mode)'**를 활성화하라. 
이 경우 계획(`parallel_tasks`)에 "관점 토론: [주제]" 형식을 포함시키고, {persona_context}를 통해 에이전트들이 상반된 전문 페르소나를 갖도록 지시하라.

[Macro Learning Rules]
1. 사용자가 "배워(Learn): [명령어]는 [작업1], [작업2]...를 의미해"라고 하면, 이를 새로운 매크로로 저장하도록 'analyst'에게 요청하라.
2. 사용자가 저장된 매크로 명령어(예: "배포 실행해")를 사용하면, 정의된 단계들을 실행 계획에 포함시키도록 'planner'에게 상세히 지시하라.

[Agent Factory Rules]
만약 현재 가용한 에이전트(planner, researcher, analyst)로 처리하기에 지나치게 전문화된 영역(예: 양자역학 분석, 특정 게임 엔진 튜닝 등)이 반복적으로 요청된다면, 새로운 전문 에이전트의 생성을 결정하라. 
이 경우 'thought'에 사유를 적고 'next_node'를 'planner'로 지정하여 신규 에이전트 코드를 작성하게 하라.

에이전트 역할:
- planner: 코드 작성, 버그 수정, 에이전트 자가 생성(Agent Factory) 등 모든 개발 관련 작업.
- researcher: 최신 정보 검색, 기술 조사.
- analyst: 데이터 분석, 피드백 분석, 매크로 저장.
- swarm: 병렬 추론 및 분산 처리.
"""

    # 자가 진화 엔진에서 학습된 규칙이 있다면 주입
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES (MUST FOLLOW)]\n{constraints_str}"

    # [Tech Radar Adoption] 신기술 도입 후보 확인
    if os.path.exists("tech_radar.json"):
        try:
            with open("tech_radar.json", "r") as f:
                radar_data = json.load(f)
                candidates = radar_data.get("adoption_candidates", [])
                if candidates:
                    candidates_str = "\n".join([f"- {c['tech']} -> {c['target_file']}: {c['reason']}" for c in candidates[:3]])
                    base_instruction += f"\n\n[OPPORTUNITY: Tech Radar Adoption]\n새로운 기술 도입 기회가 발견되었습니다. 현재 작업이 바쁘지 않다면, 이를 반영한 리팩토링을 제안하십시오.\n{candidates_str}"
        except Exception as e:
            logger.warning(f"Failed to read tech radar: {e}")

    # 시스템 최적화 제안(Improvement Task)이 있는지 확인
    system_improvement_msg = ""
    
    # [Auto-Refactor Loop] 에너지가 충분할 때 능동적 기술 부채 해소 시도
    if energy > 80 and not any("refactor" in msg.content.lower() for msg in reversed(state["messages"]) if hasattr(msg, 'content')):
        from gortex.agents.analyst import AnalystAgent
        refactor_target = AnalystAgent().suggest_refactor_target()
        if refactor_target:
            base_instruction += f"\n\n[AUTO-REFACTOR OPPORTUNITY]\n현재 시스템 에너지가 충분하여 기술 부채 해소를 제안한다.\n대상 파일: {refactor_target['file']}\n문제: {refactor_target['issue']}\n전략: {refactor_target['refactor_strategy']}\n이 작업을 최우선으로 수행할 수 있는 계획을 수립하라."

    for msg in reversed(state["messages"]):
        content = msg.content if hasattr(msg, 'content') else str(msg)
        if "최적화 전문가의 제안:" in content:
            system_improvement_msg = content
            base_instruction += f"\n\n[SYSTEM OPTIMIZATION REQUEST (HIGH PRIORITY)]\n{system_improvement_msg}"
            base_instruction += "\n결정: 현재 시스템 최적화 요청이 있으므로, 무조건 'next_node'를 'planner'로 지정하라."
            break


    # 에너지 상태에 따른 지침 주입
    energy = state.get("agent_energy", 100)
    if energy < 50:
        base_instruction += f"\n\n[Energy Alert] 현재 너의 에너지가 {energy}%로 낮다. 가급적 가벼운 모델로 처리 가능한 단순한 계획을 수립하고, 불필요한 도구 호출을 자제하라."

    # 효율성 상태에 따른 지침 주입
    last_eff = state.get("last_efficiency", 100.0)
    if last_eff < 40.0:
        base_instruction += f"\n\n[Efficiency Alert] 최근 작업의 효율성 점수가 {last_eff:.1f}로 매우 낮다. 이는 비효율적인 접근 방식 때문일 수 있다. 이번 계획 수립 시에는 더 신중하고 상세한(Detailed) 단계를 구성하여 실패 비용을 줄여라."

    # 지속적인 저효율 감지 및 Optimizer 강제 (Self-Healing)
    eff_history = state.get("efficiency_history", [])
    if len(eff_history) >= 3 and all(e < 40.0 for e in eff_history[-3:]):
        logger.warning("📉 Persistent low efficiency detected. Forcing optimization.")
        base_instruction += "\n\n[CRITICAL ALERT] 최근 3회 연속 작업 효율성이 매우 낮습니다 (< 40). 즉시 'optimizer' 에이전트로 라우팅하여 원인을 진단하고 해결책을 마련하십시오. 다른 작업은 중단하십시오."

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
                    "enum": ["planner", "researcher", "analyst", "swarm", "optimizer", "__end__"]
                },
                "requires_user_input": {
                    "type": "BOOLEAN",
                    "description": "중요한 결정에 대해 사용자의 승인이나 의견이 필요한 경우 true"
                },
                "question_to_user": {
                    "type": "STRING",
                    "description": "사용자에게 물어볼 구체적인 질문 내용"
                },
                "ui_mode": {
                    "type": "STRING",
                    "enum": ["coding", "research", "analyst", "debugging", "standard"],
                    "description": "현재 작업 맥락에 가장 적합한 UI 레이아웃 모드"
                },
                "user_intent_projection": {
                    "type": "OBJECT",
                    "properties": {
                        "big_picture": {"type": "STRING", "description": "사용자가 달성하려는 최종적인 목표"},
                        "intent_nodes": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "id": {"type": "STRING"},
                                    "label": {"type": "STRING"},
                                    "status": {"type": "STRING", "enum": ["pending", "in_progress", "done"]},
                                    "parent_id": {"type": "STRING", "nullable": True}
                                },
                                "required": ["id", "label", "status"]
                            }
                        }
                    }
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
    # 최근 API 호출 빈도 및 에너지 수준에 따라 모델 선택 (Adaptive Throttling & Energy Awareness)
    call_count = state.get("api_call_count", 0)
    
    if call_count > 10 or energy < 30:
        model_id = "gemini-2.5-flash-lite"
        reason = "High API usage" if call_count > 10 else "Low Energy"
        logger.warning(f"⚠️ {reason} ({call_count}/{energy}). Throttling to {model_id}")
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
        
        # 에너지 소모 기록 (단순화: 매 턴 5% 감소)
        new_energy = max(0, energy - 5)
        
        target_node = res_data.get("next_node", "__end__")
        
        # [Peer Review Economy] 크레딧 기반 모델 할당 및 비용 차감
        assigned_model = "gemini-1.5-flash"
        credits = state.get("token_credits", {}).copy()
        
        if target_node in ["planner", "coder", "analyst"]:
            level = state.get("agent_economy", {}).get(target_node, {}).get("level", "Novice")
            balance = credits.get(target_node, 100.0)
            
            # 비용 정의: PRO 모델 = 50.0 credits
            if level == "Master" and energy >= 30 and balance >= 50.0:
                assigned_model = "gemini-1.5-pro"
                credits[target_node] = balance - 50.0 # 비용 차감
                logger.info(f"💎 Master agent '{target_node}' purchased PRO model. Remaining: {credits[target_node]}")
            elif level == "Master" and balance < 50.0:
                logger.info(f"💸 Insufficient credits for '{target_node}'. Falling back to FLASH.")
            elif energy < 30:
                logger.info(f"🔋 Low energy. Forcing FLASH model for '{target_node}'.")
        
        updates = {
            "thought": res_data.get("thought"),
            "internal_critique": res_data.get("internal_critique"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": target_node,
            "assigned_model": assigned_model,
            "agent_energy": new_energy,
            "ui_mode": res_data.get("ui_mode", "standard"),
            "token_credits": credits,
            "knowledge_lineage": knowledge_lineage,
            "user_intent_projection": res_data.get("user_intent_projection")
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
