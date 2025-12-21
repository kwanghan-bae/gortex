import logging
import json
import os
import time
from typing import Dict, List, Any
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.translator import SynapticTranslator
from gortex.utils.vector_store import LongTermMemory
from gortex.utils.efficiency_monitor import EfficiencyMonitor

logger = logging.getLogger("GortexManager")

def manager_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 중앙 관제소(Manager) 노드.
    사용자의 의도를 분석하고 적절한 에이전트로 라우팅합니다.
    (Ollama/Gemini 하이브리드 지원)
    """
    backend = LLMFactory.get_default_backend()
    log_search = SemanticLogSearch()
    translator = SynapticTranslator()
    ltm = LongTermMemory()
    evo_mem = EvolutionaryMemory()
    monitor = EfficiencyMonitor()
    start_time = time.time()
    
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

    # 5. 시스템 프롬프트 구성 (외부 템플릿 로드)
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "manager", 
        ltm_context=ltm_context, 
        case_context=case_context, 
        macro_context=macro_context,
        persona_context=persona_context
    )

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
            file = refactor_target.get('file', 'Unknown')
            issue = refactor_target.get('issue', 'Technical debt detected')
            strategy = refactor_target.get('refactor_strategy', 'Modularization required')
            base_instruction += f"\n\n[AUTO-REFACTOR OPPORTUNITY]\n현재 시스템 에너지가 충분하여 기술 부채 해소를 제안한다.\n대상 파일: {file}\n문제: {issue}\n전략: {strategy}\n이 작업을 최우선으로 수행할 수 있는 계획을 수립하라."

    for msg in reversed(state["messages"]):
        content = msg.content if hasattr(msg, 'content') else str(msg)
        if "최적화 전문가의 제안:" in content:
            system_improvement_msg = content
            base_instruction += f"\n\n[SYSTEM OPTIMIZATION REQUEST (HIGH PRIORITY)]\n{system_improvement_msg}"
            base_instruction += "\n결정: 현재 시스템 최적화 요청이 있으므로, 무조건 'next_node'를 'planner'로 지정하라."
            break


    # 에너지 상태에 따른 지침 주입
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

    # 응답 스키마 정의 (Native용)
    schema = {
        "type": "OBJECT",
        "properties": {
            "thought": {"type": "STRING"},
            "internal_critique": {"type": "STRING"},
            "thought_tree": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "STRING"},
                        "text": {"type": "STRING"},
                        "type": {"type": "STRING"},
                        "priority": {"type": "INTEGER"},
                        "certainty": {"type": "NUMBER"}
                    },
                    "required": ["id", "text", "type", "priority", "certainty"]
                }
            },
            "next_node": {"type": "STRING"},
            "response_to_user": {"type": "STRING"},
            "ui_mode": {"type": "STRING"},
            "assigned_persona": {"type": "STRING"}
        },
        "required": ["thought", "internal_critique", "thought_tree", "next_node"]
    }

    # 백엔드 능력에 따른 설정 분기
    config = {"temperature": 0.0}
    if not backend.supports_structured_output():
        base_instruction += "\n\n[IMPORTANT: OUTPUT FORMAT]\nYou must respond in JSON format ONLY. Required fields: thought, internal_critique, thought_tree (list of {id, text, type, priority, certainty}), next_node, response_to_user."
    else:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=base_instruction,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=schema
        )

    # 모델 결정 (Routing Intelligence)
    call_count = state.get("api_call_count", 0)
    scores = monitor.calculate_model_scores()
    logger.info(f"Model Scores: {scores}")
    
    # 기본 모델 후보군
    from gortex.core.config import GortexConfig
    config_obj = GortexConfig()
    cloud_model = config_obj.get("default_model", "gemini-1.5-flash")
    local_model = "ollama/llama3" # 가칭 (추후 설정화)

    # 지능형 선택 로직
    if energy < 30 or scores.get(local_model, 0) > 70:
        # 에너지가 부족하거나 로컬 모델 성능이 충분히 검증된 경우
        model_id = local_model
        logger.info(f"🤖 Intelligent Routing: Selecting Local Model ({model_id}) for efficiency.")
    elif call_count > 10:
        model_id = "gemini-2.5-flash-lite"
        logger.warning(f"⚠️ High API usage ({call_count}). Throttling to lite model.")
    else:
        model_id = cloud_model

    # [Exception] 진화나 복잡한 분석은 가급적 강력한 모델 강제
    if any(k in internal_input.lower() for k in ["진화", "evolve", "architecture", "refactor"]):
        model_id = "gemini-1.5-pro"
        logger.info(f"💎 Critical task detected. Forcing PRO model.")

    # 메시지 구성
    formatted_messages = [{"role": "system", "content": base_instruction}]
    for m in state["messages"]:
        role = m[0] if isinstance(m, tuple) else "user"
        content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
        formatted_messages.append({"role": role, "content": content})

    # LLM 호출
    success = False
    tokens = 0
    try:
        response_text = backend.generate(model=model_id, messages=formatted_messages, config=config)
        success = True
        tokens = len(base_instruction) // 4 + len(response_text) // 4
        
        # JSON 파싱
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        
        # 상태 업데이트 및 로직 수행 (기존 로직 유지)
        new_energy = max(0, energy - 5)
        target_node = res_data.get("next_node", "__end__")
        
        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("manager", model_id, success, tokens, latency_ms, metadata={"next_node": target_node})

        updates = {
            "thought": res_data.get("thought"),
            "internal_critique": res_data.get("internal_critique"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": target_node,
            "agent_energy": new_energy,
            "ui_mode": res_data.get("ui_mode", "standard"),
            "assigned_persona": res_data.get("assigned_persona", "standard")
        }
        
        if res_data.get("response_to_user"):
            updates["messages"] = [("ai", res_data["response_to_user"])]
            
        return updates

    except Exception as e:
        logger.error(f"Error in manager node: {e}")
        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("manager", model_id, False, 0, latency_ms, metadata={"error": str(e)})
        return {"next_node": "__end__", "messages": [("ai", f"❌ 요청 분석 실패: {e}")]}