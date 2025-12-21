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

    def log_event(self, agent: str, event_type: str, payload: Any, latency_ms: Optional[int] = None, tokens: Optional[Dict[str, int]] = None):
        """이벤트를 JSONL 형식으로 기록 (정밀 프로파일링 지원)"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": self.trace_id,
            "agent": agent,
            "event": event_type, # 'thought', 'tool_call', 'node_complete', 'error'
            "payload": payload,
            "latency_ms": latency_ms,
            "tokens": tokens # {"input": 100, "output": 50} 형식
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace log: {e}")

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
