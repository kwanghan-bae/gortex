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
        """로컬의 고성과 Super Rule을 연합 네트워크에 다국어로 공유함"""
        if not mq_bus.is_connected: return
        
        # 1. 고가치 지식 선별
        wisdom = [r for r in self.memory.shards.get(category, []) if r.get("is_super_rule") and r.get("severity") >= 4]
        
        if wisdom:
            logger.info(f"🌌 [Ambassador] Distilling and Translating {len(wisdom)} rules for Galactic Swarm...")
            
            from gortex.utils.translator import SynapticTranslator
            translator = SynapticTranslator()
            
            translated_wisdom = []
            for rule in wisdom[:3]: # 과부하 방지: 상위 3개만
                # 다국어 번역본 생성
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
        from gortex.utils.economy import get_economy_manager
        eco = get_economy_manager()
        
        # 1. 비용 지불 (모든 에이전트가 공동 부담하거나 Manager가 지불)
        total_balance = sum(a.get("credits", 0) for a in state.get("agent_economy", {}).values())
        if total_balance < price:
            logger.warning(f"💸 Insufficient funds to buy wisdom from {seller_id}")
            return False
            
        # 2. 지식 통합
        self.integrate_remote_wisdom(seller_id, rules)
        
        # 3. 크레딧 차감 및 판매자 수익 알림 (판매자 정산은 MQ 이벤트로 처리)
        for agent_id in state["agent_economy"]:
            state["agent_economy"][agent_id]["credits"] -= (price / len(state["agent_economy"]))
            
        mq_bus.publish_event("gortex:galactic:economy", self.swarm_id, "payment_sent", {
            "to": seller_id,
            "amount": price,
            "item": "wisdom_pack"
        })
        return True

    def rent_compute_resource(self, node_name: str, state: GortexState, price_limit: float = 1.0) -> Optional[Dict[str, Any]]:
        """타 스웜의 연산 자원을 임대하여 노드 실행"""
        # ... (기존 로직)
        pass

    # [GALACTIC GOVERNANCE] 전역 합의 시스템
    def propose_galactic_agenda(self, title: str, goal: str, required_resources: int):
        """연합망 전체에 공동의 대규모 미션을 제안함"""
        agenda_id = f"agenda_{uuid.uuid4().hex[:6]}"
        message = {
            "agenda_id": agenda_id,
            "proposer": self.swarm_id,
            "title": title,
            "goal": goal,
            "resources_needed": required_resources,
            "timestamp": time.time()
        }
        logger.info(f"🌌 [Ambassador] Proposing Galactic Agenda: {title}")
        mq_bus.publish_event("gortex:galactic:agendas", self.swarm_id, "agenda_proposed", message)
        return agenda_id

    def cast_federated_vote(self, agenda_id: str, is_approved: bool, reason: str):
        """상정된 전역 안건에 대해 투표권을 행사함"""
        vote = {
            "agenda_id": agenda_id,
            "voter": self.swarm_id,
            "approved": is_approved,
            "reason": reason,
            "voting_power": 10.0 # (실제 구현 시 해당 스웜의 SMI 점수 등을 반영)
        }
        mq_bus.publish_event("gortex:galactic:votes", self.swarm_id, "vote_cast", vote)
        logger.info(f"🌌 [Ambassador] Cast vote for agenda {agenda_id}: {'YES' if is_approved else 'NO'}")

# 글로벌 인스턴스
ambassador = SwarmAmbassador()

