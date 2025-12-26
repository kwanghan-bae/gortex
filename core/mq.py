import json
import logging
import os
import uuid
import time
from typing import Any, Dict, Optional, Callable, List, Tuple

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
            "payload": payload,
            "timestamp": time.time()
        }
        if self.is_connected:
            self.client.publish(channel, json.dumps(message))
        else:
            logger.debug(f"[DummyMQ] Broadcast on {channel}: {event_type}")

    def stream_thought(self, agent: str, thought: str):
        """에이전트의 현재 사고 과정을 실시간으로 스트리밍함"""
        self.publish_event("gortex:thought_stream", agent, "thought_update", {"text": thought})

    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        """원격지의 중요한 이벤트를 중앙 로그 시스템으로 전송함"""
        self.publish_event("gortex:remote_logs", agent, event, payload)

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        """작업 큐에 작업을 추가함"""
        if self.is_connected:
            self.client.rpush(queue_name, json.dumps(task_data))
        else:
            logger.debug(f"[DummyMQ] Enqueued task to {queue_name}")

    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:
        """원격 노드에 실행을 요청하고 결과를 기다림 (RPC 패턴)"""
        results = self.call_remote_nodes_parallel([(node_name, state)], timeout=timeout)
        return results[0] if results else None

    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        """여러 원격 노드에 실행을 동시에 요청하고 모든 결과를 기다림 (v4.0 Parallel Swarm)"""
        if not self.is_connected or not requests:
            return []

        pending_reqs = {}
        pubsub = self.client.pubsub()
        
        # 1. 모든 요청에 대해 채널 생성 및 구독
        for node_name, state in requests:
            req_id = str(uuid.uuid4())[:8]
            resp_chan = f"gortex:resp:{req_id}"
            
            message = {
                "id": req_id, "node": node_name, "state": state,
                "reply_to": resp_chan, "timestamp": time.time()
            }
            
            pubsub.subscribe(resp_chan)
            pending_reqs[resp_chan] = {"node": node_name, "id": req_id, "done": False, "result": None}
            
            # 요청 전송
            self.client.rpush("gortex:node_tasks", json.dumps(message))
            logger.info(f"📤 Parallel Dispatch: {node_name} (Req: {req_id})")

        # 2. 결과 집계 대기
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if all(r["done"] for r in pending_reqs.values()):
                    break
                    
                msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
                if msg:
                    chan = msg['channel']
                    if chan in pending_reqs:
                        pending_reqs[chan]["result"] = json.loads(msg['data'])
                        pending_reqs[chan]["done"] = True
                        logger.info(f"📥 Received parallel result for {pending_reqs[chan]['node']}")
                time.sleep(0.05)
        finally:
            pubsub.close()

        return [r["result"] for r in pending_reqs.values() if r["done"]]

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
