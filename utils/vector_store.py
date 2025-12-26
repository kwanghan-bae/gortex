import json
import os
import logging
import math
import uuid
from datetime import datetime
from typing import List, Dict, Any
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexVectorStore")

class LongTermMemory:
    """
    세션이 종료되어도 유지되는 의미 기반 지식 저장소 (장기 기억).
    Redis와 연동하여 분산 환경에서 지식을 실시간 동기화합니다.
    """
    def __init__(self, store_dir: str = "logs/memory"):
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)
        self.auth = GortexAuth()
        self.shards: Dict[str, List[Dict[str, Any]]] = {}
        
        # [DISTRIBUTED] MQ 연동 및 백그라운드 리스너 시작
        from gortex.core.mq import mq_bus
        self.mq = mq_bus
        if self.mq.is_connected:
            self._start_sync_listener()

    def _start_sync_listener(self):
        """실시간 지식 동기화를 위한 백그라운드 스레드 시작"""
        import threading
        
        def _listen():
            def handle_sync(msg):
                payload = msg.get("payload", {})
                namespace = payload.get("namespace")
                if namespace:
                    logger.debug(f"♻️ Received knowledge sync for '{namespace}'. Refreshing...")
                    # 로컬 샤드 캐시 무효화 (다음 로드 시 Redis/파일에서 최신본 읽음)
                    if namespace in self.shards:
                        del self.shards[namespace]
            
            try:
                self.mq.listen("gortex:memory_sync", handle_sync)
            except Exception as e:
                logger.error(f"Memory sync listener failed: {e}")

        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()

    def _load_shard(self, namespace: str) -> List[Dict[str, Any]]:
        if namespace in self.shards:
            return self.shards[namespace]
            
        # 1. Redis 전역 저장소 확인
        if self.mq.is_connected:
            try:
                redis_key = f"gortex:ltm:shard:{namespace}"
                data_str = self.mq.client.get(redis_key)
                if data_str:
                    data = json.loads(data_str)
                    self.shards[namespace] = data
                    return data
            except Exception as e:
                logger.warning(f"Failed to load LTM shard from Redis: {e}")

        # 2. 로컬 파일 (Fallback)
        path = self._get_shard_path(namespace)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.shards[namespace] = data
                    return data
            except Exception:
                return []
        return []

    def _save_shard(self, namespace: str):
        if namespace not in self.shards:
            return
        data = self.shards[namespace]
        
        # 1. Redis 전역 싱크
        if self.mq.is_connected:
            try:
                redis_key = f"gortex:ltm:shard:{namespace}"
                self.mq.client.set(redis_key, json.dumps(data, ensure_ascii=False, indent=2), ex=3600*48)
                # 동기화 이벤트 발행
                self.mq.publish_event("gortex:memory_sync", "Memory", "ltm_updated", {"namespace": namespace})
            except Exception as e:
                logger.error(f"Failed to sync LTM to Redis: {e}")

        # 2. 로컬 파일 저장
        path = self._get_shard_path(namespace)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @property
    def memory(self) -> List[Dict[str, Any]]:
        """AnalystAgent 등의 하위 호환성을 위해 'global' 샤드를 기본 메모리로 반환"""
        return self._load_shard("global")

    @memory.setter
    def memory(self, value: List[Dict[str, Any]]):
        self.shards["global"] = value

    def _save_store(self):
        """AnalystAgent 등에서 호출하는 저장 메서드 (global 샤드 저장)"""
        self._save_shard("global")

    def _get_embedding(self, text: str) -> List[float]:
        """Gemini API를 사용하여 텍스트 임베딩 생성"""
        try:
            # 텍스트가 너무 길면 절삭
            clean_text = text[:2000]
            # GortexAuth를 통해 현재 활성 클라이언트 획득
            client = self.auth.get_current_client()
            if not client:
                logger.warning("No active client for embedding. Falling back to zero-vector.")
                return [0.0] * 768

            response = client.models.embed_content(
                model="models/embedding-001",
                contents=clean_text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.warning(f"Embedding failed: {e}. Falling back to zero-vector.")
            return [0.0] * 768 # 기본 차원

    def memorize(self, text: str, metadata: Dict[str, Any] = None, namespace: str = "global"):
        """특정 네임스페이스(샤드)에 지식을 저장"""
        vector = self._get_embedding(text)
        shard = self._load_shard(namespace)
        
        shard.append({
            "id": str(uuid.uuid4())[:8],
            "content": text,
            "vector": vector,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0,
            "links": []
        })
        self.shards[namespace] = shard
        self._save_shard(namespace)
        logger.info(f"🧠 Knowledge memorized in shard: {namespace}")

    def search(self, query: str = "", limit: int = 10, namespace: str = "global") -> List[Dict[str, Any]]:
        """UI와 호환되는 검색 인터페이스 (recall의 별칭 및 확장)"""
        if not query:
            # 쿼리가 없으면 최근 지식 반환
            shard = self._load_shard(namespace)
            results = []
            for item in shard[-limit:]:
                results.append({
                    "id": item["id"],
                    "content": item["content"],
                    "metadata": item.get("metadata", {}),
                    "score": 1.0,
                    "is_global": self.mq.is_connected
                })
            return list(reversed(results))
            
        results = self.recall(query, limit=limit, namespace=namespace)
        for r in results:
            r["is_global"] = self.mq.is_connected
        return results

    def recall(self, query: str, limit: int = 3, namespace: str = "global") -> List[Dict[str, Any]]:
        """특정 네임스페이스(샤드)에서 지식 소환"""
        shard = self._load_shard(namespace)
        if not shard:
            return []
            
        query_vector = self._get_embedding(query)
        scored_results = []
        
        for item in shard:
            if "vector" in item and len(item["vector"]) == len(query_vector):
                dot_product = sum(a * b for a, b in zip(query_vector, item["vector"]))
                norm_a = math.sqrt(sum(a * a for a in query_vector))
                norm_b = math.sqrt(sum(b * b for b in item["vector"]))
                similarity = dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
                scored_results.append((similarity, item))
            else:
                match_score = 0.1 if any(p in item["content"].lower() for p in query.lower().split()) else 0
                scored_results.append((match_score, item))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        final_results = []
        for score, item in scored_results[:limit]:
            if score > 0.3:
                if score > 0.5:
                    item["usage_count"] = item.get("usage_count", 0) + 1
                final_results.append({
                    "content": item["content"], 
                    "metadata": item.get("metadata", {}), 
                    "score": round(score, 2)
                })
            
        if final_results:
            self._save_shard(namespace)
        return final_results

if __name__ == "__main__":
    # 독립 실행 테스트
    ltm = LongTermMemory()
    ltm.memorize("Gortex의 샤딩 엔진이 활성화되었다.", {"topic": "system"}, namespace="test_project")
    print(ltm.recall("샤딩", namespace="test_project"))
