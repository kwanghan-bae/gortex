import json
import logging
import uuid
import os
from typing import Any, Dict, Optional, Callable

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger("GortexMQ")

class GortexMessageQueue:
    """
    Redis를 기반으로 에이전트 간 비동기 메시지 및 작업을 전달하는 큐 시스템.
    """
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.from_url(self.url) if redis else None
        if not self.client:
            logger.warning("Redis not available. MQ functions will operate in dummy mode.")

    def publish(self, channel: str, message: Any):
        """메시지 발행"""
        if not self.client:
            return
        
        payload = json.dumps({
            "id": str(uuid.uuid4()),
            "data": message
        }, ensure_ascii=False)
        self.client.publish(channel, payload)
        logger.debug(f"Pushed to {channel}: {payload[:50]}...")

    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """메시지 구독 (Blocking)"""
        if not self.client:
            return
            
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to {channel}...")
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)

    def push_task(self, queue_name: str, task: Dict[str, Any]):
        """작업 큐에 작업 추가 (LPUSH)"""
        if not self.client:
            return
        self.client.lpush(queue_name, json.dumps(task, ensure_ascii=False))

    def pop_task(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """작업 큐에서 작업 가져오기 (BRPOP)"""
        if not self.client:
            return None
        result = self.client.brpop(queue_name, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None
