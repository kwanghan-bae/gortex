import json
import asyncio
import logging
from datetime import datetime
from gortex.utils.token_counter import count_tokens, estimate_cost
from gortex.utils.vocal_bridge import VocalBridge
from gortex.utils.notifier import Notifier
from gortex.core.config import GortexConfig
from gortex.agents.analyst import AnalystAgent
from gortex.ui.three_js_bridge import ThreeJsBridge
from gortex.utils.healing_memory import SelfHealingMemory

logger = logging.getLogger("GortexEngine")

class GortexEngine:
    """에이전트 실행 루프와 시스템 상태 조율 (유실 로직 전수 복구 버전)"""
    def __init__(self, ui, observer, vocal: VocalBridge):
        self.ui = ui
        self.observer = observer
        self.vocal = vocal
        self.notifier = Notifier()
        self.bridge_3d = ThreeJsBridge()
        self.healer = SelfHealingMemory()

    async def process_node_output(self, node_name: str, output: dict, state_vars: dict):
        """노드 출력을 처리하고 시스템 상태(state_vars)를 실시간 업데이트 및 인과 관계 기록"""
        node_tokens = 0
        
        # 1. 인과 관계 기록
        state_vars["last_event_id"] = self.observer.log_event(
            node_name, 
            "node_complete", 
            {"goal": output.get("goal", "Processing")},
            cause_id=state_vars.get("last_event_id")
        )

        # 2. 메시지 처리
        if "messages" in output:
            for msg in output["messages"]:
                role, content = (msg[0], msg[1]) if isinstance(msg, tuple) else (msg.type, msg.content)
                self.ui.chat_history.append((role, content))
                
                # [VOICE/SECURITY/ACHIEVEMENT] 복구
                if role == "ai":
                    if GortexConfig().get("voice_enabled") and len(str(content)) < 500:
                        self.vocal.text_to_speech(str(content))
                        self.vocal.play_audio("logs/response.mp3")
                    
                    if "모든 계획된 작업을 완료했습니다" in str(content):
                        self.ui.add_achievement("Goal Reached", icon="✅")
                    
                    if "❌ Security Alert" in str(content):
                        self.ui.add_security_event("Forbidden Command", str(content))
                        self.notifier.send_notification(str(content), title="🚨 Security Violation")

                if isinstance(content, str):
                    node_tokens += count_tokens(content)

        # 3. [ADAPTIVE UI] 레이아웃 모드 전환
        if "ui_mode" in output:
            self.ui.set_layout_mode(output["ui_mode"])

        # 4. [ECONOMY] 에이전트 평판 및 크레딧 업데이트 (유실 복구)
        if "agent_economy" in output:
            if "agent_economy" not in state_vars: state_vars["agent_economy"] = {}
            state_vars["agent_economy"].update(output["agent_economy"])
        if "token_credits" in output:
            if "token_credits" not in state_vars: state_vars["token_credits"] = {}
            state_vars["token_credits"].update(output["token_credits"])

        # 5. [SELF-HEALING] 에러 발생 시 즉각적인 힌트 검색 (유실 복구)
        if node_name == "coder" and output.get("status") == "failed":
            hint = self.healer.get_solution_hint("Error in tool execution")
            if hint:
                self.ui.chat_history.append(("system", f"💡 **HINT**: {hint}"))

        # 6. 상태 동기화
        state_vars["agent_energy"] = output.get("agent_energy", state_vars.get("agent_energy", 100))
        state_vars["last_efficiency"] = output.get("last_efficiency", state_vars.get("last_efficiency", 0.0))
        if "file_cache" in output:
            if "session_cache" not in state_vars: state_vars["session_cache"] = {}
            state_vars["session_cache"].update(output["file_cache"])

        # 7. [VISUAL STREAMING] 3D 데이터 실시간 전송
        if self.ui.web_manager:
            current_causal = self.observer.get_causal_graph()
            causal_3d = self.bridge_3d.convert_causal_graph_to_3d(current_causal)
            if output.get("impact_analysis"):
                causal_3d = self.bridge_3d.apply_impact_highlight(causal_3d, output["impact_analysis"])
            
            payload_causal = json.dumps({"type": "causal_graph_3d", "data": causal_3d})
            coro_causal = self.ui.web_manager.broadcast(payload_causal)
            if asyncio.iscoroutine(coro_causal):
                asyncio.create_task(coro_causal)

            if output.get("user_intent_projection"):
                intent_3d = self.bridge_3d.convert_intent_to_3d(output["user_intent_projection"])
                payload_intent = json.dumps({"type": "user_intent_3d", "data": intent_3d})
                coro_intent = self.ui.web_manager.broadcast(payload_intent)
                if asyncio.iscoroutine(coro_intent):
                    asyncio.create_task(coro_intent)

        return node_tokens