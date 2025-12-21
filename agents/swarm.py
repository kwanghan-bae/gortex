import asyncio
import logging
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexSwarm")

async def execute_parallel_task(task_desc: str, state: GortexState) -> Dict[str, Any]:
    """단일 하위 작업을 수행하고 상태 델타를 반환"""
    auth = GortexAuth()
    # 작업을 위한 독립된 상태 복사본 (단순화)
    prompt = f"""다음 하위 작업을 수행하라: {task_desc}
    결과는 반드시 JSON 형식을 따르며, 발견된 정보나 변경된 사항을 포함하라.
    {{ "report": "작업 결과 요약", "new_files": {{ "path": "hash" }} }}
    """
    try:
        response = auth.generate("gemini-1.5-flash", [("user", prompt)], None)
        import json
        res_data = json.loads(response.text)
        return {
            "task": task_desc,
            "report": res_data.get("report", response.text),
            "file_cache_delta": res_data.get("new_files", {}),
            "success": True
        }
    except Exception as e:
        return {
            "task": task_desc,
            "report": f"❌ Failed: {e}",
            "file_cache_delta": {},
            "success": False
        }

async def swarm_node_async(state: GortexState) -> Dict[str, Any]:
    """병렬 에이전트 협업 노드 (Async) - 상태 병합 포함"""
    tasks = state.get("plan", [])
    if not tasks:
        return {"next_node": "manager"}

    logger.info(f"🐝 Swarm processing {len(tasks)} tasks with state merging...")
    
    # 병렬 실행
    task_results = await asyncio.gather(*[execute_parallel_task(t, state) for t in tasks])
    
    # 상태 병합 (State Merging)
    merged_file_cache = state.get("file_cache", {}).copy()
    reports = []
    conflicts = []

    for res in task_results:
        reports.append(f"Task: {res['task']}\nResult: {res['report']}")
        
        # 파일 캐시 병합 및 충돌 감지
        for path, file_hash in res.get("file_cache_delta", {}).items():
            if path in merged_file_cache and merged_file_cache[path] != file_hash:
                conflicts.append(path)
                logger.warning(f"⚠️ Conflict detected for file: {path}")
            merged_file_cache[path] = file_hash

    combined_msg = "🐝 Swarm 병렬 작업 결과:\n\n" + "\n\n".join(reports)
    if conflicts:
        combined_msg += f"\n\n⚠️ 충돌 감지({len(conflicts)}개): " + ", ".join(conflicts)

    return {
        "messages": [("ai", combined_msg)],
        "file_cache": merged_file_cache,
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
