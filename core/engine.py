import logging
import uuid
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from gortex.core.graph import compile_gortex_graph
from gortex.core.state import GortexState
from gortex.core.config import GortexConfig
from gortex.utils.tools import execute_shell
from gortex.utils.token_counter import count_tokens
from gortex.utils.notifier import Notifier
from gortex.utils.healing_memory import SelfHealingMemory
from gortex.utils.token_counter import count_tokens, DailyTokenTracker

logger = logging.getLogger("GortexEngine")

class GortexEngine:
    """
    Gortex 시스템의 핵심 실행 엔진.
    에이전트 그래프를 실행하고 상태를 관리합니다.
    """
    def __init__(self, ui=None, observer=None, vocal_bridge=None, thread_id: str = None):
        self.ui = ui
        self.observer = observer
        self.vocal = vocal_bridge
        self.graph = compile_gortex_graph()
        self.thread_id = thread_id or str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}
        self.healer = SelfHealingMemory()
        self.tracker = DailyTokenTracker()

    def select_optimal_model(self, state: GortexState, agent_name: str) -> str:
        """에이전트 평판, 작업 위험도, 일일 예산을 고려하여 최적 모델 선택"""
        risk = state.get("risk_score", 0.5)
        budget_status = self.tracker.get_budget_status()
        economy = state.get("agent_economy", {}).get(agent_name, {})
        points = economy.get("points", 0)
        
        # 1. 예산 고갈 상태 (80% 이상 소모) -> 강제 Ollama 다운그레이드
        if budget_status > 0.8:
            logger.warning(f"🔋 Budget critical ({budget_status:.1%}). Downgrading to Ollama.")
            return "ollama/llama3"
            
        # 2. 고위험/에픽 작업 + 엘리트 에이전트 -> Gemini Pro
        if risk > 0.8 and points > 1000:
            return "gemini-1.5-pro"
            
        # 3. 일반 전문 작업 -> Gemini Flash
        if points > 500 or risk > 0.4:
            return "gemini-2.0-flash"
            
        # 4. 단순 반복 작업/저평판 에이전트 -> Ollama
        return "ollama/llama3"

    async def process_node_output(self, node_name: str, output: Dict[str, Any], state: Dict[str, Any]):
        """노드 실행 결과를 처리하고 UI/관찰자에게 알림"""
        # 토큰 추적 업데이트
        tokens = count_tokens(json.dumps(output))
        model = state.get("assigned_model", "flash")
        self.tracker.update_usage(tokens, model)


        
        # 2. 인과 관계 및 관찰자 기록
        event_id = str(uuid.uuid4())
        if self.observer:
            # state["last_event_id"]를 cause_id로 사용
            cause_id = state.get("last_event_id")
            res_id = self.observer.log_event(
                agent=node_name, 
                event="node_complete", 
                payload=output, 
                cause_id=cause_id
            )
            # 결과 ID를 다시 last_event_id에 저장 (연쇄)
            state["last_event_id"] = res_id or event_id
        
        # 3. UI 업데이트 및 성과 기록
        if self.ui:
            self.ui.update_thought(output.get("thought", ""), agent_name=node_name)
            
            if "ui_mode" in output:
                self.ui.set_layout_mode(output["ui_mode"])
            
            # 성과 기록 조건: 메시지에 "완료했습니다" 포함 시
            msg_str = str(output.get("messages", ""))
            if "완료했습니다" in msg_str:
                self.ui.add_achievement("Goal Reached")
            
            # 보안 경고
            if "❌" in msg_str or "security alert" in msg_str.lower():
                self.ui.add_security_event("High", "Security issue detected")
            
            # [ECONOMY] 경제 상태 실시간 업데이트
            if "agent_economy" in state or "agent_economy" in output:
                eco_data = output.get("agent_economy") or state.get("agent_economy")
                if eco_data:
                    self.ui.update_economy_panel(eco_data)
        
        # 4. 음성 브릿지 연동
        if self.vocal and output.get("messages"):
            last_msg = str(output["messages"][-1][1] if isinstance(output["messages"][-1], tuple) else output["messages"][-1])
            self.vocal.text_to_speech(last_msg)
            self.vocal.play_audio()
            
        # 5. 자가 치유 (Healer)
        if output.get("status") == "failed":
            hint = self.healer.get_solution_hint("Error detected in node output")
            if hint:
                logger.info(f"🩹 Healing hint found: {hint}")

        # 6. 상태 변수 병합 및 캐시 관리
        if "file_cache" in output:
            if "session_cache" not in state: state["session_cache"] = {}
            state["session_cache"].update(output["file_cache"])
            
        state.update(output)
        return tokens

    def run(self, user_input: str, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """사용자 입력을 바탕으로 에이전트 루프 실행"""
        state = initial_state or {
            "messages": [("user", user_input)],
            "pinned_messages": [],
            "plan": [],
            "current_step": 0,
            "working_dir": ".",
            "file_cache": {},
            "agent_energy": 100,
            "api_call_count": 0,
            "token_credits": {},
            "agent_economy": {}
        }
        
        # [MAINTENANCE] 에너지 고갈 체크
        energy = state.get("agent_energy", 100)
        if energy < 10:
            logger.warning(f"🔋 Energy critical ({energy}%). Entering Maintenance Mode.")
            return {
                "messages": [("ai", "🔋 **시스템 에너지 고갈**: 현재 유지보수 모드입니다. 에너지가 충전될 때까지 잠시만 기다려주세요 (최소 20% 필요).")],
                "next_node": "__end__"
            }
        
        try:
            final_state = self.graph.invoke(state, self.config)
            return final_state
        except Exception as e:
            logger.error(f"Engine execution failed: {e}")
            return {"error": str(e), "next_node": "__end__"}

    async def run_async(self, user_input: str, initial_state: Optional[Dict[str, Any]] = None):
        """비동기 실행 지원"""
        return self.run(user_input, initial_state)