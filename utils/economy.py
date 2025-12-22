import logging
from typing import Dict, Any, List, Optional
from gortex.core.state import GortexState

logger = logging.getLogger("GortexEconomy")

class EconomyManager:
    """
    에이전트 평판, 포인트, 업적 등 시스템 내부 경제를 관리함.
    """
    def __init__(self):
        self.base_reward = 10
        self.pro_threshold = 1000 # 고성능 모델 사용 가능 평판 임계치

    def initialize_agent(self, economy: Dict[str, Any], agent_name: str):
        """에이전트 경제 데이터 초기화"""
        if agent_name not in economy:
            economy[agent_name] = {
                "points": 100,
                "level": "Bronze",
                "achievements": [],
                "success_rate": 100.0,
                "total_tasks": 0
            }

    def record_success(self, state: GortexState, agent_name: str, quality_score: float = 1.0):
        """작업 성공 시 보상 지급 (품질 점수 반영)"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        # 보상 계산 (기본 보상 * 품질 점수)
        reward = int(self.base_reward * quality_score)
        economy[agent_name]["points"] += reward
        economy[agent_name]["total_tasks"] += 1
        
        # 레벨 업 로직 (단순화)
        points = economy[agent_name]["points"]
        if points > 2000: economy[agent_name]["level"] = "Diamond"
        elif points > 1000: economy[agent_name]["level"] = "Gold"
        elif points > 500: economy[agent_name]["level"] = "Silver"
        
        logger.info(f"💰 Agent {agent_name} rewarded {reward} points. (Total: {points})")
        return reward

    def record_failure(self, state: GortexState, agent_name: str, penalty_factor: float = 1.0):
        """작업 실패 시 페널티 부여"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        penalty = int(self.base_reward * 0.5 * penalty_factor)
        economy[agent_name]["points"] = max(0, economy[agent_name]["points"] - penalty)
        economy[agent_name]["total_tasks"] += 1
        
        logger.warning(f"📉 Agent {agent_name} penalized {penalty} points.")
        return penalty

    def can_use_pro_model(self, state: GortexState, agent_name: str) -> bool:
        """에이전트가 고성능 모델을 사용할 자격이 있는지 확인"""
        economy = state.get("agent_economy", {})
        if agent_name not in economy: return False
        return economy[agent_name]["points"] >= self.pro_threshold

def get_economy_manager() -> EconomyManager:
    return EconomyManager()
