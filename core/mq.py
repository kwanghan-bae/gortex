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
        if not self.is_connected:
            return True # Dummy mode: 항상 성공
        
        # 락 획득 시도 (10초 후 자동 해제)
        return bool(self.client.set(f"gortex:lock:{lock_name}", "locked", ex=timeout, nx=True))

    def release_lock(self, lock_name: str):
        """분산 락 해제"""
        if self.is_connected:
            self.client.delete(f"gortex:lock:{lock_name}")

    def list_active_workers(self) -> List[Dict[str, Any]]:
        """가동 중인 모든 원격 워커의 상태 목록을 반환함"""
        if not self.is_connected:
            return []
            
        workers = []
        try:
            keys = self.client.keys("gortex:workers:*")
            for k in keys:
                data_str = self.client.get(k)
                if data_str:
                    workers.append(json.loads(data_str))
        except Exception as e:
            logger.error(f"Failed to list workers: {e}")
            
        return workers

    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        """부하 상태를 고려하여 가장 적합한 워커 ID를 선택함"""
        workers = self.list_active_workers()
        if not workers:
            return None
            
        # 1. CPU 여유가 있고 태스크 수가 적은 워커 우선 (Score = (100-CPU) - (ActiveTasks * 10))
        scored_workers = []
        for w in workers:
            if w.get("status") != "online": continue
            
            score = (100 - w.get("cpu_percent", 0)) - (w.get("active_tasks", 0) * 15)
            # 메모리 임계치 체크 (90% 이상이면 제외)
            if w.get("memory_percent", 0) > 90: score -= 100
            
            scored_workers.append((score, w["worker_id"]))
            
        if not scored_workers: return None
        
        # 점수 순 정렬 후 최고 득점 워커 반환
        scored_workers.sort(key=lambda x: x[0], reverse=True)
        best_worker = scored_workers[0][1]
        logger.info(f"⚖️ Load Balancer: Selected {best_worker} (Score: {scored_workers[0][0]:.1f})")
        return best_worker

    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
        """분산 군집에 작업을 공고하고 가장 적합한 워커의 ID를 낙찰받음"""
        if not self.is_connected:
            return None

        auction_id = str(uuid.uuid4())[:6]
        bid_channel = f"gortex:bids:{auction_id}"
        
        # 1. 입찰 공고 발행
        message = {
            "auction_id": auction_id,
            "node": node_name,
            "complexity": state.get("risk_score", 0.5),
            "reply_to": bid_channel
        }
        
        pubsub = self.client.pubsub()
        pubsub.subscribe(bid_channel)
        
        self.publish_event("gortex:auctions", "Master", "auction_started", message)
        logger.info(f"⚖️ Auction started for '{node_name}' (ID: {auction_id})")
        
        # 2. 입찰 수집 (짧은 대기 시간)
        bids = []
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.2)
                if msg:
                    bid_data = json.loads(msg['data'])
                    bids.append(bid_data)
                    # 충분한 입찰이 모이면 조기 종료 가능
                    if len(bids) >= 3: break
                time.sleep(0.05)
        finally:
            pubsub.unsubscribe(bid_channel)
            
        if not bids:
            return self.select_best_worker() # 폴백: 기존 스케줄러 사용
            
        # 3. 최적 입찰자 선정 (부하가 적고 해당 노드 처리에 자신 있는 워커)
        bids.sort(key=lambda x: x["bid_score"], reverse=True)
        winner = bids[0]["worker_id"]
        logger.info(f"🔨 Auction won by {winner} (Score: {bids[0]['bid_score']:.1f})")
        return winner

    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:

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
