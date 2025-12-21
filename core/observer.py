import json
import logging
import uuid
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger("GortexObserver")

class GortexObserver:
    """
    시스템의 모든 동작(사고, 도구 호출, 오류)을 감시하고 구조화된 로그를 생성합니다.
    """
    def __init__(self, log_path: str = "logs/trace.jsonl"):
        self.log_path = log_path
        self.trace_id = str(uuid.uuid4())
        self._ensure_log_dir()
        self._rotate_logs()

    def _ensure_log_dir(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def _rotate_logs(self, max_size_mb: int = 10):
        """로그 파일 크기가 크면 백업"""
        if os.path.exists(self.log_path):
            if os.path.getsize(self.log_path) > max_size_mb * 1024 * 1024:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                shutil.move(self.log_path, f"{self.log_path}.{ts}.bak")
                logger.info(f"Logs rotated: {self.log_path}.{ts}.bak")

    def log_event(self, agent: str, event_type: str, payload: Any, latency_ms: Optional[int] = None, tokens: Optional[Dict[str, int]] = None, cause_id: Optional[str] = None):
        """이벤트를 JSONL 형식으로 기록 (인과 관계 추적 지원)"""
        event_id = str(uuid.uuid4())[:8]
        entry = {
            "id": event_id,
            "timestamp": datetime.now().isoformat(),
            "trace_id": self.trace_id,
            "agent": agent,
            "event": event_type, # 'thought', 'tool_call', 'node_complete', 'error'
            "payload": payload,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "cause_id": cause_id # 원인이 된 이전 이벤트 ID
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace log: {e}")
        return event_id

    def get_causal_chain(self, start_event_id: str) -> List[Dict[str, Any]]:
        """특정 이벤트 ID로부터 루트까지 인과 관계 체인을 역추적"""
        if not os.path.exists(self.log_path):
            return []
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f]
            
            # ID 기반 검색 맵 생성
            log_map = {l["id"]: l for l in logs if "id" in l}
            
            chain = []
            current_id = start_event_id
            
            # 순환 참조 방지를 위해 최대 깊이 제한
            for _ in range(100):
                if current_id not in log_map:
                    break
                event = log_map[current_id]
                chain.append(event)
                current_id = event.get("cause_id")
                if not current_id:
                    break
            return chain # [최신 -> 과거] 순서
        except Exception as e:
            logger.error(f"Failed to trace causal chain: {e}")
            return []

# LangChain Callback 형식으로 확장 가능 (여기서는 단순화된 형태 제공)
class FileLoggingCallbackHandler:
    def __init__(self, observer: GortexObserver):
        self.observer = observer

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any):
        self.observer.log_event("Chain", "start", inputs)

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any):
        self.observer.log_event("Tool", "start", input_str)

    def on_tool_end(self, output: str, **kwargs: Any):
        self.observer.log_event("Tool", "end", output)
