import json
import logging
import uuid
import time
from typing import List, Dict, Any, Optional
from gortex.core.mq import mq_bus
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.core.state import GortexState

logger = logging.getLogger("GortexAmbassador")

class SwarmAmbassador:
    """
    다른 Gortex 군집과의 외교, 지식 거래, 갈등 중재를 담당함.
    지구적 지능 연합의 중추적인 외교 창구.
    """
    def __init__(self, swarm_id: str = None):
        self.swarm_id = swarm_id or f"swarm_{uuid.uuid4().hex[:6]}"
        self.memory = EvolutionaryMemory()

    def broadcast_wisdom(self, category: str = "coding"):
        """로컬의 고성과 Super Rule을 연합 네트워크에 다국어로 공유함"""
        if not mq_bus.is_connected: return
        
        wisdom = [r for r in self.memory.shards.get(category, []) if r.get("is_super_rule") and r.get("severity") >= 4]
        
        if wisdom:
            logger.info(f"🌌 [Ambassador] Distilling and Translating {len(wisdom)} rules for Galactic Swarm...")
            from gortex.utils.translator import SynapticTranslator
            translator = SynapticTranslator()
            
            translated_wisdom = []
            for rule in wisdom[:3]:
                translations = translator.translate_knowledge_shard(rule)
                rule_copy = rule.copy()
                rule_copy["translations"] = translations
                translated_wisdom.append(rule_copy)

            mq_bus.publish_event("gortex:galactic:wisdom", self.swarm_id, "wisdom_offered", {
                "category": category,
                "rules": translated_wisdom,
                "price": 5.0
            })

    def purchase_remote_wisdom(self, seller_id: str, rules: List[Dict[str, Any]], price: float, state: GortexState):
        """타 스웜의 지식을 구매하여 통합함"""
        total_balance = sum(a.get("credits", 0) for a in state.get("agent_economy", {}).values())
        if total_balance < price:
            logger.warning(f"💸 Insufficient funds to buy wisdom from {seller_id}")
            return False
            
        self.integrate_remote_wisdom(seller_id, rules)
        
        for agent_id in state["agent_economy"]:
            state["agent_economy"][agent_id]["credits"] -= (price / len(state["agent_economy"]))
            
        mq_bus.publish_event("gortex:galactic:economy", self.swarm_id, "payment_sent", {
            "to": seller_id, "amount": price, "item": "wisdom_pack"
        })
        return True

    def integrate_remote_wisdom(self, remote_swarm_id: str, remote_rules: List[Dict[str, Any]]):
        """외부 군집으로부터 수신한 지식을 로컬에 통합함"""
        if remote_swarm_id == self.swarm_id: return
        integrated_count = 0
        for rule in remote_rules:
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

    def propose_galactic_agenda(self, title: str, goal: str, required_resources: int):
        """연합망 전체에 공동의 대규모 미션을 제안함"""
        agenda_id = f"agenda_{uuid.uuid4().hex[:6]}"
        message = {
            "agenda_id": agenda_id, "proposer": self.swarm_id, "title": title,
            "goal": goal, "resources_needed": required_resources, "timestamp": time.time()
        }
        mq_bus.publish_event("gortex:galactic:agendas", self.swarm_id, "agenda_proposed", message)
        return agenda_id

    def cast_federated_vote(self, agenda_id: str, is_approved: bool, reason: str):
        """상정된 전역 안건에 대해 투표권을 행사함"""
        vote = {"agenda_id": agenda_id, "voter": self.swarm_id, "approved": is_approved, "reason": reason, "voting_power": 10.0}
        mq_bus.publish_event("gortex:galactic:votes", self.swarm_id, "vote_cast", vote)

    def propose_mediation(self, conflict_id: str, rule_a: Dict[str, Any], rule_b: Dict[str, Any]):
        """두 스웜 간의 지식 갈등에 대해 중재를 요청함"""
        mq_bus.publish_event("gortex:galactic:mediation", self.swarm_id, "mediation_requested", {
            "conflict_id": conflict_id, "rules": [rule_a, rule_b], "required_grade": "Diamond"
        })

    def rent_compute_resource(self, node_name: str, state: GortexState, price_limit: float = 1.0) -> Optional[Dict[str, Any]]:
        """타 스웜의 연산 자원을 임대하여 노드 실행"""
        request_id = f"rent_{uuid.uuid4().hex[:4]}"
        mq_bus.publish_event("gortex:galactic:compute", self.swarm_id, "compute_requested", {
            "request_id": request_id, "node": node_name, "bid_limit": price_limit, "state": state
        })
        return None

# 글로벌 인스턴스
ambassador = SwarmAmbassador()