import json
import logging
import os
import uuid
from typing import Any, Dict, Optional, Callable, List

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger("GortexMQ")

class GortexMessageBus:
    """
    Redis 기반의 분산 메시지 버스. 
    에이전트 간 비동기 작업 전달 및 상태 동기화를 담당합니다.
    """
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self.is_connected = False
        
        if redis:
            try:
                self.client = redis.from_url(self.url, decode_responses=True)
                self.client.ping()
                self.is_connected = True
                logger.info(f"🌐 Connected to Redis MQ: {self.url}")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. MQ will operate in dummy mode.")
        else:
            logger.warning("⚠️ 'redis' package not installed. MQ will operate in dummy mode.")

    def publish_event(self, channel: str, agent: str, event_type: str, payload: Dict[str, Any]):
        """이벤트를 방송(Broadcast)함"""
        message = {
            "id": str(uuid.uuid4()),
            "agent": agent,
            "type": event_type,
            "payload": payload
        }
        if self.is_connected:
            self.client.publish(channel, json.dumps(message))
        else:
            logger.debug(f"[DummyMQ] Broadcast on {channel}: {event_type}")

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        """작업 큐에 작업을 추가함"""
        if self.is_connected:
            self.client.rpush(queue_name, json.dumps(task_data))
        else:
            logger.debug(f"[DummyMQ] Enqueued task to {queue_name}")

    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """특정 채널의 메시지를 구독함 (Blocking)"""
        if not self.is_connected:
            logger.error("MQ is in dummy mode. Cannot listen.")
            return

        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        logger.info(f"👂 Listening on channel: {channel}")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)

# 글로벌 싱글톤 인스턴스
mq_bus = GortexMessageBus()
