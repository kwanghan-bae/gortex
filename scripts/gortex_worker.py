import asyncio
import json
import logging
import sys
import os
import time
import uuid
import psutil

# 모듈 경로 추가
sys.path.append(os.getcwd())

from gortex.core.mq import mq_bus
from gortex.agents.researcher import ResearcherAgent
from gortex.agents.coder import coder_node
from gortex.agents.analyst import analyst_node
from gortex.agents.manager import manager_node
from gortex.agents.planner import planner_node
from gortex.utils.vector_store import LongTermMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GortexDistributedWorker")

# 노드 매핑
NODE_MAP = {
    "manager": manager_node,
    "planner": planner_node,
    "coder": coder_node,
    "analyst": analyst_node
}

async def process_research_task(task: dict):
    """(Legacy) 리서치 작업 처리"""
    agent = ResearcherAgent()
    query = task["query"]
    task_id = task["task_id"]
    is_docs = task.get("is_docs_needed", False)
    
    logger.info(f"🔨 Processing research task {task_id}: {query}")
    try:
        if is_docs: result = await agent.fetch_api_docs(query)
        else: result = await agent.search_and_summarize(query)
        
        global total_tasks_done
        total_tasks_done += 1
        
        ltm = LongTermMemory()
        ltm.memorize(f"Async Research ({query}): {result}", {"source": "Worker", "task_id": task_id})
        mq_bus.publish_event("gortex:notifications", "Worker", "task_completed", {"task_id": task_id, "type": "research", "query": query, "summary": result[:200]})
    except Exception as e:
        logger.error(f"Task failed: {e}")
        mq_bus.publish_event("gortex:notifications", "Worker", "task_failed", {"task_id": task_id, "error": str(e)})

async def process_node_execution(request: dict):
    """원격 노드 실행 요청 처리 (v4.0 Alpha)"""
    node_name = request["node"]
    state = request["state"]
    reply_channel = request["reply_to"]
    request_id = request["id"]
    
    logger.info(f"⚡ Executing remote node: {node_name} (Req: {request_id})")
    
    # [STREAMING] 실행 시작 알림
    mq_bus.stream_thought(node_name, f"Starting remote execution for request {request_id}...")
    
    try:
        node_func = NODE_MAP.get(node_name.lower())
        if not node_func:
            raise ValueError(f"Unknown node type: {node_name}")
            
        # 1. 노드 실행 (동기 함수일 경우 executor 사용)
        if asyncio.iscoroutinefunction(node_func):
            result = await node_func(state)
        else:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, node_func, state)
            
        # [STREAMING] 완료 알림
        mq_bus.stream_thought(node_name, f"Completed task {request_id}. Sending results back.")
        mq_bus.log_remote_event(node_name, "node_complete", {"request_id": request_id, "status": "success"})
        
        global total_tasks_done
        total_tasks_done += 1
            
        # 2. 결과 전송 (Pub/Sub)
        mq_bus.client.publish(reply_channel, json.dumps(result, ensure_ascii=False))
        logger.info(f"✅ Remote node '{node_name}' finished. Result sent to {reply_channel}")
        
    except Exception as e:
        logger.error(f"❌ Remote node execution failed: {e}")
        mq_bus.log_remote_event(node_name, "error", {"request_id": request_id, "error": str(e)})
        mq_bus.client.publish(reply_channel, json.dumps({"error": str(e), "status": "failed"}))

import psutil

# ... (기존 임포트 하단)

total_tasks_done = 0

async def send_heartbeat(worker_id: str):
    """주기적으로 워커의 건강 상태를 Redis에 보고함"""
    while True:
        try:
            stats = {
                "worker_id": worker_id,
                "status": "online",
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "active_tasks": 0, 
                "total_tasks_done": total_tasks_done, # 기여도 추가
                "last_seen": time.time(),
                "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown"
            }
            mq_bus.client.set(f"gortex:workers:{worker_id}", json.dumps(stats), ex=15)
            logger.debug(f"💓 Heartbeat sent for {worker_id}")
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
        await asyncio.sleep(10)

async def main():
    if not mq_bus.is_connected:
        logger.critical("Redis MQ not connected. Worker cannot start.")
        return

    worker_id = f"worker_{os.uname().nodename}_{str(uuid.uuid4())[:4]}" if hasattr(os, "uname") else f"worker_win_{str(uuid.uuid4())[:4]}"
    logger.info(f"🚀 Gortex Distributed Swarm Worker (v4.0 Alpha) is active: {worker_id}")
    
    # 하트비트 태스크 시작
    asyncio.create_task(send_heartbeat(worker_id))
    
    logger.info("Monitoring 'gortex:tasks:research' and 'gortex:node_tasks'...")
    
    while True:
        # 1. 노드 실행 큐 감시 (우선순위 높음)
        node_req = mq_bus.client.blpop("gortex:node_tasks", timeout=1)
        if node_req:
            await process_node_execution(json.loads(node_req[1]))
            continue
            
        # 2. 리서치 큐 감시
        research_req = mq_bus.client.blpop("gortex:tasks:research", timeout=1)
        if research_req:
            await process_research_task(json.loads(research_req[1]))
            
        await asyncio.sleep(0.05)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Worker shutting down.")