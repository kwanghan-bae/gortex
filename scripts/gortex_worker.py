import asyncio
import json
import logging
import sys
import os

# 모듈 경로 추가
sys.path.append(os.getcwd())

from gortex.core.mq import mq_bus
from gortex.agents.researcher import ResearcherAgent
from gortex.utils.vector_store import LongTermMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("GortexWorker")

async def process_research_task(task: dict):
    agent = ResearcherAgent()
    query = task["query"]
    task_id = task["task_id"]
    is_docs = task.get("is_docs_needed", False)
    
    logger.info(f"🔨 Processing research task {task_id}: {query}")
    
    try:
        if is_docs:
            result = await agent.fetch_api_docs(query)
        else:
            result = await agent.search_and_summarize(query)
            
        # 결과를 장기 기억 장소에 저장 (모든 에이전트 공유 가능)
        ltm = LongTermMemory()
        ltm.memorize(
            f"Asynchronous Research Result ({query}): {result}",
            {"source": "Worker", "task_id": task_id, "type": "research"}
        )
        
        # 완료 이벤트 발행
        mq_bus.publish_event(
            "gortex:notifications",
            "Worker",
            "task_completed",
            {
                "task_id": task_id,
                "type": "research",
                "query": query,
                "summary": result[:200] + "..."
            }
        )
        logger.info(f"✅ Task {task_id} completed and results stored.")
        
    except Exception as e:
        logger.error(f"❌ Task {task_id} failed: {e}")
        mq_bus.publish_event("gortex:notifications", "Worker", "task_failed", {"task_id": task_id, "error": str(e)})

async def main():
    if not mq_bus.is_connected:
        logger.critical("Redis MQ not connected. Worker cannot start.")
        return

    logger.info("🚀 Gortex Distributed Worker is active. Monitoring 'gortex:tasks:research'...")
    
    while True:
        # 큐에서 작업 가져오기 (Blocking pop)
        task_raw = mq_bus.client.blpop("gortex:tasks:research", timeout=5)
        if task_raw:
            task_data = json.loads(task_raw[1])
            await process_research_task(task_data)
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Worker shutting down.")
