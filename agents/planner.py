import logging
import json
import time
from typing import Dict, Any, List
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.tools import list_files
from gortex.utils.indexer import SynapticIndexer
from gortex.utils.efficiency_monitor import EfficiencyMonitor

logger = logging.getLogger("GortexPlanner")

def planner_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 설계자(Planner) 노드.
    사용자의 목표를 달성하기 위해 원자적 단위(Atomic Unit)의 실행 계획을 수립합니다.
    (Ollama/Gemini 하이브리드 지원)
    """
    backend = LLMFactory.get_default_backend()
    indexer = SynapticIndexer()
    monitor = EfficiencyMonitor()
    start_time = time.time()
    
    # 1. 인덱스 기반 맥락 정보 추출
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    search_results = indexer.search(last_msg) if last_msg else []
    
    context_info = ""
    if search_results:
        context_info = "\n[Synaptic Index Search Results]\n"
        for res in search_results[:5]: # 상위 5개만 주입
            context_info += f"- {res['type'].upper()} '{res['name']}' in {res['file']} (Line {res['line']})\n"
            if res.get('docstring'):
                context_info += f"  Doc: {res['docstring'].split('\\n')[0]}\n"

    # 2. 현재 환경 및 리소스 파악
    current_files = list_files(state.get("working_dir", "."))
    energy = state.get("agent_energy", 100)
    
    # 3. 시스템 프롬프트 구성 (외부 템플릿 로드)
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "planner", 
        persona_id=state.get("assigned_persona", "standard"),
        current_files=current_files, 
        context_info=context_info
    )
    
    # 리소스 인식 지침 추가
    base_instruction += f"\n\n[System Resource State]\n- Current Energy: {energy}/100\n- Budget Constraints: API costs must be minimized."
    base_instruction += "\n\nAssign 'priority' (1-10) and 'is_essential' (true/false) to each step. Essential steps are those without which the main goal cannot be achieved."

    # 응답 스키마 정의 (Native용)
    schema = {
        "type": "OBJECT",
        "properties": {
            "thought_process": {"type": "STRING"},
            "impact_analysis": {
                "type": "OBJECT",
                "properties": {
                    "target": {"type": "STRING"},
                    "direct": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "indirect": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "risk_level": {"type": "STRING"}
                },
                "required": ["target", "direct", "indirect", "risk_level"]
            },
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
            "goal": {"type": "STRING"},
            "steps": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "id": {"type": "INTEGER"},
                        "action": {"type": "STRING"},
                        "target": {"type": "STRING"},
                        "reason": {"type": "STRING"},
                        "priority": {"type": "INTEGER"},
                        "is_essential": {"type": "BOOLEAN"}
                    },
                    "required": ["id", "action", "target", "reason", "priority", "is_essential"]
                }
            }
        },
        "required": ["thought_process", "internal_critique", "thought_tree", "goal", "steps"]
    }

    # 백엔드 능력에 따른 설정 분기
    assigned_model = state.get("assigned_model", "gemini-1.5-flash")
    config = {"temperature": 0.0}
    
    if not backend.supports_structured_output():
        base_instruction += "\n\n[IMPORTANT: OUTPUT FORMAT]\nYou must respond in JSON format ONLY. Required fields: thought_process, internal_critique, thought_tree, goal, steps (list of {id, action, target, reason}), impact_analysis."
    else:
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction=base_instruction,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=schema
        )

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
        response_text = backend.generate(model=assigned_model, messages=formatted_messages, config=config)
        success = True
        tokens = len(base_instruction) // 4 + len(response_text) // 4
        
        # JSON 파싱
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        plan_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
        
        logger.info(f"Planner Thought: {plan_data.get('thought_process')}")
        
        # [Autonomous Pruning] 리소스 상황에 따른 계획 최적화
        raw_steps = plan_data.get("steps", [])
        energy = state.get("agent_energy", 100)
        
        final_steps = []
        pruned_count = 0
        
        for step in raw_steps:
            # 에너지가 부족한 경우 (30 미만)
            if energy < 30:
                if step.get("is_essential", True) or step.get("priority", 5) >= 8:
                    final_steps.append(step)
                else:
                    pruned_count += 1
                    logger.warning(f"⚡ Resource low ({energy}%). Pruning non-essential step: {step.get('action')}")
            else:
                final_steps.append(step)
        
        # Plan을 상태에 저장하고 Coder에게 넘김
        plan_steps = [json.dumps(step, ensure_ascii=False) for step in final_steps]
        
        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("planner", assigned_model, success, tokens, latency_ms, metadata={"goal": plan_data.get('goal'), "pruned": pruned_count})

        from gortex.utils.translator import i18n
        
        msg = i18n.t("task.plan_established", goal=plan_data.get('goal'), steps=len(plan_steps))
        if pruned_count > 0:
            msg += f" (⚠️ {pruned_count}개의 부차적 작업이 리소스 절약을 위해 생략되었습니다.)"

        updates = {
            "thought_process": plan_data.get("thought_process"),
            "impact_analysis": plan_data.get("impact_analysis"),
            "internal_critique": plan_data.get("internal_critique"),
            "thought_tree": plan_data.get("thought_tree"),
            "plan": plan_steps,
            "current_step": 0,
            "next_node": "coder",
            "messages": [("ai", msg)]
        }
        
        return updates

    except Exception as e:
        logger.error(f"Error parsing planner response: {e}")
        latency_ms = int((time.time() - start_time) * 1000)
        monitor.record_interaction("planner", assigned_model, False, 0, latency_ms, metadata={"error": str(e)})
        from gortex.utils.translator import i18n
        return {
            "next_node": "__end__", 
            "messages": [("ai", i18n.t("error.general", error=str(e)))]
        }