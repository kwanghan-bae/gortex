import json
import logging
import uuid
import time
from typing import List, Dict, Any, Optional
from gortex.core.mq import mq_bus
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexAmbassador")

class SwarmAmbassador:
    """
    다른 Gortex 군집과의 외교 및 지식 전파를 담당함.
    지식 공유(Sharing) 및 자원 협상(Negotiation)의 중추.
    """
    def __init__(self, swarm_id: str = None):
        self.swarm_id = swarm_id or f"swarm_{uuid.uuid4().hex[:6]}"
        self.memory = EvolutionaryMemory()

    def broadcast_wisdom(self, category: str = "coding"):
        """로컬의 고성과 Super Rule을 연합 네트워크에 공유함"""
        if not mq_bus.is_connected: return
        
        # 공인된 최상위 지침만 선별
        wisdom = [r for r in self.memory.shards.get(category, []) if r.get("is_super_rule") and r.get("severity") >= 4]
        
        if wisdom:
            logger.info(f"🌌 [Ambassador] Broadcasting {len(wisdom)} rules to Galactic Swarm.")
            mq_bus.publish_event("gortex:galactic:wisdom", self.swarm_id, "wisdom_shared", {
                "category": category,
                "rules": wisdom
            })

    def integrate_remote_wisdom(self, remote_swarm_id: str, remote_rules: List[Dict[str, Any]]):
        """외부 군집으로부터 수신한 지식을 로컬에 통합함"""
        if remote_swarm_id == self.swarm_id: return
        
        integrated_count = 0
        for rule in remote_rules:
            # 중복 체크 후 저장 (context에 출처 명시)
            rule_id = self.memory.save_rule(
                instruction=rule["learned_instruction"],
                trigger_patterns=rule["trigger_patterns"],
                category=rule.get("category", "general"),
                severity=rule.get("severity", 3),
                is_super_rule=True,
                context=f"Federated Wisdom from {remote_swarm_id}"
            )
            if rule_id: integrated_count += 1
            
        if integrated_count > 0:
            logger.info(f"🌌 [Ambassador] Integrated {integrated_count} rules from {remote_swarm_id}.")

    def request_external_help(self, node_name: str, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """로컬 자원이 부족할 때 연합 군집에 지원 요청"""
        # (v7.5의 핵심인 Cross-Swarm RPC 구현 지점)
        logger.info(f"🌌 [Ambassador] Local resources exhausted. Requesting aid for '{node_name}'...")
        # 연합 전용 큐에 태스크 전송
        mq_bus.enqueue_task("gortex:galactic:tasks", {
            "requester": self.swarm_id,
            "node": node_name,
            "state": state,
            "reply_to": f"gortex:galactic:resp:{self.swarm_id}"
        })
        return None # 비동기 대기 로직 필요

# 글로벌 인스턴스
ambassador = SwarmAmbassador()
