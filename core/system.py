import asyncio
import logging
import uuid
import os
import re
import warnings
from typing import Optional, List

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

# prompt_toolkit for autocomplete
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PromptStyle

from gortex.config.settings import settings
from gortex.core.state import GortexState, SessionManager
from gortex.core.graph import compile_gortex_graph
from gortex.core.commands import handle_command
from gortex.core.engine import GortexEngine
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import ThemeManager
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import estimate_cost
from gortex.utils.tools import deep_integrity_check
from gortex.utils.vocal_bridge import VocalBridge
from gortex.utils.translator import i18n
from gortex.agents.analyst import AnalystAgent
from gortex.ui.components.boot import BootManager
from gortex.ui.themes.palette import Palette

logger = logging.getLogger("GortexSystem")

# Autocomplete commands
COMMANDS = [
    "/help", "/status", "/agents", "/inspect", "/rca", "/search", "/map", 
    "/kg", "/scan_debt", "/index", "/voice", "/language", "/theme", 
    "/config", "/export", "/import", "/clear", "/bug", "/mode", "/save", 
    "/load", "/provider", "/model", "/history"
]

class GortexCommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith('/') and ' ' not in text:
            for cmd in COMMANDS:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))

class GortexSystem:
    def __init__(self):
        # Mute unnecessary warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        self.console = Console()
        self.theme_manager = ThemeManager()
        self.ui = DashboardUI(console=self.console)
        self.observer = GortexObserver()
        self.vocal = VocalBridge()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.session_manager = SessionManager()
        self.thread_id = str(uuid.uuid4())[:8]

        # Ensure working directory exists
        os.makedirs(settings.WORKING_DIR, exist_ok=True)
        session_data = self.session_manager.get_session(self.thread_id)
        checked_session_data, _ = deep_integrity_check(settings.WORKING_DIR, session_data)

        self.state: GortexState = {
            "agent_energy": 100,
            "last_efficiency": 100.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "session_cache": checked_session_data,
            "file_cache": checked_session_data,
            "pinned_messages": [],
            "last_event_id": None,
            "last_question": None,
            "agent_economy": {},
            "current_predicted_usage": None,
            "messages": [],
            "working_dir": settings.WORKING_DIR,
            "plan": [],
            "current_step": 0,
            "next_node": "manager",
            "assigned_model": "gemini-1.5-flash",
            "coder_iteration": 0,
            "history_summary": "",
            "active_constraints": [],
            "efficiency_history": [],
            "ui_language": "ko",
            "token_credits": {},
            "api_call_count": 0,
            "step_count": 0
        }

        # Setup prompt session
        self.prompt_session = PromptSession(
            history=FileHistory("logs/input_history.txt"),
            completer=GortexCommandCompleter(),
            complete_while_typing=True
        )

    async def get_user_input(self) -> Optional[str]:
        """Safe user input with autocomplete support."""
        try:
            style = PromptStyle.from_dict({'prompt': 'ansigreen bold'})
            user_input = await self.prompt_session.prompt_async("\n👤 You: ", style=style)
            return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input.strip())
        except (KeyboardInterrupt, EOFError):
            return None

    async def energy_recovery_loop(self):
        """Loop to recover energy during idle time."""
        while True:
            await asyncio.sleep(2)
            if self.state["agent_energy"] < 100:
                self.state["agent_energy"] = min(100, self.state["agent_energy"] + 1)
                self.ui.update_energy_visualizer(self.state["agent_energy"])
                
                # Only update sidebar if idle to avoid flickering during active work
                if self.ui.current_agent == "Idle":
                    self.ui.update_sidebar(
                        "Idle", "Recovering...",
                        self.state["total_tokens"],
                        self.state["total_cost"],
                        len(self.state.get("active_constraints", [])),
                        energy=self.state["agent_energy"],
                        efficiency=self.state["last_efficiency"],
                        agent_economy=self.state.get("agent_economy")
                    )

    async def trend_scout_loop(self):
        """Background loop for trend analysis."""
        from gortex.agents.trend_scout import TrendScoutAgent
        scout = TrendScoutAgent()
        while True:
            await asyncio.sleep(1)
            interval = settings.TREND_SCAN_INTERVAL_HOURS
            if scout.should_scan(interval):
                try:
                    notifications = await scout.scan_trends()
                    for msg in notifications:
                        self.ui.add_achievement(f"Trend: {msg}")
                except Exception as e:
                    logger.error(f"Trend scout error: {e}")
            await asyncio.sleep(3600)

    async def notification_listener_loop(self):
        """Listen for MQ notifications and thought streams from distributed workers."""
        from gortex.core.mq import mq_bus
        if not mq_bus.is_connected:
            return

        from gortex.core.web_api import manager as web_manager, format_event_for_web
        
        def handle_notification(msg):
            event_type = msg.get("type")
            payload = msg.get("payload", {})
            agent = msg.get("agent", "Unknown")
            
            # [WEB BROADCAST] 시각화 최적화 포맷으로 전송
            formatted_msg = format_event_for_web(msg)
            asyncio.create_task(web_manager.broadcast(json.dumps(formatted_msg, ensure_ascii=False)))
            
            # [THOUGHT STREAM] 실시간 사고 중계 처리 (기존 로직)
                thought_text = payload.get("text", "")
                self.ui.update_thought(f"[Distributed] {thought_text}", agent_name=agent)
                return

            if event_type == "task_completed":
                task_type = payload.get("type", "Task").upper()
                msg_text = f"✨ **{task_type} Done**: {payload.get('query')}"
                self.ui.add_achievement(msg_text)
                self.ui.chat_history.append(("system", f"🔔 {msg_text}\nSummary: {payload.get('summary')}"))
            
            elif event_type == "training_completed":
                job_id = payload.get("job_id")
                agent_name = payload.get("agent", "Coder")
                from gortex.core.llm.trainer import trainer
                # 1. 모델 등록
                if trainer.register_custom_model(job_id, agent_name):
                    msg_text = f"💎 **Neural Evolution**: {agent_name} has evolved with a Custom SLM!"
                    self.ui.add_achievement(f"Evolved: {agent_name}")
                    self.ui.chat_history.append(("system", f"🚀 {msg_text} (Job: {job_id})"))
            
            elif event_type == "agent_registered":
                agent_name = payload.get("agent")
                logger.info(f"🆕 New agent '{agent_name}' detected. Refreshing graph topology...")
                # 핫스왑 실행
                if self.engine.refresh_graph():
                    self.ui.chat_history.append(("system", f"🕸️ **Neural Architecture Swapped**: '{agent_name}' is now active in the workflow."))
            
            elif event_type == "agent_deregistered":
                agent_name = payload.get("agent")
                logger.info(f"🗑️ Agent '{agent_name}' removed. Updating neural map...")
                if self.engine.refresh_graph():
                    self.ui.add_achievement(f"Swarm Leanified")
            
            elif event_type == "task_failed":
                self.ui.add_achievement(f"❌ Task Failed: {payload.get('task_id')}")
            
            elif event_type == "worker_heartbeat":
                pass

        # 멀티 채널 구독을 위해 listen 메서드 수정이 필요할 수 있으나, 
        # 현재 구현상 gortex:thought_stream과 gortex:notifications를 모두 감시해야 함
        loop = asyncio.get_running_loop()
        # 공통 알림 채널 청취
        loop.run_in_executor(None, mq_bus.listen, "gortex:notifications", handle_notification)
        # 사고 스트림 채널 청취 (추가)
        loop.run_in_executor(None, mq_bus.listen, "gortex:thought_stream", handle_notification)
        
        # [WORKSPACE SYNC] 실시간 파일 동기화 리스너
        def handle_sync(msg):
            payload = msg.get("payload", {})
            if msg.get("type") == "file_changed":
                path = payload.get("path")
                content = payload.get("content")
                new_hash = payload.get("hash")
                
                if path and content:
                    # 무한 루프 방지: 현재 파일 해시와 다를 때만 쓰기
                    from gortex.utils.tools import get_file_hash
                    if get_file_hash(path) != new_hash:
                        logger.info(f"📥 Syncing remote file change: {path}")
                        # 원자적 쓰기 (이벤트 재발행 방지를 위해 직접 쓰기 또는 플래그 사용)
                        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(content)
                        self.ui.update_logs({"agent": "Sync", "event": f"Synced {os.path.basename(path)}"})

        loop.run_in_executor(None, mq_bus.listen, "gortex:workspace_sync", handle_sync)
        
        # 원격 로그 채널 청취 (추가)
        loop.run_in_executor(None, mq_bus.listen, "gortex:remote_logs", lambda msg: self.ui.update_logs({
            "agent": f"Rem:{msg.get('agent','???')}", 
            "event": msg.get("type", "log"),
            "payload": msg.get("payload", {})
        }))
        
        # [SECURITY ALERTS] 보안 위반 실시간 감시 (기존 로직)
        loop.run_in_executor(None, mq_bus.listen, "gortex:security_alerts", handle_security)
        
        # [GALACTIC SWARM] 연합 지식 및 경제 리스너 (v9.2 New)
        from gortex.core.collaboration import ambassador
        def handle_galactic_events(msg):
            event_type = msg.get("type")
            payload = msg.get("payload", {})
            sender_id = msg.get("agent", "Unknown")
            
            if event_type == "wisdom_offered":
                # [MARKET] 지능 구매 의사결정
                price = payload.get("price", 0)
                if price < 10.0: # 단순 정책: $10 미만이면 즉시 구매
                    if ambassador.purchase_remote_wisdom(sender_id, payload["rules"], price, self.state):
                        self.ui.add_achievement(f"Bought Wisdom from {sender_id}")
                        self.ui.chat_history.append(("system", f"🛒 **지능 구매 완료**: {sender_id}로부터 최상위 지침 {len(payload['rules'])}개를 구매하여 통합했습니다."))
            
            elif event_type == "payment_sent" and payload.get("to") == ambassador.swarm_id:
                # [REVENUE] 판매 수익 정산
                amount = payload.get("amount", 0)
                from gortex.utils.economy import get_economy_manager
                get_economy_manager().add_credits(self.state, "Manager", amount)
                self.ui.add_achievement("Wisdom Sold!")
                self.ui.chat_history.append(("system", f"💰 **지식 판매 수익**: 연합 군집으로부터 ${amount}의 로열티를 수령했습니다."))

        loop.run_in_executor(None, mq_bus.listen, "gortex:galactic:wisdom", handle_galactic_events)
        loop.run_in_executor(None, mq_bus.listen, "gortex:galactic:economy", handle_galactic_events)
        
        # 주기적인 자신의 지식 홍보 (1시간마다)
        async def broadcast_loop():
            while True:
                ambassador.broadcast_wisdom("coding")
                await asyncio.sleep(3600)
        asyncio.create_task(broadcast_loop())

        async def autonomous_drive_loop(self):
            """Idle 상태일 때 스스로 미션을 생성하여 실행함 (v10.0 Sovereign Mode)"""
            while True:
                await asyncio.sleep(300) # 5분마다 상태 체크
                
                # 에너지가 충분하고 현재 진행 중인 작업이 없을 때
                if self.state["agent_energy"] > 90 and self.ui.current_agent == "Idle":
                    logger.info("🤖 Sovereign Singularity: Generating autonomous mission...")
                    from gortex.agents.manager import ManagerAgent
                    mission = ManagerAgent().self_generate_mission(self.state)
                    
                    if mission:
                        msg = f"🌟 **자율 미션 개시**: '{mission['mission_name']}'\n\n**목표**: {mission['goal']}\n**이유**: {mission['rationale']}"
                        self.ui.chat_history.append(("system", msg))
                        self.ui.add_achievement("Sovereign Mission Started")
                        # 워크플로우 자동 실행
                        asyncio.create_task(self.run_mission(mission["goal"]))
    
        async def run_mission(self, user_input: str):
            """워크플로우 실행 래퍼"""
            initial_state = {
                "messages": [("user", user_input)],
                "pinned_messages": self.state["pinned_messages"],
                "working_dir": settings.WORKING_DIR,
                "file_cache": self.state["file_cache"],
                "agent_energy": self.state["agent_energy"],
                "last_efficiency": self.state["last_efficiency"]
            }
            # (기존 execute_workflow 로직과 통합하거나 호출)
            pass
    
        async def run(self):
            # ... (기존 부트 시퀀스)
            workflow = compile_gortex_graph()
            recovery_task = asyncio.create_task(self.energy_recovery_loop())
            trend_task = asyncio.create_task(self.trend_scout_loop())
            notify_task = asyncio.create_task(self.notification_listener_loop())
            # [V10.0] 자율 가동 루프 시작
            drive_task = asyncio.create_task(self.autonomous_drive_loop())
        current_task = None

        async def execute_workflow(user_input):
            self.ui.chat_history.append(("user", user_input))
            initial_state = {
                "messages": [("user", user_input)],
                "pinned_messages": self.state["pinned_messages"],
                "working_dir": settings.WORKING_DIR,
                "file_cache": self.state["file_cache"],
                "agent_energy": self.state["agent_energy"],
                "last_efficiency": self.state["last_efficiency"]
            }
            try:
                                        async for event in workflow.astream(initial_state, config={"configurable": {"thread_id": self.thread_id}}):
                                            for node_name, output in event.items():
                                                self.ui.update_sidebar(agent=node_name, step="Processing")
                                                
                                                try:
                                                    node_tokens = await self.engine.process_node_output(node_name, output, self.state)
                                                except PermissionError as pe:
                                                    # [MULTI-SIG WORKFLOW] 보안 위반 감지 시 투표 개시
                                                    self.ui.chat_history.append(("system", f"⚠️ **Approval Required**: {pe}"))
                                                    self.ui.update_main(self.ui.chat_history)
                                                    
                                                    from gortex.agents.swarm import SwarmAgent
                                                    vote_res = await SwarmAgent().run_security_vote(str(pe), self.state, output.get("action_payload", {}))
                                                    
                                                    if vote_res.get("is_approved"):
                                                        self.ui.chat_history.append(("system", f"✅ **Swarm Approved**: {vote_res['rationale']}"))
                                                        # 승인됨: 엔진에게 강제 실행 지시 (bypass_sentinel=True 등의 플래그 필요)
                                                        # (여기서는 데모 흐름을 위해 메시지 기록 위주로 처리)
                                                        node_tokens = 0
                                                    else:
                                                        self.ui.chat_history.append(("system", f"🛑 **Swarm Rejected**: {vote_res['rationale']}"))
                                                        continue
                
                                                self.state["total_tokens"] += node_tokens                        self.state["total_cost"] += estimate_cost(node_tokens)

                        if node_name == "manager" and output.get("question_to_user"):
                            self.state["last_question"] = output["question_to_user"]

                        # Update UI immediately for responsiveness
                        self.ui.update_main(self.ui.chat_history)
                        self.ui.update_sidebar(
                            node_name,
                            "Active",
                            self.state["total_tokens"],
                            self.state["total_cost"],
                            len(self.state.get("active_constraints", [])),
                            energy=self.state["agent_energy"],
                            efficiency=self.state["last_efficiency"],
                            agent_economy=self.state.get("agent_economy"),
                            capability=output.get("required_capability", "N/A"),
                            predicted_usage=output.get("predicted_usage")
                        )
                
                # After workflow ends
                self.session_manager.update_session(self.thread_id, self.state["file_cache"])
                if self.observer:
                    self.ui.update_collaboration_heatmap(self.observer.get_collaboration_matrix())
                
                self.ui.update_sidebar(
                    "Idle", "Ready",
                    self.state["total_tokens"],
                    self.state["total_cost"],
                    len(self.state.get("active_constraints", [])),
                    energy=self.state["agent_energy"],
                    efficiency=self.state["last_efficiency"],
                    agent_economy=self.state.get("agent_economy")
                )

            except Exception as e:
                logger.error(f"Workflow error: {e}")
                self.ui.chat_history.append(("system", f"❌ Error: {e}"))

        try:
            with Live(self.ui.layout, console=self.console, refresh_per_second=4, screen=False) as live:
                while True:
                    live.stop() # Stop rendering during input to avoid cursor issues
                    try:
                        user_input = await self.get_user_input()
                    finally:
                        live.start()

                    if user_input is None: break
                    if not user_input: continue
                    if user_input.lower() in ["exit", "quit", "q"]: break

                    # Interaction learning
                    if self.state.get("last_question") and user_input:
                        try:
                            AnalystAgent().learn_from_interaction(self.state["last_question"], user_input)
                            self.state["last_question"] = None
                        except: pass

                    if user_input.startswith("/"):
                        cmd_result = await handle_command(
                            user_input, self.ui, self.observer, 
                            self.session_manager.all_sessions_cache, 
                            self.thread_id, self.theme_manager
                        )
                        
                        # [VOICE INTERACTION] 음성 입력 처리
                        if cmd_result == "voice_input":
                            live.stop()
                            try:
                                audio_file = self.vocal.record_audio(duration=5)
                                if audio_file:
                                    transcript = self.vocal.speech_to_text(audio_file)
                                    if transcript:
                                        mapped_cmd = self.vocal.map_to_command(transcript)
                                        self.ui.chat_history.append(("user", f"🎙️ {transcript} (-> {mapped_cmd})"))
                                        # 변환된 명령어로 다시 루프 실행
                                        user_input = mapped_cmd
                                    else:
                                        self.ui.chat_history.append(("system", "❌ 음성을 인식하지 못했습니다."))
                            except Exception as e:
                                self.ui.chat_history.append(("system", f"❌ Voice Error: {e}"))
                            finally:
                                live.start()
                                if not user_input.startswith("/"): # 명령어가 아닌 일반 텍스트면 워크플로우 실행
                                    current_task = asyncio.create_task(execute_workflow(user_input))
                                    continue
                                # 명령어로 변환되었다면 다시 아래 / 처리 로직이나 다음 루프에서 처리되도록 함
                                # 여기서는 간편하게 다시 위로 점프하기 위해 continue 처리하고 user_input을 보존
                        
                        if cmd_result == "config_ui":
                            live.stop()
                            try:
                                from gortex.ui.components.config_manager import ConfigManagerUI
                                ConfigManagerUI(self.console).run_menu()
                            except Exception as e:
                                self.ui.chat_history.append(("system", f"❌ Config UI Error: {e}"))
                            finally:
                                live.start()
                                self.ui.update_main(self.ui.chat_history)
                        live.refresh()
                        continue

                    if current_task and not current_task.done():
                        self.ui.chat_history.append(("system", "⏳ Neural pathways busy..."))
                        continue
                    
                    current_task = asyncio.create_task(execute_workflow(user_input))

        finally:
            recovery_task.cancel()
            trend_task.cancel()
            try:
                await asyncio.gather(recovery_task, trend_task, return_exceptions=True)
            except asyncio.CancelledError: pass

        # Cleanup & Finalization
        AnalystAgent().auto_finalize_session(self.state)
        self.session_manager.update_session(self.thread_id, self.state["file_cache"])
        self.console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")