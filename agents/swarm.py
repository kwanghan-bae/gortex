import asyncio
import logging
import time
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth
from gortex.agents.analyst import AnalystAgent

from gortex.utils.log_vectorizer import SemanticLogSearch
from gortex.utils.message_queue import GortexMessageQueue

logger = logging.getLogger("GortexSwarm")

async def execute_parallel_task(task_desc: str, state: GortexState) -> Dict[str, Any]:
    """단일 하위 작업 또는 시나리오를 수행하고 상태 델타 및 점수 반환"""
    auth = GortexAuth()
    log_search = SemanticLogSearch()
    
    start_time = time.time()
    
    # 1. 과거 유사 성공 사례 확인 (Experience Weight)
    past_cases = log_search.search_similar_cases(task_desc, limit=1)
    experience_weight = 0.2 if past_cases else 0.0 # 성공 사례가 있으면 보너스 점수
    
    prompt = f"""다음 시나리오 또는 작업을 수행하라: {task_desc}
    결과는 반드시 JSON 형식을 따르며, 추론의 확신도와 위험도를 자체 평가하라.
    {{ 
        "report": "작업 결과", 
        "certainty": 0.0~1.0, 
        "risk": 0.0~1.0,
        "new_files": {{ "path": "hash" }} 
    }}
    """
    try:
        response = auth.generate("gemini-1.5-flash", [("user", prompt)], {
            "response_mime_type": "application/json"
        })
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 토큰 수 추정 (metadata가 없으면 길이 기반)
        tokens = 0
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            tokens = response.usage_metadata.total_token_count
        else:
            tokens = len(prompt) // 4 + len(response.text) // 4
            
        import json
        res_data = json.loads(response.text)
        return {
            "task": task_desc,
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
            "task": task_desc, 
            "report": f"Error: {e}", 
            "certainty": 0, 
            "risk": 1, 
            "experience_score": 0, 
            "file_cache_delta": {}, 
            "success": False,
            "latency_ms": latency_ms,
            "tokens": 0
        }

async def swarm_node_async(state: GortexState) -> Dict[str, Any]:
    """병렬 에이전트 협업 노드 (Async) - MQ 연동 및 효율성 평가 포함"""
    tasks = state.get("plan", [])
    if not tasks:
        return {"next_node": "manager"}

    mq = GortexMessageQueue()
    analyst = AnalystAgent()
    logger.info(f"🐝 Swarm processing {len(tasks)} tasks...")
    
    # 1. 태스크들을 MQ에 발행 (Event-Driven 준비)
    for t in tasks:
        mq.publish("gortex_tasks", {"task": t, "state_id": "session_context"})

    # 2. 기존 실시간 병렬 실행
    task_results = await asyncio.gather(*[execute_parallel_task(t, state) for t in tasks])
    
    # 고도화된 시나리오 평가 (Score = Efficiency + Certainty - Risk + Experience)
    scored_results = []
    
    # 에너지 비용은 병렬 작업 개수에 비례 (단순화)
    energy_cost_per_task = 5 
    
    for res in task_results:
        # 효율성 점수 계산
        eff_score = analyst.calculate_efficiency_score(
            res["success"], 
            res.get("tokens", 0), 
            res.get("latency_ms", 0), 
            energy_cost_per_task
        )
        
        # 종합 점수 (효율성 점수를 0~1 스케일로 변환하여 반영)
        normalized_eff = eff_score / 100.0
        base_score = res["certainty"] * (1 - res["risk"])
        final_score = base_score + res.get("experience_score", 0) + (normalized_eff * 0.5) # 효율성 가중치 0.5
        
        res["efficiency_score"] = eff_score
        scored_results.append((final_score, res))
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    winner_score, winner = scored_results[0]
    
    # 우수 패턴 승격 시도 (효율성 점수가 높으면)
    if winner["efficiency_score"] >= 80:
        analyst.memory.promote_efficient_pattern(winner["task"], winner["efficiency_score"], context=winner["report"])
    
    logger.info(f"🏆 Scenario Winner: '{winner['task']}' (Score: {winner_score:.2f}, Eff: {winner['efficiency_score']:.1f})")

    merged_file_cache = state.get("file_cache", {}).copy()
    merged_file_cache.update(winner.get("file_cache_delta", {}))

    combined_msg = f"🐝 Swarm 가설 추론 결과:\n\n"
    combined_msg += f"✅ **선택된 안**: {winner['task']}\n"
    combined_msg += f"📊 **최종 점수**: {winner_score:.2f} (확신: {winner['certainty']*100:.0f}%, 효율: {winner['efficiency_score']:.1f})\n\n"
    combined_msg += f"📝 **상세 보고**:\n{winner['report']}\n\n"
    
    if len(scored_results) > 1:
        combined_msg += "--- 기타 검토된 시나리오 ---\n"
        for score, res in scored_results[1:]:
            combined_msg += f"- {res['task']} (Score: {score:.2f}, Eff: {res['efficiency_score']:.1f})\n"

    return {
        "messages": [("ai", combined_msg)],
        "file_cache": merged_file_cache,
        "next_node": "manager",
        "last_efficiency": winner["efficiency_score"], # 효율성 상태 업데이트
        "agent_energy": max(0, state.get("agent_energy", 100) - (len(tasks) * 2)) # 에너지 소모
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
