from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.columns import Columns
from rich import box
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional

from gortex.ui.themes.palette import Palette, get_agent_style
from gortex.ui.components.header import AppHeader
from gortex.ui.components.welcome import WelcomeScreen
from gortex.ui.components.monitor import SystemMonitor

logger = logging.getLogger("GortexDashboard")

class DashboardUI:
    """Gortex "Agent OS" Master UI.

    Inspired by gemini-cli, optimized for professional aesthetics.
    Handles rendering of the main application layout including chat, thoughts, and stats.

    Args:
        console (Console): The rich console instance to use for rendering.
    """
    def __init__(self, console: Console):
        self.console = console
        self.chat_history = []
        self.recent_logs = []
        self.current_agent = "System"
        self.current_step = "Initialized"
        self.tokens_used = 0
        self.total_cost = 0.0
        self.rules_count = 0
        self.provider = "GEMINI"
        self.energy = 100
        self.efficiency = 100.0
        self.agent_thought = ""
        self.collab_matrix = {}
        
        # [Phase 3] System Inspector
        self.monitor = SystemMonitor(console)
        self.monitor_active = False

    def update_sidebar(self, agent="Idle", step="Ready", tokens=None, cost=None, rules=None, provider=None, energy=None, efficiency=None):
        if agent: self.current_agent = agent
        if step: self.current_step = step
        if tokens is not None: self.tokens_used = tokens
        if cost is not None: self.total_cost = cost
        if rules is not None: self.rules_count = rules
        if provider: self.provider = provider
        if energy is not None: self.energy = energy
        if efficiency is not None: self.efficiency = efficiency

    def update_main(self, messages: list):
        self.chat_history = messages

    def update_thought(self, thought: str, agent_name: str = None):
        if thought is not None: self.agent_thought = thought
        if agent_name: self.current_agent = agent_name

    def update_logs(self, log_entry: dict):
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 8: self.recent_logs.pop(0)
        
    def toggle_monitor_mode(self):
        """Toggle System Inspector overlay."""
        self.monitor_active = not self.monitor_active
        mode_msg = "ON" if self.monitor_active else "OFF"
        self.chat_history.append(("system", f"🔍 System Monitor: [bold]{mode_msg}[/]"))

    def _render_chat(self, height: int, width: int) -> Group:
        if not self.chat_history:
            return Group(WelcomeScreen.render(width))
            
        elements = []
        # Calculate limit based on available vertical space
        limit = max(1, height // 6)
        for role, content in self.chat_history[-limit:]:
            if role == "user":
                elements.append(Panel(
                    Text(str(content), style=Palette.FOREGROUND),
                    title=f" [bold {Palette.GREEN}]👤 USER[/] ",
                    border_style=Palette.GREEN,
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
            elif role == "ai":
                elements.append(Panel(
                    Markdown(str(content)),
                    title=f" [bold {Palette.CYAN}]🤖 GORTEX[/] ",
                    border_style=Palette.CYAN,
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
            else:
                elements.append(Text.from_markup(f"  [dim]• {content}[/]", style=f"dim {Palette.GRAY}"))
        return Group(*elements)

    def _render_info_table(self) -> Table:
        table = Table.grid(expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        
        table.add_row(
            Text.from_markup(f" [{Palette.CYAN}]⚡ Tokens[/]\n [bold]{self.tokens_used:,}[/]"),
            Text.from_markup(f" [{Palette.GREEN}]💰 Cost[/]\n [bold]${self.total_cost:.4f}[/]")
        )
        table.add_row("", "")
        table.add_row(
            Text.from_markup(f" [{Palette.YELLOW}]📜 Rules[/]\n [bold]{self.rules_count}[/]"),
            Text.from_markup(f" [{Palette.MAGENTA}]📈 Efficiency[/]\n [bold]{self.efficiency:.1f}%[/]")
        )
        return table

    @property
    def layout(self) -> Layout:
        width = self.console.width
        height = self.console.height
        
        l = Layout()
        l.split_column(
            Layout(name="header", size=10 if width >= 100 else 6),
            Layout(name="body")
        )
        
        # 1. Header
        header_comp = AppHeader(width, self.energy, self.provider)
        l["header"].update(header_comp.render())

        # [Phase 3] System Monitor Overlay
        if self.monitor_active:
            # 상태값 주입
            state_snapshot = {
                "agent_energy": self.energy,
                "total_tokens": self.tokens_used,
                "total_cost": self.total_cost
            }
            self.monitor.collect_metrics(state_snapshot)
            l["body"].update(self.monitor.render())
            return l

        l["body"].split_row(
            Layout(name="main", ratio=3),
            Layout(name="side", ratio=1)
        )
        
        l["main"].split_column(
            Layout(name="chat", ratio=1),
            Layout(name="thought", size=5)
        )
        
        # 2. Main Chat
        l["chat"].update(Panel(
            self._render_chat(height - 15, width), 
            title=f" [bold {Palette.BLUE}]⚡ AGENT CORE[/] ", 
            border_style=Palette.BLUE, 
            box=box.ROUNDED
        ))

        # 3. Thought Panel
        agent_style = get_agent_style(self.current_agent)
        thought_msg = self.agent_thought if self.agent_thought else "System idle. Awaiting neural input..."
        thought_content = Text.assemble(
            (f" {self.current_agent.upper()} ", f"bold {agent_style} reverse"),
            (f"  {thought_msg}", f"italic {agent_style}")
        )
        l["thought"].update(Panel(
            thought_content, 
            title=" [bold italic]Thinking Scratchpad[/] ",
            border_style=agent_style, 
            box=box.ROUNDED,
            padding=(1, 2)
        ))

        # 4. Sidebar
        side_l = Layout()
        side_l.split_column(
            Layout(name="info", size=8),
            Layout(name="trace", ratio=1)
        )
        
        logs = "\n".join([f"[{get_agent_style(log.get('agent',''))}]{log.get('agent','Sys')[:3].upper()}[/] {log.get('event','')[:20]}" for log in self.recent_logs])
        
        side_l["info"].update(Panel(self._render_info_table(), title=" [bold]📊 STATS[/] ", border_style=Palette.GRAY, box=box.ROUNDED))
        side_l["trace"].update(Panel(Text.from_markup(logs), title=" [bold]🔍 TRACE[/] ", border_style=Palette.GRAY, box=box.ROUNDED))
        
        l["side"].update(side_l)

        return l

    # Stubs
    def update_energy_visualizer(self, *args): pass
    def update_auth_panel(self, *args): pass
    def update_impact_panel(self, *args): pass
    def update_collaboration_heatmap(self, m): self.collab_matrix = m
    def update_debt_panel(self, *args): pass
    def update_registry_panel(self, *args): pass
    def update_economy_panel(self, *args): pass
    def add_achievement(self, text: str): self.update_logs({"agent": "System", "event": text})
    def add_security_event(self, s, t): self.update_logs({"agent": "Security", "event": t})
    def set_mode(self, *args): pass
    def set_layout_mode(self, *args): pass
    def filter_thoughts(self, *args, **kwargs): return []
    def add_journal_entry(self, *args): pass
    def update_review_board(self, *args): pass