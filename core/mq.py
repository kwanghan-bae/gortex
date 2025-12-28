import json
import logging
import os
import uuid
import time
from typing import Any, Dict, Optional, Callable, List, Tuple
from abc import ABC, abstractmethod

# gortex.core.storage imports will be resolved later to avoid circular imports if needed,
# or assumed to be available. For now, we will import them.
from gortex.core.storage import StorageProvider, SqliteStorage, RedisStorage, MockStorage
from gortex.config.settings import settings

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger("GortexMQ")

class BaseMessageBus(ABC):
    """
    Abstract base class for the Message Bus.
    """

    @abstractmethod
    def publish_event(self, channel: str, agent: str, event_type: str, payload: Dict[str, Any]):
        """Publish an event to a channel."""
        pass

    @abstractmethod
    def stream_thought(self, agent: str, thought: str):
        """Stream agent's thought process."""
        pass

    @abstractmethod
    def broadcast_file_change(self, file_path: str, content: str, file_hash: str):
        """Broadcast file changes to the swarm."""
        pass

    @abstractmethod
    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        """Log remote events to central system."""
        pass

    @abstractmethod
    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        """Enqueue a task."""
        pass

    @abstractmethod
    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """Acquire a distributed lock."""
        pass

    @abstractmethod
    def release_lock(self, lock_name: str):
        """Release a distributed lock."""
        pass

    @abstractmethod
    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to a channel."""
        pass

    # --- Distributed Worker Management Interface (Optional/Stubbed for Local) ---

    @abstractmethod
    def list_active_workers(self) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        pass

    @abstractmethod
    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
        pass

    @abstractmethod
    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def announce_presence(self, swarm_id: str, capabilities: List[str]):
        pass


class LocalMessageBus(BaseMessageBus):
    """
    In-Memory implementation of MessageBus for local development.
    Uses simple list/dict structures.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queues: Dict[str, List[Dict[str, Any]]] = {}
        self._locks: Dict[str, float] = {}
        self.storage = SqliteStorage()
        logger.info("🏠 Initialized LocalMessageBus (In-Memory).")

    def publish_event(self, channel: str, agent: str, event_type: str, payload: Dict[str, Any]):
        message = {
            "id": str(uuid.uuid4()),
            "agent": agent,
            "type": event_type,
            "payload": payload,
            "timestamp": time.time()
        }
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Local subscriber error on {channel}: {e}")
        logger.debug(f"[LocalMQ] Broadcast on {channel}: {event_type}")

    def stream_thought(self, agent: str, thought: str):
        self.publish_event("gortex:thought_stream", agent, "thought_update", {"text": thought})

    def broadcast_file_change(self, file_path: str, content: str, file_hash: str):
         self.publish_event("gortex:workspace_sync", "System", "file_changed", {
            "path": file_path,
            "content": content,
            "hash": file_hash,
            "timestamp": time.time()
        })

    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        self.publish_event("gortex:remote_logs", agent, event, payload)

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        if queue_name not in self._queues:
            self._queues[queue_name] = []
        self._queues[queue_name].append(task_data)
        logger.debug(f"[LocalMQ] Enqueued task to {queue_name}")

    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        now = time.time()
        if lock_name in self._locks:
            if self._locks[lock_name] > now:
                return False
        self._locks[lock_name] = now + timeout
        return True

    def release_lock(self, lock_name: str):
        if lock_name in self._locks:
            del self._locks[lock_name]

    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        self._subscribers[channel].append(callback)

    # --- Stubs for Distributed methods ---
    def list_active_workers(self) -> List[Dict[str, Any]]:
        return []

    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        return None

    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
        return None

    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:
        return None

    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        return []

    def announce_presence(self, swarm_id: str, capabilities: List[str]):
        # Just log locally
        logger.debug(f"Swarm {swarm_id} online with capabilities: {capabilities}")


class RedisMessageBus(BaseMessageBus):
    """
    Redis implementation of MessageBus for distributed environment.
    """
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        if not redis:
             raise ImportError("Redis package is missing. Cannot use RedisMessageBus.")

        try:
            self.client = redis.from_url(self.url, decode_responses=True)
            self.client.ping()
            self.storage = RedisStorage(client=self.client)
            logger.info(f"🌐 Connected to Redis MQ: {self.url}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise e

    def publish_event(self, channel: str, agent: str, event_type: str, payload: Dict[str, Any]):
        message = {
            "id": str(uuid.uuid4()),
            "agent": agent,
            "type": event_type,
            "payload": payload,
            "timestamp": time.time()
        }
        self.client.publish(channel, json.dumps(message))

    def stream_thought(self, agent: str, thought: str):
        self.publish_event("gortex:thought_stream", agent, "thought_update", {"text": thought})

    def broadcast_file_change(self, file_path: str, content: str, file_hash: str):
        self.publish_event("gortex:workspace_sync", "System", "file_changed", {
            "path": file_path,
            "content": content,
            "hash": file_hash,
            "timestamp": time.time()
        })

    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        self.publish_event("gortex:remote_logs", agent, event, payload)

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        self.client.rpush(queue_name, json.dumps(task_data))

    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        return bool(self.client.set(f"gortex:lock:{lock_name}", "locked", ex=timeout, nx=True))

    def release_lock(self, lock_name: str):
        self.client.delete(f"gortex:lock:{lock_name}")

    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        # Note: This implementation blocks. In a real async system, we'd loop in a separate task.
        # For compatibility with existing synchronous calls, we assume usage in a thread or simple loop.
        for msg in pubsub.listen():
             if msg['type'] == 'message': callback(json.loads(msg['data']))

    def list_active_workers(self) -> List[Dict[str, Any]]:
        workers = []
        try:
            keys = self.client.keys("gortex:workers:*")
            for k in keys:
                data = self.client.get(k)
                if data: workers.append(json.loads(data))
        except: pass
        return workers

    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        workers = self.list_active_workers()
        if not workers: return None
        scored = []
        for w in workers:
            score = (100 - w.get("cpu_percent", 0)) - (w.get("active_tasks", 0) * 15)
            scored.append((score, w["worker_id"]))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1] if scored else None

    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
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
        results = self.call_remote_nodes_parallel([(node_name, state)], timeout=timeout)
        return results[0] if results else None

    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        if not requests: return []
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

    def announce_presence(self, swarm_id: str, capabilities: List[str]):
        self.publish_event("gortex:galactic:discovery", "Master", "swarm_online", {"swarm_id": swarm_id, "capabilities": capabilities})


class GortexMessageBus(BaseMessageBus):
    """
    Proxy class that delegates to either LocalMessageBus or RedisMessageBus.
    """
    def __init__(self):
        self.env = settings.GORTEX_ENV
        self._impl: BaseMessageBus = None

        if self.env == "distributed":
            try:
                self._impl = RedisMessageBus(url=settings.REDIS_URL)
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize RedisMessageBus: {e}. Falling back to LocalMessageBus.")
                self._impl = LocalMessageBus()
        else:
            self._impl = LocalMessageBus()

    @property
    def storage(self):
        # Delegate storage access to implementation's storage
        if hasattr(self._impl, 'storage'):
             return self._impl.storage
        return SqliteStorage() # Fallback

    @property
    def is_connected(self) -> bool:
        if isinstance(self._impl, LocalMessageBus):
            return True
        elif isinstance(self._impl, RedisMessageBus):
            try:
                return self._impl.client.ping()
            except Exception:
                return False
        return False

    def publish_event(self, channel: str, agent: str, event_type: str, payload: Dict[str, Any]):
        self._impl.publish_event(channel, agent, event_type, payload)

    def stream_thought(self, agent: str, thought: str):
        self._impl.stream_thought(agent, thought)

    def broadcast_file_change(self, file_path: str, content: str, file_hash: str):
        self._impl.broadcast_file_change(file_path, content, file_hash)

    def log_remote_event(self, agent: str, event: str, payload: Dict[str, Any]):
        self._impl.log_remote_event(agent, event, payload)

    def enqueue_task(self, queue_name: str, task_data: Dict[str, Any]):
        self._impl.enqueue_task(queue_name, task_data)

    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        return self._impl.acquire_lock(lock_name, timeout)

    def release_lock(self, lock_name: str):
        self._impl.release_lock(lock_name)

    def listen(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        self._impl.listen(channel, callback)

    # --- Delegations for Distributed Methods ---
    def list_active_workers(self) -> List[Dict[str, Any]]:
        return self._impl.list_active_workers()

    def select_best_worker(self, required_cpu: float = 20.0) -> Optional[str]:
        return self._impl.select_best_worker(required_cpu)

    def auction_task(self, node_name: str, state: Dict[str, Any], timeout: int = 5) -> Optional[str]:
        return self._impl.auction_task(node_name, state, timeout)

    def call_remote_node(self, node_name: str, state: Dict[str, Any], timeout: int = 120) -> Optional[Dict[str, Any]]:
        return self._impl.call_remote_node(node_name, state, timeout)

    def call_remote_nodes_parallel(self, requests: List[Tuple[str, Dict[str, Any]]], timeout: int = 120) -> List[Dict[str, Any]]:
        return self._impl.call_remote_nodes_parallel(requests, timeout)

    def announce_presence(self, swarm_id: str, capabilities: List[str]):
        self._impl.announce_presence(swarm_id, capabilities)


# 글로벌 인스턴스
mq_bus = GortexMessageBus()
