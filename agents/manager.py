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
    
    # 1. 언어 감지 및 번역
    last_msg_obj = state["messages"][-1]
    raw_input = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    lang_info = translator.detect_and_translate(raw_input)
    internal_input = lang_info.get("translated_text", raw_input) if not lang_info.get("is_korean") else raw_input

    energy = state.get("agent_energy", 100)
    call_count = state.get("api_call_count", 0)
    roadmap = state.get("evolution_roadmap", [])

    # [Persona Lab]
    recommended_personas = ["Innovation", "Stability"]
    virtual_persona_instruction = ""
    
    # 특수 상황 감지: 보안 위반 또는 대규모 리팩토링 필요 시
    is_critical_security = any(k in internal_input.lower() for k in ["보안", "security", "취약점", "auth"])
    major_roadmap = [r for r in roadmap if r.get("priority") == "High"]
    
    if is_critical_security:
        recommended_personas = ["Security Expert"]
        virtual_persona_instruction = "너는 지금부터 'Gortex Security Sentinel'이다. 모든 아키텍처 변경을 보안적 관점에서 검열하고, 최소 권한 원칙을 강제하라."
    elif major_roadmap:
        recommended_personas = ["Innovation"]
        virtual_persona_instruction = f"너는 지금부터 'Evolution Architect'이다. 로드맵의 {major_roadmap[0]['target']} 진화를 최우선으로 고려하여 과감한 구조 개선을 설계하라."
    
    persona_context = f"선택 가능 페르소나: {', '.join(recommended_personas)}"
    if virtual_persona_instruction:
        persona_context += f"\n[VIRTUAL PERSONA OVERRIDE] {virtual_persona_instruction}"
    
    # 2. 장기 기억 및 과거 사례 검색
    namespace = os.path.basename(state.get("working_dir", "global"))
    recalled_items = ltm.recall(internal_input, namespace=namespace)
    ltm_context = "\n".join([f"- {item['content']}" for item in recalled_items]) if recalled_items else ""
    
    past_cases = log_search.search_similar_cases(internal_input)
    case_context = "\n".join([f"Case: {c.get('agent')} - {c.get('event')}" for c in past_cases]) if past_cases else ""

    # 3. 시스템 프롬프트 구성
    roadmap = state.get("evolution_roadmap", [])
    roadmap_context = "\n".join([f"- {r['target']} ({r['suggested_tech']}) [Priority: {r['priority']}]" for r in roadmap]) if roadmap else ""
    
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "manager", 
        persona_id=state.get("assigned_persona", "standard"),
        ltm_context=ltm_context, 
        case_context=case_context, 
        macro_context=f"\n[CURRENT EVOLUTION ROADMAP]\n{roadmap_context}",
        persona_context=persona_context,
        context_text=internal_input
    )

    # 4. 모델 결정 (Initial Selection for Intent Analysis)
    scores = monitor.calculate_model_scores()
    from gortex.core.config import GortexConfig
    config_obj = GortexConfig()
    cloud_model = config_obj.get("default_model", "gemini-1.5-flash")
    local_model = "ollama/llama3"

    if energy < 30 or scores.get(local_model, 0) > 70:
        model_id = local_model
    elif call_count > 10:
        model_id = "gemini-2.5-flash-lite"
    else:
        model_id = cloud_model

    # 복잡한 작업은 PRO 강제
    if any(k in internal_input.lower() for k in ["진화", "evolve", "architecture", "refactor"]):
        model_id = "gemini-1.5-pro"

    # 5. LLM 호출 준비
    schema = {
        "type": "OBJECT",
        "properties": {
            "thought": {"type": "STRING"},
            "internal_critique": {"type": "STRING"},
            "thought_tree": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": {"type": "STRING"}, "text": {"type": "STRING"}, "type": {"type": "STRING"}, "priority": {"type": "INTEGER"}, "certainty": {"type": "NUMBER"}}, "required": ["id", "text", "type", "priority", "certainty"]}},
            "next_node": {"type": "STRING"},
            "response_to_user": {"type": "STRING"},
            "ui_mode": {"type": "STRING"},
            "assigned_persona": {"type": "STRING"}
        },
        "required": ["thought", "internal_critique", "thought_tree", "next_node"]
    }

    config = {"temperature": 0.0}
    if backend.supports_structured_output():
        config = types.GenerateContentConfig(system_instruction=base_instruction, temperature=0.0, response_mime_type="application/json", response_schema=schema)

    formatted_messages = [{"role": "system", "content": base_instruction}]
    for m in state["messages"]:
        role = m[0] if isinstance(m, tuple) else "user"
        content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
        formatted_messages.append({"role": role, "content": content})

    # 6. LLM 호출 및 결과 처리
    success = False
    tokens = 0
    target_node = "__end__"
    
    try:
        response_text = backend.generate(model=model_id, messages=formatted_messages, config=config)
        success = True
        tokens = len(base_instruction) // 4 + len(response_text) // 4
        
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        
        target_node = res_data.get("next_node", "__end__")
        expert_model = monitor.get_best_model_for_task(target_node)
        final_assigned_model = expert_model if expert_model and expert_model.startswith("gemini") else "gemini-1.5-flash"

        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("manager", model_id, success, tokens, latency_ms, metadata={"next_node": target_node})

        updates = {
            "thought": res_data.get("thought"),
            "internal_critique": res_data.get("internal_critique"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": target_node,
            "assigned_model": final_assigned_model,
            "agent_energy": max(0, energy - 5),
            "ui_mode": res_data.get("ui_mode", "standard"),
            "assigned_persona": res_data.get("assigned_persona", "standard")
        }
        
        if res_data.get("response_to_user"):
            updates["messages"] = [("ai", res_data["response_to_user"])]
            
        return updates

    except Exception as e:
        logger.error(f"Error in manager node: {e}")
        return {"next_node": "__end__", "messages": [("ai", f"❌ 분석 실패: {e}")]}
