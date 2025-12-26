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
        self.thread_id = thread_id or str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}
        
        # 1. 초기 그래프 컴파일
        self.graph = compile_gortex_graph()
        
        self.healer = SelfHealingMemory()
        self.tracker = DailyTokenTracker()
        self.monitor = ResourceMonitor()
        self.max_concurrency = 2 

    def refresh_graph(self):
        """런타임에 에이전트 그래프를 재컴파일함 (Zero-Downtime Evolution)"""
        logger.info("🧠 Hot-swapping neural architecture: Re-compiling graph...")
        try:
            # 새로운 에이전트 레지스트리 상태를 반영하여 그래프 재구축
            self.graph = compile_gortex_graph()
            if self.ui:
                self.ui.add_achievement("Neural Map Updated")
            logger.info("✅ Graph successfully re-compiled and swapped.")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh graph: {e}")
            return False

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
        """에이전트 평판, 지갑 잔고, 작업 위험도를 고려하여 최적 모델 선택"""
        risk = state.get("risk_score", 0.5)
        budget_status = self.tracker.get_budget_status()
        economy = state.get("agent_economy", {}).get(agent_name.lower(), {})
        
        points = economy.get("points", 0)
        credits = economy.get("credits", 0.0) # [NEW] 지불 능력 확인
        
        # 1. 예산 고갈 상태 (시스템 전체)
        if budget_status > 0.9:
            return "ollama/llama3"
            
        # 2. [ECONOMY] 지불 능력 기반 필터링
        # Gemini Pro는 최소 $1.0의 잔고가 있어야 시도 가능
        can_afford_pro = credits >= 1.0
        # Gemini Flash는 최소 $0.1의 잔고 필요
        can_afford_flash = credits >= 0.1

        # 3. 모델 할당 로직
        if risk > 0.8 and points > 1000 and can_afford_pro:
            return "gemini-1.5-pro"
            
        if (points > 500 or risk > 0.4) and can_afford_flash:
            return "gemini-2.0-flash"
            
        # 4. 잔고 부족 시 강제 다운그레이드
        if not can_afford_flash:
            logger.info(f"💸 Agent {agent_name} is under-funded (${credits:.4f}). Downgrading to Ollama.")
            
        return "ollama/llama3"

    async def process_node_output(self, node_name: str, output: Dict[str, Any], state: Dict[str, Any], latency_ms: Optional[int] = None):
        """노드 실행 결과를 처리하고 실시간 경제 정산 및 UI 업데이트 수행"""
        # 1. 토큰 추적 및 비용 계산
        tokens = count_tokens(json.dumps(output))
        model = state.get("assigned_model", "flash")
        self.tracker.update_usage(tokens, model)
        
        from gortex.utils.token_counter import estimate_cost
        cost = estimate_cost(tokens, model)
        
        # 2. [ECONOMIC SOWEREIGNTY] 자동 결제 (Auto-Billing)
        from gortex.utils.economy import get_economy_manager
        eco_manager = get_economy_manager()
        
        # 사용료 차감
        eco_manager.deduct_credits(state, node_name, cost)
        
        # 성공 시 상금 지급 (비용의 1.5배 보너스 또는 고정 수익)
        if output.get("status") == "success" or "❌" not in str(output.get("messages", "")):
            reward = cost * 1.2 + 0.001 # 최소 수익 보장
            eco_manager.add_credits(state, node_name, reward)
            logger.info(f"💰 Agent '{node_name}' earned ${reward:.6f} (ROI: +20%)")

        # 3. 인과 관계 및 관찰자 기록 (기존 로직)
        event_id = str(uuid.uuid4())
        if self.observer:
            cause_id = state.get("last_event_id")
            res_id = self.observer.log_event(
                agent=node_name, 
                event="node_complete", 
                payload=output, 
                latency_ms=latency_ms,
                cause_id=cause_id
            )
            state["last_event_id"] = res_id or event_id
        
        # UI 업데이트
        if self.ui:
            self.ui.update_thought(output.get("thought", ""), agent_name=node_name)
            if "ui_mode" in output:
                self.ui.set_mode(output["ui_mode"])
            
            # [NEW] AI 메시지를 UI 채팅 기록에 반영 (필터링 강화)
            if "messages" in output:
                for msg in output["messages"]:
                    if isinstance(msg, (list, tuple)) and msg[0] == "ai":
                        content = str(msg[1])
                        # 내부 기술적 에러나 단순 완료 알림은 메인 채팅에서 제외
                        internal_keywords = ["Planning Error", "분석 오류", "All steps completed", "완료했습니다"]
                        if not any(k in content for k in internal_keywords):
                            self.ui.chat_history.append(msg)
                        else:
                            # 내부 상태는 로그로 기록
                            self.ui.update_logs({"agent": node_name, "event": content})
            
            msg_str = str(output.get("messages", ""))
            if "완료했습니다" in msg_str:
                self.ui.add_achievement("Goal Reached")
            
            if "❌" in msg_str or "security alert" in msg_str.lower():
                self.ui.add_security_event("High", "Security issue detected")
            
            if "agent_economy" in state or "agent_economy" in output:
                eco_data = output.get("agent_economy") or state.get("agent_economy")
                if eco_data:
                    self.ui.update_economy_panel(eco_data)
        
        # 음성 브릿지 (v9.0 에이전트 고유 보이스 연동)
        if self.vocal and output.get("messages"):
            for m in output["messages"]:
                if isinstance(m, (list, tuple)) and m[0] == "ai":
                    last_msg = str(m[1])
                    if self.vocal.text_to_speech(last_msg, agent_name=node_name):
                        self.vocal.play_audio("logs/response.mp3")
            
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
