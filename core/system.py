import asyncio
import logging
import uuid
import os
import dataclasses
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

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

logger = logging.getLogger("GortexSystem")

class GortexSystem:
    def __init__(self):
        self.console = Console()
        self.theme_manager = ThemeManager()
        self.ui = DashboardUI(console=self.console)
        self.observer = GortexObserver()
        self.vocal = VocalBridge()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.session_manager = SessionManager()
        self.thread_id = str(uuid.uuid4())[:8]

        # Initialize State (Dictionary based now)
        session_data = self.session_manager.get_session(self.thread_id)

        # Ensure working directory exists
        os.makedirs(settings.WORKING_DIR, exist_ok=True)
        checked_session_data, _ = deep_integrity_check(settings.WORKING_DIR, session_data)

        # Initialize the state dictionary conforming to GortexState TypedDict
        self.state: GortexState = {
            "agent_energy": 100,
            "last_efficiency": 100.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "session_cache": checked_session_data, # mapped to file_cache in graph logic often, but let's keep consistency
            "file_cache": checked_session_data, # redundancy for compatibility
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
            "efficiency_history": []
        }

    async def get_user_input(self):
        terminal_task = asyncio.create_task(asyncio.get_event_loop().run_in_executor(None, input, "👤 You: "))
        done, pending = await asyncio.wait([terminal_task], return_when=asyncio.FIRST_COMPLETED)
        for t in pending: t.cancel()
        return done.pop().result().strip() if done else ""

    async def energy_recovery_loop(self):
        """Loop to recover energy during idle time."""
        while True:
            await asyncio.sleep(2)
            if self.state["agent_energy"] < 100:
                self.state["agent_energy"] = min(100, self.state["agent_energy"] + 1)

                self.ui.update_energy_visualizer(self.state["agent_energy"])

                if self.ui.current_agent == "Idle":
                    self.ui.update_sidebar(
                        "Idle", "Recovering...",
                        self.state["total_tokens"],
                        self.state["total_cost"],
                        0,
                        energy=self.state["agent_energy"],
                        efficiency=self.state["last_efficiency"],
                        agent_economy=self.state.get("agent_economy"),
                        capability="N/A",
                        predicted_usage=self.state.get("current_predicted_usage")
                    )

    async def run(self):
        workflow = compile_gortex_graph()
        self.console.print(f"[bold cyan]🚀 {i18n.t('system.initialized', thread_id=self.thread_id)}[/bold cyan]")

        recovery_task = asyncio.create_task(self.energy_recovery_loop())

        try:
            with Live(self.ui.layout, console=self.console, refresh_per_second=4) as live:
                while True:
                    try:
                        user_input = await self.get_user_input()
                        if not user_input: continue
                        if user_input.lower() in ["exit", "quit", "q"]:
                            break

                        if self.state.get("last_question") and user_input:
                            try:
                                AnalystAgent().learn_from_interaction(self.state["last_question"], user_input)
                                self.state["last_question"] = None
                            except:
                                pass

                        if user_input.startswith("/"):
                            status = await handle_command(
                                user_input,
                                self.ui,
                                self.observer,
                                self.session_manager.all_sessions_cache,
                                self.thread_id,
                                self.theme_manager
                            )
                            if status == "skip": continue

                        initial_state = {
                            "messages": [("user", user_input)],
                            "pinned_messages": self.state["pinned_messages"],
                            "working_dir": settings.WORKING_DIR,
                            "file_cache": self.state["file_cache"],
                            "agent_energy": self.state["agent_energy"],
                            "last_efficiency": self.state["last_efficiency"]
                        }

                        async for event in workflow.astream(initial_state, config={"configurable": {"thread_id": self.thread_id}}):
                            for node_name, output in event.items():

                                # PASSING MUTABLE STATE (self.state is a dict now)
                                node_tokens = await self.engine.process_node_output(node_name, output, self.state)

                                # Write back changes (manual sync for some, others by reference)
                                self.state["total_tokens"] += node_tokens
                                self.state["total_cost"] += estimate_cost(node_tokens)

                                if "predicted_usage" in output:
                                    self.state["current_predicted_usage"] = output["predicted_usage"]

                                if node_name == "manager" and output.get("question_to_user"):
                                    self.state["last_question"] = output["question_to_user"]

                                # Update UI
                                self.ui.update_main(self.ui.chat_history)
                                self.ui.update_sidebar(
                                    node_name,
                                    "Active",
                                    self.state["total_tokens"],
                                    self.state["total_cost"],
                                    0,
                                    energy=self.state["agent_energy"],
                                    efficiency=self.state["last_efficiency"],
                                    agent_economy=self.state.get("agent_economy"),
                                    capability=output.get("required_capability", "N/A"),
                                    predicted_usage=self.state.get("current_predicted_usage")
                                )

                        # Persist session
                        self.session_manager.update_session(self.thread_id, self.state["file_cache"])

                        if self.observer:
                            collab_matrix = self.observer.get_collaboration_matrix()
                            self.ui.update_collaboration_heatmap(collab_matrix)

                        self.ui.update_sidebar(
                            "Idle", "N/A",
                            self.state["total_tokens"],
                            self.state["total_cost"],
                            0,
                            energy=self.state["agent_energy"],
                            efficiency=self.state["last_efficiency"],
                            agent_economy=self.state.get("agent_economy"),
                            capability="N/A",
                            predicted_usage=self.state.get("current_predicted_usage")
                        )

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        if "할당량" in str(e).lower() or "exhausted" in str(e).lower():
                            live.stop()
                            self.console.clear()
                            warning = Text.assemble(("\n🚫 API QUOTA EXHAUSTED\n\n", "bold red"), ("All API keys exhausted.\n", "white"))
                            self.console.print(Align.center(Panel(warning, title="EMERGENCY", border_style="red"), vertical="middle"))
                            break
                        logger.error(f"Loop error: {e}")
                        self.ui.chat_history.append(("system", f"❌ Error: {e}"))

        finally:
            recovery_task.cancel()
            try:
                await recovery_task
            except asyncio.CancelledError:
                pass

        # Cleanup
        AnalystAgent().auto_finalize_session({
             "messages": [], # Simplify for closure
             "pinned_messages": self.state["pinned_messages"],
             "working_dir": settings.WORKING_DIR,
             "file_cache": self.state["file_cache"],
             "agent_energy": self.state["agent_energy"],
             "last_efficiency": self.state["last_efficiency"]
        })
        self.session_manager.update_session(self.thread_id, self.state["file_cache"])
        self.console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")
