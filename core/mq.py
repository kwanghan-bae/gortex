import json
import logging
import os
import uuid
import time
from typing import Any, Dict, Optional, Callable, List, Tuple
from core.storage import StorageProvider, SqliteStorage, RedisStorage
from gortex.config.settings import settings

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
        self.env = settings.GORTEX_ENV
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self.is_connected = False
        
        # Storage Initialization
        if self.env == "distributed":
            if redis:
                try:
                    self.client = redis.from_url(self.url, decode_responses=True)
                    self.client.ping()
                    self.is_connected = True
                    self.storage = RedisStorage(client=self.client)
                    logger.info(f"🌐 Connected to Redis MQ: {self.url}")
                except Exception as e:
                    logger.warning(f"⚠️ Redis connection failed: {e}. Falling back to Local Storage.")
                    self.storage = SqliteStorage()
            else:
                logger.warning("⚠️ 'redis' package not installed. Using Local Storage.")
                self.storage = SqliteStorage()
        else:
            # Local Mode
            logger.info("🏠 Running in Local Mode (SqliteStorage).")
            self.storage = SqliteStorage()
            self.client = None # Explicitly None for local mode to avoid accidental redis usage

        # Local In-Memory PubSub for standalone mode
        self._local_subscribers: Dict[str, List[Callable]] = {}

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
            # Local PubSub
            if channel in self._local_subscribers:
                for callback in self._local_subscribers[channel]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Local subscriber error on {channel}: {e}")
            logger.debug(f"[LocalMQ] Broadcast on {channel}: {event_type}")

    def stream_thought(self, agent: str, thought: str):
        """에이전트의 현재 사고 과정을 실시간으로 스트리밍함"""
        self.publish_event("gortex:thought_stream", agent, "thought_update", {"text": thought})

    def broadcast_file_change(self, file_path: str, content: str, file_hash: str):
        """워크스페이스 파일 변경 사항을 분산 군집 전체에 전파함"""
        self.publish_event("gortex:workspace_sync", "System", "file_changed", {
            "path": file_path,
            "content": content,
            "hash": file_hash,
            "timestamp": time.time()
        })

    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        """원격지의 중요한 이벤트를 중앙 로그 시스템으로 전송함"""
        self.publish_event("gortex:remote_logs", agent, event, payload)

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        """작업 큐에 작업을 추가함"""
        if self.is_connected:
            self.client.rpush(queue_name, json.dumps(task_data))
        else:
            logger.debug(f"[DummyMQ] Enqueued task to {queue_name}")

    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """분산 락 획득 시도 (NX 옵션 사용)"""
        if not self.is_connected: return True
        return bool(self.client.set(f"gortex:lock:{lock_name}", "locked", ex=timeout, nx=True))

    def release_lock(self, lock_name: str):
        """분산 락 해제"""
        if self.is_connected: self.client.delete(f"gortex:lock:{lock_name}")

    def list_active_workers(self) -> List[Dict[str, Any]]:
        """가동 중인 모든 원격 워커의 상태 목록을 반환함"""
        if not self.is_connected: return []
        workers = []
        try:
            keys = self.client.keys("gortex:workers:*")
            for k in keys:
                data = self.client.get(k)
                if data: workers.append(json.loads(data))
        except: pass
        return workers

    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        """부하 상태를 고려하여 가장 적합한 워커 ID를 선택함"""
        workers = self.list_active_workers()
        if not workers: return None
        scored = []
        for w in workers:
            score = (100 - w.get("cpu_percent", 0)) - (w.get("active_tasks", 0) * 15)
            scored.append((score, w["worker_id"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
        """분산 군집에 작업을 공고하고 가장 적합한 워커의 ID를 낙찰받음"""
        if not self.is_connected: return None
        auction_id = str(uuid.uuid4())[:6]
        bid_chan = f"gortex:bids:{auction_id}"
        pubsub = self.client.pubsub()
        pubsub.subscribe(bid_chan)
        self.publish_event("gortex:auctions", "Master", "auction_started", {"auction_id": auction_id, "node": node_name, "reply_to": bid_chan})
        
        bids = []
        start = time.time()
        while time.time() - start < timeout:
            msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.2)
            if msg:
                bids.append(json.loads(msg['data']))
                if len(bids) >= 3: break
        pubsub.unsubscribe(bid_chan)
        if not bids: return self.select_best_worker()
        bids.sort(key=lambda x: x["bid_score"], reverse=True)
        return bids[0]["worker_id"]

    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:
        """원격 노드에 실행을 요청하고 결과를 기다림"""
        results = self.call_remote_nodes_parallel([(node_name, state)], timeout=timeout)
        return results[0] if results else None

    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        """여러 원격 노드를 동시에 호출"""
        if not self.is_connected or not requests: return []
        pending = {}
        pubsub = self.client.pubsub()
        for node, state in requests:
            req_id = str(uuid.uuid4())[:8]
            resp_chan = f"gortex:resp:{req_id}"
            pubsub.subscribe(resp_chan)
            pending[resp_chan] = {"done": False, "result": None}
            self.client.rpush("gortex:node_tasks", json.dumps({"id": req_id, "node": node, "state": state, "reply_to": resp_chan}))
        
        start = time.time()
        while time.time() - start < timeout:
            if all(r["done"] for r in pending.values()): break
            msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
            if msg and msg['channel'] in pending:
                pending[msg['channel']]["result"] = json.loads(msg['data'])
                pending[msg['channel']]["done"] = True
        pubsub.close()
        return [r["result"] for r in pending.values() if r["done"]]

    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        if self.is_connected:
            pubsub = self.client.pubsub()
            pubsub.subscribe(channel)
            for msg in pubsub.listen():
                if msg['type'] == 'message': callback(json.loads(msg['data']))
        else:
            # Local PubSub Registration
            if channel not in self._local_subscribers:
                self._local_subscribers[channel] = []
            self._local_subscribers[channel].append(callback)

    def announce_presence(self, swarm_id: str, capabilities: List[str]):
        self.publish_event("gortex:galactic:discovery", "Master", "swarm_online", {"swarm_id": swarm_id, "capabilities": capabilities})

# 글로벌 인스턴스
mq_bus = GortexMessageBus()