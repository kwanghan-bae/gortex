import json
import logging
import uuid
import os
import shutil
from datetime import datetime
from typing import Any, Dict, Optional, List

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

    def archive_and_reset_logs(self) -> str:
        """현재 로그를 압축 아카이빙하고 원본을 초기화함 (리소스 최적화)"""
        if not os.path.exists(self.log_path) or os.path.getsize(self.log_path) == 0:
            return "Log file is already empty or missing."

        try:
            archive_dir = "logs/archives"
            os.makedirs(archive_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_path = os.path.join(archive_dir, f"trace_archive_{timestamp}.zip")
            
            # 임시 파일로 복사 후 압축 (쓰기 잠금 방지)
            temp_path = self.log_path + ".tmp"
            shutil.copy2(self.log_path, temp_path)
            
            # 압축 수행 (파일 하나만 압축하므로 compress_directory 활용 또는 직접 구현)
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_path, os.path.basename(self.log_path))
            
            os.remove(temp_path)
            
            # 원본 로그 초기화 (Truncate)
            with open(self.log_path, 'w') as f:
                f.write("")
                
            logger.info(f"📁 Trace logs archived to {zip_path} and reset.")
            return zip_path
        except Exception as e:
            logger.error(f"Failed to archive logs: {e}")
            return f"Error: {e}"

    def _rotate_logs(self, max_size_mb: int = 10):
        """로그 파일 크기가 크면 자동으로 아카이빙 트리거"""
        if os.path.exists(self.log_path):
            if os.path.getsize(self.log_path) > max_size_mb * 1024 * 1024:
                logger.warning(f"⚠️ Log size exceeded {max_size_mb}MB. Triggering auto-archive.")
                self.archive_and_reset_logs()

    def get_stats(self) -> Dict[str, Any]:
        """누적 통계 데이터 반환"""
        total_tokens = 0
        total_cost = 0.0
        start_time = None
        event_count = 0
        
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip(): continue
                        data = json.loads(line)
                        event_count += 1
                        
                        # 토큰 및 비용 합산
                        if "tokens" in data and data["tokens"]:
                            if isinstance(data["tokens"], dict):
                                total_tokens += data["tokens"].get("total", 0)
                            elif isinstance(data["tokens"], (int, float)):
                                total_tokens += int(data["tokens"])
                        
                        if not start_time:
                            start_time = datetime.fromisoformat(data["timestamp"])
            except Exception as e:
                logger.warning(f"Error reading stats from log: {e}")

        uptime = "N/A"
        if start_time:
            delta = datetime.now() - start_time
            uptime = str(delta).split(".")[0] # HH:MM:SS 형식

        return {
            "total_tokens": total_tokens,
            "total_cost": round(total_tokens * 0.000002, 6),
            "uptime": uptime,
            "event_count": event_count,
            "trace_id": self.trace_id
        }

    def log_event(self, agent: str, event: str, payload: Any, latency_ms: Optional[int] = None, tokens: Optional[Dict[str, int]] = None, cause_id: Optional[str] = None):
        """이벤트를 JSONL 형식으로 기록 (인과 관계 추적 지원)"""
        # [SECURITY] 도구 호출 시 사전 검증 수행 (Neural Firewall)
        if event == "tool_call":
            self.validate_tool_call(agent, payload)
            
        event_id = str(uuid.uuid4())[:8]
        entry = {
            "id": event_id,
            "timestamp": datetime.now().isoformat(),
            "trace_id": self.trace_id,
            "agent": agent,
            "event": event,
            "payload": payload,
            "latency_ms": latency_ms,
            "tokens": tokens,
            "cause_id": cause_id
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write trace log: {e}")
        return event_id

    def validate_tool_call(self, agent: str, payload: Any):
        """도구 호출의 보안 정책 위반 여부를 실시간 검사함 (다중 서명 지원)"""
        from gortex.core.evolutionary_memory import EvolutionaryMemory
        memory = EvolutionaryMemory()
        
        # 1. 전역 보안 정책 및 고위험 도구 식별
        security_rules = [r for r in memory.memory if r.get("is_super_rule") and r.get("severity", 0) >= 4]
        
        # [NEW] 다중 서명이 필요한 초고위험 도구 리스트
        multi_sig_tools = ["execute_shell", "git_push", "delete_branch", "ingest_remote_agent"]
        tool_name = str(payload.get("action", "")) if isinstance(payload, dict) else ""
        
        # 2. 다중 서명 체크
        if tool_name in multi_sig_tools:
            logger.info(f"🔑 [Multi-Sig] Tool '{tool_name}' requested by {agent}. Initiating swarm approval...")
            # [EVENT] 승인 요청 발행
            from gortex.core.mq import mq_bus
            mq_bus.publish_event("gortex:security_alerts", agent, "approval_requested", {
                "tool": tool_name,
                "payload": payload,
                "required_trust": 1.5 # 합산 신뢰도 임계치
            })
            # (실제 동기적 대기 로직은 엔진과 Swarm 연동 필요 - 현재는 흐름 구축)
            
        # 3. 페이로드 문자열 분석 (기존 로직)
        payload_str = str(payload).lower()
        for rule in security_rules:
            for pattern in rule.get("trigger_patterns", []):
                if pattern.lower() in payload_str:
                    logger.critical(f"🛑 [Sentinel] Security Violation! Agent '{agent}' tried to violate rule: {rule['learned_instruction']}")
                    from gortex.core.mq import mq_bus
                    mq_bus.publish_event("gortex:security_alerts", agent, "security_violation", {
                        "rule_id": rule["id"],
                        "violation": rule["learned_instruction"],
                        "payload": payload
                    })
                    raise PermissionError(f"Security Policy Violation: {rule['learned_instruction']}")

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

    def get_collaboration_matrix(self, limit: int = 500) -> Dict[str, Dict[str, int]]:
        """로그를 분석하여 에이전트 간 호출 빈도(Collaboration Matrix) 산출"""
        if not os.path.exists(self.log_path):
            return {}
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f][-limit:]
            
            # ID 기반 검색 맵 (최적화)
            event_agent_map = {l["id"]: l["agent"] for l in logs if "id" in l}
            
            matrix = {} # {caller: {callee: count}}
            
            for l in logs:
                callee = l["agent"]
                cause_id = l.get("cause_id")
                
                if cause_id and cause_id in event_agent_map:
                    caller = event_agent_map[cause_id]
                    
                    # 자기 자신 호출 제외
                    if caller == callee:
                        continue
                        
                    if caller not in matrix: matrix[caller] = {}
                    matrix[caller][callee] = matrix[caller].get(callee, 0) + 1
                    
            return matrix
        except Exception as e:
            logger.error(f"Failed to generate collaboration matrix: {e}")
            return {}

    def get_causal_graph(self, limit: int = 200) -> Dict[str, Any]:
        """전체 로그를 바탕으로 인과 관계 그래프(Nodes/Edges) 생성"""
        if not os.path.exists(self.log_path):
            return {"nodes": [], "edges": []}
            
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                logs = [json.loads(line) for line in f][-limit:]
            
            nodes = []
            edges = []
            
            for l in logs:
                # 노드 정보 구성
                nodes.append({
                    "id": l["id"],
                    "label": f"{l['agent']}: {l['event']}",
                    "agent": l["agent"],
                    "event": l["event"],
                    "timestamp": l["timestamp"]
                })
                # 인과 관계 엣지 구성
                if l.get("cause_id"):
                    edges.append({"from": l["cause_id"], "to": l["id"]})
                    
            return {"nodes": nodes, "edges": edges}
        except Exception as e:
            logger.error(f"Failed to generate causal graph: {e}")
            return {"nodes": [], "edges": []}

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
