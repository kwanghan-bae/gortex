import logging
import json
from typing import Dict, Any, List
from google.genai import types
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.tools import list_files
from gortex.utils.indexer import SynapticIndexer

logger = logging.getLogger("GortexPlanner")

def planner_node(state: GortexState) -> Dict[str, Any]:
    """
    Gortex 시스템의 설계자(Planner) 노드.
    사용자의 목표를 달성하기 위해 원자적 단위(Atomic Unit)의 실행 계획을 수립합니다.
    """
    auth = GortexAuth()
    indexer = SynapticIndexer()
    
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

    # 2. 현재 환경 파악
    current_files = list_files(state.get("working_dir", "."))
    file_cache = state.get("file_cache", {})
    
    # 3. 시스템 프롬프트 구성 (외부 템플릿 로드)
    from gortex.utils.prompt_loader import loader
    base_instruction = loader.get_prompt(
        "planner", 
        persona_id=state.get("assigned_persona", "standard"),
        current_files=current_files, 
        context_info=context_info
    )

    # 진화된 제약 조건 주입
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES]\n{constraints_str}"

    config = types.GenerateContentConfig(
        system_instruction=base_instruction + "\n\n[Thought Tree Rules]\n사용자의 목표를 달성하기 위한 설계 과정을 논리적인 트리 구조(분석 -> 설계 -> 검증 계획)로 구성하라.\n\n[Architecture Sketcher]\n복잡한 로직이나 모듈 간 상호작용이 필요한 경우, 반드시 'diagram_code' 필드에 Mermaid 형식의 다이어그램 코드를 작성하라.\n\n[Self-Consistency Rules]\n계획을 확정하기 전, 반드시 'internal_critique' 단계에서 설계의 누락 사항이나 모순을 재검토하라.\n\n[Predictive Pre-fetching]\n다음 단계에서 필요할 것으로 예상되는 리소스(파일 읽기 등)가 있다면 'pre_fetch' 리스트에 포함시켜 시스템 지연 시간을 최적화하라.",
        temperature=0.0,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought_process": {"type": "STRING", "description": "전체 설계 요약"},
                "impact_analysis": {
                    "type": "OBJECT",
                    "properties": {
                        "target": {"type": "STRING", "description": "수정 대상 메인 파일"},
                        "direct": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "직접 영향 받는 파일 목록"},
                        "indirect": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "간접 영향 받는 파일 목록"},
                        "risk_level": {"type": "STRING", "enum": ["Critical", "High", "Medium", "Low"]}
                    },
                    "required": ["target", "direct", "indirect", "risk_level"]
                },
                "internal_critique": {"type": "STRING", "description": "설계 계획에 대한 비판적 재검토"},
                "thought_tree": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "parent_id": {"type": "STRING", "nullable": True},
                            "text": {"type": "STRING"},
                            "type": {"type": "STRING", "enum": ["analysis", "design", "verification"]},
                            "priority": {"type": "INTEGER"},
                            "certainty": {"type": "NUMBER"},
                            "visual_payload": {"type": "STRING", "nullable": True, "description": "노드와 관련된 시각적 데이터 (예: Mermaid 다이어그램 코드)"}
                        },
                        "required": ["id", "text", "type", "priority", "certainty"]
                    }
                },
                "pre_fetch": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "다음 단계들을 위해 미리 로드해둘 파일 경로 목록"
                },
                "diagram_code": {"type": "STRING", "description": "Mermaid 형식의 아키텍처 다이어그램 코드 (선택사항)"},
                "goal": {"type": "STRING"},
                "steps": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "INTEGER"},
                            "action": {
                                "type": "STRING", 
                                "enum": ["read_file", "write_file", "execute_shell", "list_files", "apply_patch"]
                            },
                            "target": {"type": "STRING"},
                            "reason": {"type": "STRING"}
                        },
                        "required": ["id", "action", "target", "reason"]
                    }
                }
            },
            "required": ["thought_process", "internal_critique", "thought_tree", "goal", "steps"]
        }
    )

    # 3. Gemini 호출
    assigned_model = state.get("assigned_model", "gemini-3-flash-preview")
    response = auth.generate(
        model_id=assigned_model,
        contents=state["messages"],
        config=config
    )

    try:
        # JSON 파싱
        plan_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        
        logger.info(f"Planner Thought: {plan_data.get('thought_process')}")
        logger.info(f"Critique: {plan_data.get('internal_critique')}")
        
        # Plan을 상태에 저장하고 Coder에게 넘김
        plan_steps = [json.dumps(step, ensure_ascii=False) for step in plan_data["steps"]]
        
        from gortex.utils.translator import i18n
        updates = {
            "thought_process": plan_data.get("thought_process"),
            "impact_analysis": plan_data.get("impact_analysis"),
            "internal_critique": plan_data.get("internal_critique"),
            "thought_tree": plan_data.get("thought_tree"),
            "plan": plan_steps,
            "current_step": 0,
            "next_node": "coder",
            "messages": [("ai", i18n.t("task.plan_established", goal=plan_data.get('goal'), steps=len(plan_steps)))]
        }
        
        if plan_data.get("impact_analysis"):
            impact = plan_data["impact_analysis"]
            impact_msg = f"⚠️ **수정 영향 범위 분석** (위험도: {impact.get('risk_level', 'Unknown')})\n"
            impact_msg += f"- 대상: {impact.get('target')}\n"
            if impact.get("direct"): impact_msg += f"- 직접 영향: {', '.join(impact['direct'])}\n"
            if impact.get("indirect"): impact_msg += f"- 간접 영향: {', '.join(impact['indirect'])}"
            updates["messages"].append(("system", impact_msg))
        
        if plan_data.get("pre_fetch"):
            updates["pre_fetch"] = plan_data["pre_fetch"]
            logger.info(f"🚀 Pre-fetching suggested for {len(plan_data['pre_fetch'])} files.")
        
        if plan_data.get("diagram_code"):
            updates["diagram_code"] = plan_data["diagram_code"]
            updates["messages"].append(("system", "📊 아키텍처 다이어그램이 생성되었습니다. 웹 대시보드에서 확인 가능합니다."))
            
        return updates


    except Exception as e:
        logger.error(f"Error parsing planner response: {e}")
        from gortex.utils.translator import i18n
        return {
            "next_node": "__end__", 
            "messages": [("ai", i18n.t("error.general", error=str(e)))]
        }
