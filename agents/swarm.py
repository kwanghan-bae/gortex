import asyncio
import logging
import os
import re
import json
from typing import Dict, Any, List
from datetime import datetime
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.prompt_loader import PromptLoader
from gortex.core.registry import registry
from gortex.core.evolutionary_memory import EvolutionaryMemory

logger = logging.getLogger("GortexSwarm")

class SwarmAgent:
    """
    다중 에이전트 협업 및 토론(Debate)을 관장하는 Swarm Intelligence 모듈.
    상반된 페르소나 또는 실제 전문가(Swarm) 간의 라운드 기반 토론을 수행하고 합의를 도출합니다.
    """
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()
        self.prompts = PromptLoader()
        self.participants = [] # Recruited experts

    def recruit_experts(self, state: GortexState, required_skills: List[str]) -> List[Dict[str, Any]]:
        """요구되는 스킬에 대해 가장 높은 점수를 가진 전문가들을 소집함."""
        agent_eco = state.get("agent_economy", {})
        recruits = []
        recruited_names = set()

        for skill in required_skills:
            best_agent = None
            best_score = -1
            
            # 모든 에이전트를 순회하며 해당 스킬 점수 확인
            all_agents = registry.list_agents()
            for name in all_agents:
                data = agent_eco.get(name.lower(), {})
                score = data.get("skill_points", {}).get(skill, 0)
                if score > best_score:
                    best_score = score
                    best_agent = name
            
            if best_agent and best_agent not in recruited_names:
                meta = registry.get_metadata(best_agent)
                recruits.append({
                    "name": meta.name,
                    "role": meta.role,
                    "recruited_for": skill,
                    "skill_score": best_score,
                    "description": meta.description
                })
                recruited_names.add(best_agent)
                logger.info(f"🤝 Recruited {meta.name} (Role: {meta.role}) for {skill} (Score: {best_score})")

        # 만약 모집된 인원이 너무 적으면(1명 이하), Planner를 기본 보조자로 추가
        if len(recruits) < 2 and "Planner" not in recruited_names:
             meta = registry.get_metadata("Planner")
             if meta:
                 recruits.append({
                     "name": meta.name,
                     "role": meta.role,
                     "recruited_for": "Facilitation",
                     "skill_score": 0,
                     "description": meta.description
                 })
                 logger.info(f"🤝 Recruited Planner for facilitation (Fallback)")

        self.participants = recruits
        return recruits

    async def conduct_dynamic_round(self, topic: str, round_idx: int, history: List[Dict[str, str]], is_debug: bool = False) -> List[Dict[str, str]]:
        """모집된 전문가들이 각자의 전문성을 바탕으로 의견을 제시함."""
        responses = []
        
        # 만약 참여자가 없으면 기존 정적 페르소나 방식으로 폴백
        if not self.participants:
            return await self.conduct_static_round(topic, round_idx, history, is_debug)

        for expert in self.participants:
            role_ctx = f"You are {expert['name']}, the {expert['role']}. You were recruited for your expertise in {expert['recruited_for']}."
            
            if is_debug:
                 obj = "Analyze the error from your domain perspective and propose a specific fix."
                 if round_idx > 1: obj = "Critique previous proposals and refine the fix plan."
            else:
                 obj = "Propose a solution to the topic based on your specialized skills."
                 if round_idx > 1: obj = "Review other agents' ideas and suggest improvements or highlight risks."

            context_str = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in history])
            
            prompt = f"""{role_ctx}
            
            [Debate Topic]: {topic}
            [Current Round]: {round_idx}
            [Context]:
            {context_str}
            
            Your Objective: {obj}
            Keep it concise (under 200 words). Be highly technical.
            """
            
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, self.backend.generate, "gemini-2.0-flash", [{"role": "user", "content": prompt}])
            
            entry = {"role": expert["name"], "content": response_text, "round": round_idx, "persona": expert["role"]} # UI용 persona 필드 추가
            responses.append(entry)
            history.append(entry)
            
        return responses

    async def conduct_static_round(self, topic: str, round_idx: int, history: List[Dict[str, str]], is_debug: bool = False) -> List[Dict[str, str]]:
        """(Legacy) 정적 페르소나 기반 토론"""
        responses = []
        personas = ["innovation", "stability"]
        
        for p_name in personas:
            persona_prompt = self.prompts.get(f"persona_{p_name}")
            
            if is_debug:
                role_desc = "propose a radical fix hypothesis" if p_name == "innovation" else "propose a safe and minimal fix hypothesis"
                if round_idx > 1:
                    role_desc = "critique the other's hypothesis and refine your patch proposal"
            else:
                role_desc = "propose a radical solution" if p_name == "innovation" else "critique and propose a safer alternative"
                if round_idx > 1:
                    role_desc = "rebut the counter-arguments and refine your stance"

            context_str = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in history])
            
            prompt = f"""{persona_prompt}
            
            [Debate Topic/Error]: {topic}
            [Current Round]: {round_idx}
            [Context]:
            {context_str}
            
            Your Objective: {role_desc}.
            Keep it concise (under 200 words). Focus on technical feasibility and risks.
            """
            
            loop = asyncio.get_event_loop()
            response_text = await loop.run_in_executor(None, self.backend.generate, "gemini-2.0-flash", [{"role": "user", "content": prompt}])
            
            entry = {"role": p_name, "content": response_text, "round": round_idx}
            responses.append(entry)
            history.append(entry)
            
        return responses

    def synthesize_consensus(self, topic: str, history: List[Dict[str, str]], is_debug: bool = False) -> Dict[str, Any]:
        """토론 히스토리를 종합하여 최종 합의(Consensus) 도출"""
        context_str = "\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in history])
        
        role_title = "Debate Moderator" if not is_debug else "Chief System Surgeon"
        format_hint = "JSON format"
        
        prompt = f"""You are the {role_title}.
        Synthesize the following debate into a final consensus decision.
        If this is a Knowledge Conflict Resolution, you MUST provide a 'unified_rule' structure.
        
        [Topic/Error]: {topic}
        [Debate History]:
        {context_str}
        
        Output strictly in {format_hint}:
        {{
            "final_decision": "Selected approach or compromise",
            "rationale": "Key reasons for this decision",
            "unified_rule": {{
                "instruction": "The single authoritative instruction",
                "trigger_patterns": ["pattern1", "pattern2"],
                "severity": 1-5,
                "category": "coding/research/general"
            }},
            "tradeoffs": [
                {{ "aspect": "performance/safety/etc", "gain": "...", "loss": "..." }}
            ],
            "action_plan": ["Step 1", "Step 2"]
        }}
        """
        
        config = {}
        # Structured output hint for LLM
        config["response_mime_type"] = "application/json"

        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], config)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            # [Debate Memory Integration] 합의안을 Super Rule로 승격하여 저장
            if "unified_rule" in data and data["unified_rule"]:
                try:
                    memory = EvolutionaryMemory()
                    rule = data["unified_rule"]
                    # 필수 필드 존재 여부 확인 후 저장
                    if rule.get("instruction") and rule.get("trigger_patterns"):
                        memory.save_rule(
                            instruction=rule["instruction"],
                            trigger_patterns=rule["trigger_patterns"],
                            category=rule.get("category"),
                            severity=rule.get("severity", 3),
                            source_session="swarm_debate",
                            is_super_rule=True
                        )
                        logger.info(f"🚀 Swarm consensus saved as Super Rule: {rule['instruction'][:50]}...")
                except Exception as mem_e:
                    logger.error(f"Failed to save consensus as Super Rule: {mem_e}")
            
            os.makedirs("logs/debates", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "debug_" if is_debug else "consensus_"
            with open(f"logs/debates/{prefix}{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump({"topic": topic, "history": history, "consensus": data}, f, indent=2, ensure_ascii=False)
                
            return data
        except Exception as e:
            logger.error(f"Consensus synthesis failed: {e}")
            return {"final_decision": "Failed to synthesize", "rationale": str(e), "action_plan": []}

    async def run_debate(self, topic: str, state: GortexState, rounds: int = 2, is_debug: bool = False) -> Dict[str, Any]:
        """토론 전체 프로세스 실행 (Dynamic Recruitment 포함)"""
        history = []
        mode_icon = "⚔️" if not is_debug else "🩺"
        
        # 1. 전문가 모집
        required_skills = ["Analysis", "Coding"] # 기본값
        if is_debug: required_skills = ["Analysis", "Coding", "General"] # Security 대신 General로 테스트
        
        # 키워드 기반 필요 스킬 추론 (간이 로직)
        if "security" in topic.lower() or "hack" in topic.lower(): required_skills.append("Security") # Security 카테고리는 Economy에 추가 필요
        if "design" in topic.lower() or "architecture" in topic.lower(): required_skills.append("Design")
        
        logger.info(f"{mode_icon} Starting debate on: {topic}")
        self.recruit_experts(state, required_skills)
        
        for r in range(1, rounds + 1):
            logger.info(f"--- Round {r} ---")
            await self.conduct_dynamic_round(topic, r, history, is_debug=is_debug)
            
        logger.info("⚖️ Synthesizing consensus...")
        consensus = self.synthesize_consensus(topic, history, is_debug=is_debug)
        return consensus

async def swarm_node_async(state: GortexState) -> Dict[str, Any]:
    """Swarm Node Entry Point (Async)"""
    # 1. 디버그 모드 판별 (에러 발생 상황인지 확인)
    last_msg = str(state["messages"][-1][1] if isinstance(state["messages"][-1], tuple) else state["messages"][-1].content)
    is_debug = "❌" in last_msg or "error" in last_msg.lower() or state.get("next_node") == "swarm_debug"
    
    topic = state.get("current_issue") or last_msg
    
    # 2. Swarm Agent 인스턴스화
    agent = SwarmAgent()
    
    # 3. 토론 실행 (State 전달)
    consensus = await agent.run_debate(topic, state, rounds=2, is_debug=is_debug)
    
    # 4. 결과 메시지 포맷팅
    title = "⚖️ **Consensus Reached**" if not is_debug else "🩺 **Joint Diagnosis & Fix Plan Established**"
    msg = f"{title}\n\n**Decision**: {consensus.get('final_decision')}\n**Rationale**: {consensus.get('rationale')}\n"
    if consensus.get("action_plan"):
        msg += "**Action Plan**:\n" + "\n".join([f"- {step}" for step in consensus["action_plan"]])

    # UI에 보여줄 참가자 정보
    participants_info = ", ".join([f"{p['name']} ({p['role']})" for p in agent.participants])
    msg += f"\n\n*(Participants: {participants_info})*"

    return {
        "messages": [("ai", msg)],
        "next_node": "manager", 
        "debate_result": consensus,
        "is_debug_mode": is_debug
    }

def swarm_node(state: GortexState) -> Dict[str, Any]:
    """Sync wrapper for graph compatibility"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(swarm_node_async(state)))
            return future.result()
    else:
        return loop.run_until_complete(swarm_node_async(state))