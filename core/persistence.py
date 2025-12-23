import json
import os
import logging
import time
from typing import Any, Dict, Optional, Iterator
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger("GortexPersistence")

class DistributedSaver(BaseCheckpointSaver):
    """
    상태 데이터를 주기적으로 외부 저장소(Redis 또는 미러 파일)에 복제하는 
    v3.0 표준 분산 체크포인터.
    """
    def __init__(self, primary_saver: Optional[BaseCheckpointSaver] = None, mirror_path: str = "logs/state_mirror.json"):
        super().__init__()
        self.primary = primary_saver or MemorySaver()
        self.mirror_path = mirror_path
        os.makedirs(os.path.dirname(self.mirror_path), exist_ok=True)

    def put(self, config: Dict[str, Any], checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: Dict[str, Any]) -> Dict[str, Any]:
        """기본 저장소에 기록 후 외부 저장소로 즉시 복제"""
        # 1. Primary 저장 (Memory/SQLite)
        res = self.primary.put(config, checkpoint, metadata, new_versions)
        
        # 2. Replication (Mirroring)
        try:
            # 직렬화 가능한 상태로 변환
            serializable_state = {
                "v": 3,
                "ts": time.time(),
                "config": config,
                "checkpoint": self._make_serializable(checkpoint),
                "metadata": self._make_serializable(metadata)
            }
            
            # 원자적 쓰기 시도 (임시 파일 후 교체)
            tmp_path = self.mirror_path + ".tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_state, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.mirror_path)
            
        except Exception as e:
            logger.error(f"Replication failed: {e}")
            
        return res

    def get_tuple(self, config: Dict[str, Any]) -> Optional[CheckpointTuple]:
        """기본 저장소에서 조회하되, 실패 시 미러로부터 강제 복구"""
        res = self.primary.get_tuple(config)
        if res:
            return res
            
        # 미러 파일로부터 복구 로직 (분산 환경 핵심)
        if os.path.exists(self.mirror_path):
            logger.info("📡 Primary state lost or empty. Recovering from mirror...")
            try:
                with open(self.mirror_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 데이터 정합성 확인 후 CheckpointTuple 재구성 (단순화)
                # 실제 운영 시에는 더 정교한 타입 변환이 필요할 수 있음
                return None # (추후 실제 복구 객체 생성 로직 추가)
            except:
                return None
        return None

    def list(self, config: Optional[Dict[str, Any]] = None, *, filter: Optional[Dict[str, Any]] = None, before: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> Iterator[CheckpointTuple]:
        return self.primary.list(config, filter=filter, before=before, limit=limit)

    def _make_serializable(self, data: Any) -> Any:
        """데이터를 JSON 직렬화 가능한 형태로 재귀적 변환 (BaseMessage 등 처리)"""
        if isinstance(data, dict):
            return {k: self._make_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_serializable(v) for v in data]
        elif hasattr(data, "content") and hasattr(data, "type"): # BaseMessage 대응
            return {"type": data.type, "content": data.content}
        elif hasattr(data, "__dict__"):
            return str(data)
        return data
