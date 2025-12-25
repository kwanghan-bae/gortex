import logging
import uuid
import json
from typing import Dict, Any, Optional
from gortex.core.graph import compile_gortex_graph
from gortex.core.state import GortexState
from gortex.utils.healing_memory import SelfHealingMemory
from gortex.utils.token_counter import count_tokens, DailyTokenTracker
from gortex.utils.resource_monitor import ResourceMonitor

logger = logging.getLogger("GortexEngine")

class GortexEngine:
    """
    Gortex 시스템의 핵심 실행 엔진.
    시스템 부하에 따라 리소스를 동적으로 스케일링하며 에이전트 그래프를 실행합니다.
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
        self.monitor = ResourceMonitor()
        self.max_concurrency = 2 # 기본 동시 실행 한도

    def update_scaling_policy(self):
        """시스템 부하에 따라 동시 실행 한도 스케일링"""
        old_limit = self.max_concurrency
        self.max_concurrency = self.monitor.estimate_concurrency_limit(base_limit=2)
        
        if old_limit != self.max_concurrency:
            logger.info(f"⚖️ Scaling Policy Updated: {old_limit} -> {self.max_concurrency} tasks concurrently.")
            if self.ui:
                self.ui.add_achievement(f"Scaling to {self.max_concurrency}x")

    async def run_self_defense_cycle(self):
        """자율적으로 취약 구역을 찾아 테스트를 생성하고 방어력을 높임."""
        from gortex.agents.analyst.base import AnalystAgent
        from gortex.agents.coder import CoderAgent
        import os
        
        analyst = AnalystAgent()
        coder = CoderAgent()
        
        logger.info("🛡️ Initiating Self-Defense Cycle...")
        
        # 1. 테스트 핫스팟 식별
        hotspots = analyst.identify_test_hotspots()
        if not hotspots:
            logger.info("✅ No urgent test hotspots found. System is well-defended.")
            return
            
        target = hotspots[0] # 가장 위험한 곳 우선
        logger.info(f"📍 Target hotspot identified: {target['file']} (Risk: {target['risk_score']})")
        
        # 2. 회귀 테스트 생성 및 검증
        res = coder.generate_regression_test(target["file"], risk_info=target["reason"])
        
        if res.get("status") == "success":
            logger.info(f"✅ Defenses strengthened: {res['file']}")
            if self.ui:
                self.ui.add_achievement(f"Defense Up: {os.path.basename(res['file'])}")
        else:
            logger.error(f"❌ Defense generation failed for {target['file']}: {res.get('error') or res.get('reason')}")

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
        
        # 인과 관계 및 관찰자 기록
        event_id = str(uuid.uuid4())
        if self.observer:
            cause_id = state.get("last_event_id")
            res_id = self.observer.log_event(
                agent=node_name, 
                event="node_complete", 
                payload=output, 
                cause_id=cause_id
            )
            state["last_event_id"] = res_id or event_id
        
        # UI 업데이트
        if self.ui:
            self.ui.update_thought(output.get("thought", ""), agent_name=node_name)
            if "ui_mode" in output:
                self.ui.set_layout_mode(output["ui_mode"])
            
            msg_str = str(output.get("messages", ""))
            if "완료했습니다" in msg_str:
                self.ui.add_achievement("Goal Reached")
            
            if "❌" in msg_str or "security alert" in msg_str.lower():
                self.ui.add_security_event("High", "Security issue detected")
            
            if "agent_economy" in state or "agent_economy" in output:
                eco_data = output.get("agent_economy") or state.get("agent_economy")
                if eco_data:
                    self.ui.update_economy_panel(eco_data)
        
        # 음성 브릿지
        if self.vocal and output.get("messages"):
            last_msg = str(output["messages"][-1][1] if isinstance(output["messages"][-1], tuple) else output["messages"][-1])
            self.vocal.text_to_speech(last_msg)
            self.vocal.play_audio()
            
        # 자가 치유
        if output.get("status") == "failed":
            hint = self.healer.get_solution_hint("Error detected in node output")
            if hint:
                logger.info(f"🩹 Healing hint found: {hint}")

        state.update(output)
        return tokens

    def run(self, user_input: str, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """사용자 입력을 바탕으로 에이전트 루프 실행"""
        # 실행 전 스케일링 정책 갱신
        self.update_scaling_policy()
        
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
            "agent_economy": {},
            "risk_score": 0.5
        }
        
        energy = state.get("agent_energy", 100)
        if energy < 10:
            return {
                "messages": [("ai", "🔋 **시스템 에너지 고갈**: 유지보수 모드입니다.")],
                "next_node": "__end__"
            }
        
        try:
            final_state = self.graph.invoke(state, self.config)
            return final_state
        except Exception as e:
            logger.error(f"Engine execution failed: {e}")
            return {"error": str(e), "next_node": "__end__"}

    async def run_async(self, user_input: str, initial_state: Optional[Dict[str, Any]] = None):
        return self.run(user_input, initial_state)
