import asyncio
import logging
import uuid
import os
import re
import json
import warnings
from typing import Optional

from rich.console import Console
from rich.live import Live

# prompt_toolkit for autocomplete
from prompt_toolkit import PromptSession
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
from gortex.utils.tools import deep_integrity_check
from gortex.utils.vocal_bridge import VocalBridge
from gortex.agents.analyst import AnalystAgent
from gortex.ui.components.boot import BootManager

logger = logging.getLogger("GortexSystem")

class GortexSystem:
    def __init__(self):
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
        self.workflow = compile_gortex_graph()
        self.current_task = None

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

        self.prompt_session = PromptSession(
            history=FileHistory("logs/input_history.txt"),
            completer=self._get_completer(),
            complete_while_typing=True
        )

    def _get_completer(self):
        from prompt_toolkit.completion import WordCompleter
        commands = ["/help", "/status", "/agents", "/inspect", "/rca", "/search", "/map", 
                    "/kg", "/scan_debt", "/index", "/voice", "/language", "/theme", 
                    "/config", "/export", "/import", "/clear", "/bug", "/mode", "/save", 
                    "/load", "/provider", "/model", "/history"]
        return WordCompleter(commands, ignore_case=True)

    async def get_user_input(self) -> Optional[str]:
        try:
            style = PromptStyle.from_dict({'prompt': 'ansigreen bold'})
            user_input = await self.prompt_session.prompt_async("\n👤 You: ", style=style)
            return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input.strip())
        except (KeyboardInterrupt, EOFError):
            return None

    async def energy_recovery_loop(self):
        while True:
            await asyncio.sleep(2)
            if self.state["agent_energy"] < 100:
                self.state["agent_energy"] = min(100, self.state["agent_energy"] + 1)
                self.ui.update_energy_visualizer(self.state["agent_energy"])

    async def trend_scout_loop(self):
        from gortex.agents.trend_scout import TrendScoutAgent
        scout = TrendScoutAgent()
        while True:
            await asyncio.sleep(3600)
            if scout.should_scan(settings.TREND_SCAN_INTERVAL_HOURS):
                try:
                    notifications = await scout.scan_trends()
                    for msg in notifications:
                        self.ui.add_achievement(f"Trend: {msg}")
                except Exception as e:
                    logger.error(f"Trend scout error: {e}")

    async def notification_listener_loop(self):
        from gortex.core.mq import mq_bus
        if not mq_bus.is_connected: return
        from gortex.core.web_api import manager as web_manager, format_event_for_web
        from gortex.core.collaboration import ambassador

        def handle_notification(msg):
            formatted_msg = format_event_for_web(msg)
            asyncio.create_task(web_manager.broadcast(json.dumps(formatted_msg, ensure_ascii=False)))
            
            event_type = msg.get("type")
            payload = msg.get("payload", {})
            agent = msg.get("agent", "Unknown")

            if event_type == "thought_update":
                self.ui.update_thought(f"[Distributed] {payload.get('text', '')}", agent_name=agent)
            elif event_type == "task_completed":
                self.ui.add_achievement(f"✨ {payload.get('type','').upper()} Done")
                self.ui.chat_history.append(("system", f"🔔 Task Done: {payload.get('query')}"))
            elif event_type == "training_completed":
                from gortex.core.llm.trainer import trainer
                if trainer.register_custom_model(payload.get("job_id"), payload.get("agent")):
                    self.ui.add_achievement(f"Evolved: {payload.get('agent')}")
            elif event_type == "agent_registered":
                self.engine.refresh_graph()
            elif event_type == "agent_deregistered":
                self.engine.refresh_graph()
            elif event_type == "security_violation":
                self.ui.add_security_event("CRITICAL", f"Blocked {agent}")
                self.state["last_security_alert"] = payload

        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, mq_bus.listen, "gortex:notifications", handle_notification)
        loop.run_in_executor(None, mq_bus.listen, "gortex:thought_stream", handle_notification)
        loop.run_in_executor(None, mq_bus.listen, "gortex:security_alerts", handle_notification)
        loop.run_in_executor(None, mq_bus.listen, "gortex:workspace_sync", self._handle_workspace_sync)
        loop.run_in_executor(None, mq_bus.listen, "gortex:galactic:wisdom", handle_galactic_events)
        loop.run_in_executor(None, mq_bus.listen, "gortex:galactic:economy", handle_galactic_events)
        
        # [GALACTIC GOVERNANCE] 전역 안건 수신 리스너 (v10.2 New)
        def handle_galactic_agendas(msg):
            if msg.get("type") == "agenda_proposed":
                payload = msg.get("payload", {})
                title = payload.get("title")
                logger.info(f"🌌 [Galactic] New agenda proposed: {title}")
                
                # Analyst를 통한 자동 검토
                audit = AnalystAgent().audit_autonomous_mission({"goal": payload.get("goal"), "mission_name": title})
                
                # 투표 행사
                ambassador.cast_federated_vote(
                    payload["agenda_id"], 
                    audit.get("is_approved", False),
                    audit.get("findings", ["Aligned with local constitution"])[0]
                )
                self.ui.chat_history.append(("system", f"🌌 **전역 안건 투표**: '{title}' 제안에 대해 {'찬성' if audit.get('is_approved') else '반대'} 투표를 행사했습니다."))

        loop.run_in_executor(None, mq_bus.listen, "gortex:galactic:agendas", handle_galactic_agendas)

    def _handle_workspace_sync(self, msg):
        if msg.get("type") == "file_changed":
            payload = msg.get("payload", {})
            path, content, new_hash = payload.get("path"), payload.get("content"), payload.get("hash")
            from gortex.utils.tools import get_file_hash
            if path and content and get_file_hash(path) != new_hash:
                os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
                with open(path, "w", encoding="utf-8") as f: f.write(content)
                self.ui.update_logs({"agent": "Sync", "event": f"Synced {os.path.basename(path)}"})

    def _handle_galactic_events(self, msg):
        from gortex.core.collaboration import ambassador
        if msg.get("type") == "wisdom_offered":
            payload = msg.get("payload", {})
            if payload.get("price", 0) < 10.0:
                ambassador.purchase_remote_wisdom(msg.get("agent"), payload["rules"], payload["price"], self.state)

    async def execute_workflow(self, user_input: str):
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
            async for event in self.workflow.astream(initial_state, config={"configurable": {"thread_id": self.thread_id}}):
                for node_name, output in event.items():
                    self.ui.update_sidebar(agent=node_name, step="Processing")
                    try:
                        node_tokens = await self.engine.process_node_output(node_name, output, self.state)
                    except PermissionError as pe:
                        from gortex.agents.swarm import SwarmAgent
                        vote_res = await SwarmAgent().run_security_vote(str(pe), self.state, output.get("action_payload", {}))
                        if vote_res.get("is_approved"):
                            self.ui.chat_history.append(("system", f"✅ Swarm Approved: {vote_res['rationale']}"))
                            node_tokens = 0
                        else: continue
                    self.state["total_tokens"] += node_tokens
                    self.ui.update_main(self.ui.chat_history)
            self.session_manager.update_session(self.thread_id, self.state["file_cache"])
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self.ui.chat_history.append(("system", f"❌ Error: {e}"))

    async def run_mission(self, user_input: str):
        """자가 가동 미션 실행 엔진"""
        await self.execute_workflow(user_input)

    async def autonomous_drive_loop(self):
        while True:
            await asyncio.sleep(300)
            if self.state["agent_energy"] > 90 and self.ui.current_agent == "Idle":
                logger.info("🤖 Sovereign Singularity: Generating autonomous mission...")
                from gortex.agents.manager import ManagerAgent
                mission = ManagerAgent().self_generate_mission(self.state)
                
                if mission:
                    # [V10.1] Safety Audit before execution
                    audit_res = AnalystAgent().audit_autonomous_mission(mission)
                    if audit_res.get("is_approved"):
                        msg = f"🌟 **자율 미션 승인**: '{mission['mission_name']}'\n\n**목표**: {mission['goal']}\n**리스크**: {int(audit_res['risk_score']*100)}%"
                        self.ui.chat_history.append(("system", msg))
                        self.ui.add_achievement("Secure Mission Started")
                        await self.run_mission(mission["goal"])
                    else:
                        logger.warning(f"🚫 Mission Rejected: {mission['mission_name']}. Reason: {', '.join(audit_res.get('findings', []))}")
                        self.ui.chat_history.append(("system", f"🛑 **자율 미션 반려**: '{mission['mission_name']}'이 안전 헌장을 위배하여 중단되었습니다."))

    async def run(self):
        boot = BootManager(self.console)
        await boot.run_sequence()
        from gortex.utils.integrity import guard
        if not os.path.exists(guard.signature_path): guard.generate_master_signature()
        from gortex.core.web_api import start_web_server
        asyncio.create_task(start_web_server(port=8000))
        
        asyncio.create_task(self.energy_recovery_loop())
        asyncio.create_task(self.trend_scout_loop())
        asyncio.create_task(self.notification_listener_loop())
        asyncio.create_task(self.autonomous_drive_loop())

        with Live(self.ui.layout, console=self.console, refresh_per_second=4, screen=False) as live:
            while True:
                live.stop()
                user_input = await self.get_user_input()
                live.start()
                if user_input is None or user_input.lower() in ["exit", "quit", "q"]: break
                if not user_input: continue
                if user_input.startswith("/"):
                    res = await handle_command(user_input, self.ui, self.observer, self.session_manager.all_sessions_cache, self.thread_id, self.theme_manager)
                    if res == "skip": continue
                self.current_task = asyncio.create_task(self.execute_workflow(user_input))
                await self.current_task

        AnalystAgent().auto_finalize_session(self.state)
        self.console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")
