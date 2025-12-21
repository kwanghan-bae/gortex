import asyncio
import logging
import time
import os
import re
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth
from gortex.agents.analyst import AnalystAgent

from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.message_queue import GortexMessageQueue

logger = logging.getLogger("GortexSwarm")

def get_persona_instruction(persona_name: str) -> str:
    """docs/PERSONAS.md에서 특정 페르소나의 지침을 읽어옴"""
    persona_path = "docs/PERSONAS.md"
    if not os.path.exists(persona_path):
        return f"[Persona: {persona_name}] (지침 파일을 찾을 수 없습니다.)"
    
    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 더 유연한 파싱 (페르소나 섹션 추출)
        pattern = rf"### .*?{persona_name}.*?\n(.*?)(?=\n### |$)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            persona_section = match.group(1)
            # 행동 지침 문구 추출
            instr_match = re.search(r"행동 지침.*?: \"(.*?)\"", persona_section)
            if instr_match:
                return f"[Persona: {persona_name}] {instr_match.group(1)}"
    except Exception as e:
        logger.warning(f"Failed to parse personas: {e}")
        
    return f"[Persona: {persona_name}] 너의 역할에 충실하라."

async def execute_parallel_task(task_desc: str, state: GortexState, persona: str = None) -> Dict[str, Any]:
    """단일 하위 작업 또는 시나리오를 수행하고 상태 델타 및 점수 반환"""
    auth = GortexAuth()
    log_search = SemanticLogSearch()
    
    start_time = time.time()
    
    # 1. 과거 유사 성공 사례 확인
    past_cases = log_search.search_similar_cases(task_desc, limit=1)
    experience_weight = 0.2 if past_cases else 0.0
    
    # 2. 페르소나 지침 동적 획득
    persona_instruction = get_persona_instruction(persona) if persona else ""

    prompt = f"""{persona_instruction}
    다음 시나리오 또는 작업을 수행하라: {task_desc}
    결과는 반드시 JSON 형식을 따르며, 추론의 확신도와 위험도를 자체 평가하라.
    {{ 
        "report": "작업 결과", 
        "certainty": 0.0~1.0, 
        "risk": 0.0~1.0,
        "new_files": {{ "path": "hash" }} 
    }}
    """
    try:
        # 할당된 모델 사용 (state 기반)
        model_id = state.get("assigned_model", "gemini-1.5-flash")
        response = auth.generate(model_id, [("user", prompt)], {
            "response_mime_type": "application/json"
        })
        latency_ms = int((time.time() - start_time) * 1000)
        
        tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else (len(prompt) // 4 + len(response.text) // 4)
            
        import json
        res_data = json.loads(response.text)
        return {
            "task": task_desc,
            "persona": persona,
            "report": res_data.get("report", response.text),
            "certainty": res_data.get("certainty", 0.5),
            "risk": res_data.get("risk", 0.5),
            "experience_score": experience_weight,
            "file_cache_delta": res_data.get("new_files", {}),
            "success": True,
            "latency_ms": latency_ms,
            "tokens": tokens
        }
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "task": task_desc, "persona": persona, "report": f"Error: {e}", "certainty": 0, "risk": 1, 
            "experience_score": 0, "file_cache_delta": {}, "success": False, "latency_ms": latency_ms, "tokens": 0
        }

async def swarm_node_async(state: GortexState) -> Dict[str, Any]:
    """병렬 에이전트 협업 노드 (Async) - 토론 프로토콜 연동"""
    tasks = state.get("plan", [])
    if not tasks:
        return {"next_node": "manager"}

    mq = GortexMessageQueue()
    analyst = AnalystAgent()
    logger.info(f"🐝 Swarm processing {len(tasks)} tasks...")
    
    # [Debate Mode] 태스크가 2개 이상이고 고위험 상황인 경우 페르소나 할당
    is_debate = len(tasks) >= 2 and any("debate" in t.lower() or "토론" in t.lower() for t in tasks)
    
    parallel_calls = []
    for i, t in enumerate(tasks):
        persona = None
        if is_debate:
            persona = "Innovation" if i % 2 == 0 else "Stability"
        parallel_calls.append(execute_parallel_task(t, state, persona=persona))
        mq.publish("gortex_tasks", {"task": t, "persona": persona})

    task_results = await asyncio.gather(*parallel_calls)
    
    scored_results = []
    energy_cost_per_task = 5 
    
    for res in task_results:
        eff_score = analyst.calculate_efficiency_score(res["success"], res.get("tokens", 0), res.get("latency_ms", 0), energy_cost_per_task)
        normalized_eff = eff_score / 100.0
        base_score = res["certainty"] * (1 - res["risk"])
        final_score = base_score + res.get("experience_score", 0) + (normalized_eff * 0.5)
        res["efficiency_score"] = eff_score
        scored_results.append((final_score, res))
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    winner_score, winner = scored_results[0]
    
    # 우수 패턴 승격
    if winner["efficiency_score"] >= 80:
        analyst.memory.promote_efficient_pattern(winner["task"], winner["efficiency_score"], context=winner["report"])
    
    logger.info(f"🏆 Scenario Winner: '{winner['task']}' (Persona: {winner.get('persona')}, Score: {winner_score:.2f})")

    merged_file_cache = state.get("file_cache", {}).copy()
    merged_file_cache.update(winner.get("file_cache_delta", {}))

    combined_msg = f"🐝 Swarm {'토론 및 ' if is_debate else ''}가설 추론 결과:\n\n"
    combined_msg += f"✅ **선택된 안**: {winner['task']} ({winner.get('persona', 'Standard')})\n"
    combined_msg += f"📊 **최종 점수**: {winner_score:.2f} (효율: {winner['efficiency_score']:.1f})\n\n"
    combined_msg += f"📝 **상세 보고**:\n{winner['report']}\n\n"
    
    if len(scored_results) > 1:
        combined_msg += "--- 기타 검토된 시나리오 ---\n"
        for score, res in scored_results[1:]:
            combined_msg += f"- {res['task']} ({res.get('persona', 'N/A')}, Score: {score:.2f})\n"

    # 토론 모드였을 경우 Analyst에게 최종 합의 도출 요청 가능 (next_node 변경)
    next_node = "analyst" if is_debate else "manager"

    return {
        "messages": [("ai", combined_msg)],
        "file_cache": merged_file_cache,
        "next_node": next_node,
        "last_efficiency": winner["efficiency_score"],
        "agent_energy": max(0, state.get("agent_energy", 100) - (len(tasks) * 2)),
        "debate_context": task_results # 토론 원본 데이터 보존
    }
def swarm_node(state: GortexState) -> Dict[str, Any]:
    """Swarm 노드 엔트리 포인트 (Sync wrapper)"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(swarm_node_async(state)))
            return future.result()
    else:
        return loop.run_until_complete(swarm_node_async(state))
