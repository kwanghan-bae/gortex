import asyncio
import logging
import time
import os
import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from gortex.core.state import GortexState
from gortex.agents.analyst import AnalystAgent
from gortex.core.llm.factory import LLMFactory
from gortex.utils.prompt_loader import PromptLoader

logger = logging.getLogger("GortexSwarm")

class SwarmAgent:
    """
    다중 에이전트 협업 및 토론(Debate)을 관장하는 Swarm Intelligence 모듈.
    상반된 페르소나(Innovation vs Stability) 간의 라운드 기반 토론을 수행하고 합의를 도출합니다.
    """
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()
        self.prompts = PromptLoader()

    async def conduct_debate_round(self, topic: str, round_idx: int, history: List[Dict[str, str]], is_debug: bool = False) -> List[Dict[str, str]]:
        """단일 토론 라운드 실행 (Innovation -> Stability 순서)"""
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
        
        [Topic/Error]: {topic}
        [Debate History]:
        {context_str}
        
        Output strictly in {format_hint}:
        {{
            "final_decision": "Selected approach or compromise",
            "rationale": "Key reasons for this decision",
            "tradeoffs": [
                {{ "aspect": "performance/safety/etc", "gain": "...", "loss": "..." }}
            ],
            "residual_risk": "Remaining risks",
            "action_plan": ["Step 1", "Step 2"]
        }}
        """
        
        config = {}
        if self.backend.supports_structured_output():
            from google.genai import types
            config = types.GenerateContentConfig(response_mime_type="application/json")

        try:
            response_text = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}], config)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            os.makedirs("logs/debates", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "debug_" if is_debug else "consensus_"
            with open(f"logs/debates/{prefix}{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump({"topic": topic, "history": history, "consensus": data}, f, indent=2, ensure_ascii=False)
                
            return data
        except Exception as e:
            logger.error(f"Consensus synthesis failed: {e}")
            return {"final_decision": "Failed to synthesize", "rationale": str(e), "action_plan": []}

    async def run_debate(self, topic: str, rounds: int = 2, is_debug: bool = False) -> Dict[str, Any]:
        """토론 전체 프로세스 실행"""
        history = []
        mode_icon = "⚔️" if not is_debug else "🩺"
        logger.info(f"{mode_icon} Starting debate on: {topic}")
        
        for r in range(1, rounds + 1):
            logger.info(f"--- Round {r} ---")
            await self.conduct_debate_round(topic, r, history, is_debug=is_debug)
            
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
    
    # 3. 토론 실행 (디버그 시에는 고도로 집중된 2라운드 토론)
    consensus = await agent.run_debate(topic, rounds=2, is_debug=is_debug)
    
    # 4. 결과 메시지 포맷팅
    title = "⚖️ **Consensus Reached**" if not is_debug else "🩺 **Joint Diagnosis & Fix Plan Established**"
    msg = f"{title}\n\n**Decision**: {consensus.get('final_decision')}\n**Rationale**: {consensus.get('rationale')}\n"
    if consensus.get("action_plan"):
        msg += "**Action Plan**:\n" + "\n".join([f"- {step}" for step in consensus["action_plan"]])

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
