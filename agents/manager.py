import logging
import json
import os
import time
from typing import Dict, List, Any
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.translator import SynapticTranslator
from gortex.utils.vector_store import LongTermMemory
from gortex.utils.efficiency_monitor import EfficiencyMonitor
from gortex.core.registry import registry

logger = logging.getLogger("GortexManager")

def manager_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 중앙 관제소(Manager) 노드.
    사용자의 의도를 분석하고 레지스트리를 조회하여 가장 적합한 에이전트로 라우팅합니다.
    """
    backend = LLMFactory.get_default_backend()
    log_search = SemanticLogSearch()
    translator = SynapticTranslator()
    ltm = LongTermMemory()
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

    # 2. 맥락 정보 수집 (장기 기억, 과거 사례, 가용 에이전트)
    namespace = os.path.basename(state.get("working_dir", "global"))
    recalled_items = ltm.recall(internal_input, namespace=namespace)
    ltm_context = "\n".join([f"- {item['content']}" for item in recalled_items])
    
    past_cases = log_search.search_similar_cases(internal_input)
    case_context = "\n".join([f"Case: {c.get('agent')} - {c.get('event')}" for c in past_cases])
    
    available_agents = "\n".join([f"- {name}: {registry.get_metadata(name).description} (Tools: {registry.get_metadata(name).tools})" for name in registry.list_agents()])

    # 3. 시스템 프롬프트 구성
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "manager", 
        persona_id=state.get("assigned_persona", "standard"),
        ltm_context=ltm_context, 
        case_context=case_context, 
        persona_context=f"[AVAILABLE AGENTS]\n{available_agents}",
        context_text=internal_input
    )

    # 4. 모델 결정 (분석용 모델)
    from gortex.core.config import GortexConfig
    budget_limit = GortexConfig().get("daily_budget", 0.5)
    daily_cost = monitor.get_daily_cumulative_cost()
    
    # 분석은 기본적으로 Flash 사용하되 예산 부족 시 Lite/Ollama
    model_id = LLMFactory.get_model_for_grade("Silver", daily_cost, budget_limit)

    # 5. LLM 호출
    schema = {
        "type": "OBJECT",
        "properties": {
            "thought": {"type": "STRING"},
            "internal_critique": {"type": "STRING"},
            "thought_tree": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": {"type": "STRING"}, "text": {"type": "STRING"}, "type": {"type": "STRING"}, "priority": {"type": "INTEGER"}, "certainty": {"type": "NUMBER"}}}},
            "required_capability": {"type": "STRING"},
            "response_to_user": {"type": "STRING"},
            "ui_mode": {"type": "STRING"}
        },
        "required": ["thought", "required_capability"]
    }

    config = {"temperature": 0.0}
    formatted_messages = [{"role": "system", "content": base_instruction}]
    for m in state["messages"]:
        role = m[0] if isinstance(m, tuple) else "user"
        content = m[1] if isinstance(m, tuple) else (m.content if hasattr(m, 'content') else str(m))
        formatted_messages.append({"role": role, "content": content})

    try:
        response_text = backend.generate(model=model_id, messages=formatted_messages, config=config)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        
        # 6. 동적 에이전트 탐색 (Capability Discovery)
        req_cap = res_data.get("required_capability", "").lower()
        candidates = registry.get_agents_by_tool(req_cap) or registry.get_agents_by_role(req_cap)
        
        if candidates:
            agent_eco = state.get("agent_economy", {})
            candidates.sort(key=lambda x: agent_eco.get(x, {}).get("points", 0), reverse=True)
            target_node = candidates[0]
        else:
            target_node = "planner" # 기본값

        # 7. 타겟 에이전트에 최적화된 모델 할당
        target_grade = state.get("agent_economy", {}).get(target_node, {}).get("level", "Bronze")
        final_assigned_model = LLMFactory.get_model_for_grade(target_grade, daily_cost, budget_limit)

        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("manager", model_id, True, len(response_text)//4, latency_ms)

        return {
            "thought": res_data.get("thought"),
            "thought_tree": res_data.get("thought_tree"),
            "next_node": target_node,
            "assigned_model": final_assigned_model,
            "agent_energy": max(0, energy - 5),
            "handoff_instruction": "",
            "messages": [("ai", res_data.get("response_to_user", "분석을 완료했습니다."))] if res_data.get("response_to_user") else []
        }

    except Exception as e:
        logger.error(f"Manager failed: {e}")
        return {"next_node": "__end__", "messages": [("ai", f"❌ 분석 오류: {e}")]}
