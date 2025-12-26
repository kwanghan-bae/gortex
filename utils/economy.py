import logging
from datetime import datetime
from typing import Dict, Any
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
        agent_id = agent_name.lower()
        if agent_id not in economy:
            economy[agent_id] = {
                "points": 100,
                "level": "Bronze",
                "achievements": [],
                "success_rate": 100.0,
                "total_tasks": 0,
                "skill_points": {
                    "Coding": 0,
                    "Research": 0,
                    "Design": 0,
                    "Analysis": 0,
                    "General": 0
                }
            }

    def update_skill_points(self, state: GortexState, agent_name: str, category: str, quality_score: float, difficulty: float):
        """특정 분야의 숙련도 포인트 업데이트 및 랭크업 관리"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        agent_id = agent_name.lower()
        skills = economy[agent_id].get("skill_points", {})
        if category not in skills:
            skills[category] = 0
            
        # 획득 포인트 계산: (기본 10) * 품질 * 난이도
        gain = int(10 * quality_score * difficulty)
        old_val = skills[category]
        new_val = old_val + gain
        skills[category] = new_val
        
        # 랭크업 체크 (500점 단위로 칭호 부여)
        ranks = {0: "Apprentice", 500: "Journeyman", 1500: "Expert", 3000: "Master"}
        new_rank = "Apprentice"
        for threshold, title in sorted(ranks.items()):
            if new_val >= threshold:
                new_rank = title
                
        old_rank = "Apprentice"
        for threshold, title in sorted(ranks.items()):
            if old_val >= threshold:
                old_rank = title
                
        if new_rank != old_rank:
            achievement = f"🎓 Agent {agent_name} is now a {new_rank} in {category}!"
            if "achievements" not in state: state["achievements"] = []
            state["achievements"].append({"time": datetime.now().strftime("%H:%M:%S"), "text": achievement})
            logger.info(f"🌟 SKILL RANK UP: {achievement}")
            
        economy[agent_id]["skill_points"] = skills
        return gain

    def record_skill_gain(self, state: GortexState, agent_name: str, category: str, points: int):
        """특정 분야의 스킬 포인트 적립"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        agent_id = agent_name.lower()
        skills = economy[agent_id].get("skill_points", {})
        if category in skills:
            skills[category] += points
            logger.info(f"🎓 Agent {agent_name} gained {points} pts in {category}. (Total: {skills[category]})")
        
        economy[agent_id]["skill_points"] = skills

    def calculate_weighted_reward(self, quality_score: float, difficulty: float = 1.0, efficiency_bonus: float = 0.0) -> int:
        """난이도, 품질, 효율성을 고려한 가중 보상액 계산"""
        # 기본 보상(10) * 품질(0~2) * 난이도(1~3) + 효율 보너스
        reward = (self.base_reward * quality_score * difficulty) + (efficiency_bonus * 5)
        return int(max(1, reward))

    def record_success(self, state: GortexState, agent_name: str, quality_score: float = 1.0, difficulty: float = 1.0, efficiency_bonus: float = 0.0):
        """작업 성공 시 보상 지급 (가중치 반영)"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        agent_id = agent_name.lower()
        # 가중 보상 계산
        reward = self.calculate_weighted_reward(quality_score, difficulty, efficiency_bonus)
        economy[agent_id]["points"] += reward
        economy[agent_id]["total_tasks"] += 1
        
        # 레벨 업 로직 (단순화)
        points = economy[agent_id]["points"]
        old_level = economy[agent_id]["level"]
        new_level = old_level
        
        if points > 2000:
            new_level = "Diamond"
        elif points > 1000:
            new_level = "Gold"
        elif points > 500:
            new_level = "Silver"
        
        if new_level != old_level:
            economy[agent_id]["level"] = new_level
            achievement = f"🌟 Agent {agent_name} promoted to {new_level}!"
            if "achievements" not in state:
                state["achievements"] = []
            state["achievements"].append({"time": datetime.now().strftime("%H:%M:%S"), "text": achievement})
            logger.info(f"🏆 ACHIEVEMENT UNLOCKED: {achievement}")
        
        logger.info(f"💰 Agent {agent_name} rewarded {reward} points. (Total: {points})")
        return reward

    def record_failure(self, state: GortexState, agent_name: str, penalty_factor: float = 1.0):
        """작업 실패 시 페널티 부여"""
        economy = state.get("agent_economy", {})
        self.initialize_agent(economy, agent_name)
        
        agent_id = agent_name.lower()
        penalty = int(self.base_reward * 0.5 * penalty_factor)
        economy[agent_id]["points"] = max(0, economy[agent_id]["points"] - penalty)
        economy[agent_id]["total_tasks"] += 1
        
        logger.warning(f"📉 Agent {agent_name} penalized {penalty} points.")
        return penalty

    def can_use_pro_model(self, state: GortexState, agent_name: str) -> bool:
        """에이전트가 고성능 모델을 사용할 자격이 있는지 확인"""
        economy = state.get("agent_economy", {})
<<<<<<< HEAD
        agent_id = agent_name.lower()
        if agent_id not in economy: return False
        return economy[agent_id]["points"] >= self.pro_threshold
=======
        if agent_name not in economy:
            return False
        return economy[agent_name]["points"] >= self.pro_threshold
>>>>>>> origin/main

def get_economy_manager() -> EconomyManager:
    return EconomyManager()