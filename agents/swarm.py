import asyncio
import logging
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexSwarm")

async def execute_parallel_task(task_desc: str, state: GortexState) -> str:
    """단일 하위 작업을 병렬로 수행"""
    auth = GortexAuth()
    # 하위 작업은 주로 Researcher나 Planner 성격이므로 Flash 모델 활용
    prompt = f"다음 하위 작업을 수행하고 결과를 보고하라: {task_desc}"
    try:
        response = auth.generate("gemini-1.5-flash", [("user", prompt)], None)
        return f"### Task: {task_desc}\n{response.text}\n"
    except Exception as e:
        return f"### Task: {task_desc}\n❌ Failed: {e}\n"

async def swarm_node_async(state: GortexState) -> Dict[str, Any]:
    """병렬 에이전트 협업 노드 (Async)"""
    tasks = state.get("plan", [])
    if not tasks:
        return {"next_node": "manager", "messages": [("ai", "처리할 병렬 작업이 없습니다.")]}

    logger.info(f"🐝 Swarm activated! Executing {len(tasks)} tasks in parallel...")
    
    # 병렬 실행
    results = await asyncio.gather(*[execute_parallel_task(t, state) for t in tasks])
    
    combined_result = "\n".join(results)
    
    return {
        "messages": [("ai", f"🐝 Swarm 작업 결과 요약:\n\n{combined_result}")],
        "next_node": "manager"
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
