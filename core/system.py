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

    async def run(self):
        # 1. Boot Sequence
        boot = BootManager(self.console)
        await boot.run_sequence()

        workflow = compile_gortex_graph()
        recovery_task = asyncio.create_task(self.energy_recovery_loop())
        trend_task = asyncio.create_task(self.trend_scout_loop())

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
                        
                        node_tokens = await self.engine.process_node_output(node_name, output, self.state)
                        self.state["total_tokens"] += node_tokens
                        self.state["total_cost"] += estimate_cost(node_tokens)

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