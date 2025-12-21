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
    
    # 3. 시스템 프롬프트 구성
    base_instruction = f"""너는 Gortex v1.0 시스템의 수석 아키텍트(Planner)다.
현재 작업 디렉토리의 파일 구조를 분석하고, 사용자의 목표를 달성하기 위한 구체적이고 검증 가능한 단계(Step)들을 계획하라.

[Current File Structure]
{current_files}
{context_info}

[File Cache Status]
현재 너는 {len(file_cache)}개 파일의 최신 내용을 기억하고 있다. 
이미 읽은 파일(Cache에 존재)은 다시 'read_file'을 할 필요가 없으나, 
중요한 변경이 예상되거나 확실하지 않다면 다시 읽는 계획을 세워라.

[Planning Rules]
1. 작업을 '원자적 단위(Atomic Unit)'로 쪼개라.
2. 각 단계는 `coder` 에이전트가 수행할 수 있는 구체적인 행동이어야 한다.
3. 심볼명(클래스/함수명)을 언급했으나 파일 경로를 모를 경우, 제공된 [Synaptic Index Search Results]를 참조하여 정확한 경로를 target으로 설정하라.
4. 시스템 최적화 제안(System Optimization Request)이 포함된 경우, 그 타당성을 반드시 검토하라.
5. 코드를 작성한 후에는 반드시 검증(테스트) 단계를 포함하라.

[Output Schema (Strict JSON)]
반드시 다음 JSON 구조를 준수하라:
{{
  "thought_process": "현재 상황 분석 및 계획 수립 이유",
  "goal": "최종 달성 목표 요약",
  "steps": [
    {{"id": 1, "action": "tool_name", "target": "file_path_or_command", "reason": "구체적인 이유"}}
  ]
}}
"""

    # 진화된 제약 조건 주입
    if state.get("active_constraints"):
        constraints_str = "\n".join([f"- {c}" for c in state["active_constraints"]])
        base_instruction += f"\n\n[USER-SPECIFIC EVOLVED RULES]\n{constraints_str}"

    config = types.GenerateContentConfig(
        system_instruction=base_instruction + "\n\n[Thought Tree Rules]\n사용자의 목표를 달성하기 위한 설계 과정을 논리적인 트리 구조(분석 -> 설계 -> 검증 계획)로 구성하라.",
        temperature=0.0,
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "thought_process": {"type": "STRING", "description": "전체 설계 요약"},
                "thought_tree": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "STRING"},
                            "parent_id": {"type": "STRING", "nullable": True},
                            "text": {"type": "STRING"},
                            "type": {"type": "STRING", "enum": ["analysis", "design", "verification"]}
                        },
                        "required": ["id", "text", "type"]
                    }
                },
                "goal": {"type": "STRING"},
                "steps": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "id": {"type": "INTEGER"},
                            "action": {
                                "type": "STRING", 
                                "enum": ["read_file", "write_file", "execute_shell", "list_files"]
                            },
                            "target": {"type": "STRING"},
                            "reason": {"type": "STRING"}
                        },
                        "required": ["id", "action", "target", "reason"]
                    }
                }
            },
            "required": ["thought_process", "thought_tree", "goal", "steps"]
        }
    )

    # 3. Gemini 호출
    response = auth.generate(
        model_id="gemini-3-flash-preview", # 복잡한 계획 수립을 위해 고성능 모델 사용
        contents=state["messages"],
        config=config
    )

    try:
        # JSON 파싱
        plan_data = response.parsed if hasattr(response, 'parsed') else json.loads(response.text)
        
        logger.info(f"Planner Thought: {plan_data.get('thought_process')}")
        
        # Plan을 상태에 저장하고 Coder에게 넘김
        plan_steps = [json.dumps(step, ensure_ascii=False) for step in plan_data["steps"]]
        
        return {
            "thought_process": plan_data.get("thought_process"),
            "thought_tree": plan_data.get("thought_tree"),
            "plan": plan_steps,
            "current_step": 0,
            "next_node": "coder",
            "messages": [("ai", f"계획을 수립했습니다: {plan_data.get('goal')} ({len(plan_steps)} steps)")]
        }


    except Exception as e:
        logger.error(f"Error parsing planner response: {e}")
        return {
            "next_node": "__end__", 
            "messages": [("ai", f"계획 수립 중 오류가 발생했습니다: {e}")]
        }
