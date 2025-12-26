from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.markdown import Markdown
from rich import box
import logging
import json
from typing import Dict, List, Optional, Any

from gortex.ui.themes.palette import Palette, get_agent_style
from gortex.ui.components.header import AppHeader
from gortex.ui.components.welcome import WelcomeScreen
from gortex.ui.components.monitor import SystemMonitor
from gortex.ui.components.memory_viewer import MemoryViewer
from gortex.ui.components.trace_tree import TraceTreeRenderer
from gortex.core.registry import registry

logger = logging.getLogger("GortexDashboard")

def render_sparkline(data: List[float]) -> str:
    """Renders a simple unicode sparkline."""
    if not data:
        return ""
    min_val, max_val = min(data), max(data)
    if min_val == max_val:
        return "█" * len(data)
    
    chars = "  ▂▃▄▅▆▇█"
    steps = len(chars) - 1
    result = ""
    for val in data:
        normalized = (val - min_val) / (max_val - min_val)
        idx = int(normalized * steps)
        result += chars[idx]
    return result

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
        
        # Extended state for new panels
        self.active_rules_count = 0
        self.call_count = 0
        self.knowledge_lineage = []
        self.suggested_actions = []
        self.agent_economy = {}
        self.current_capability = "N/A"
        self.current_predicted_usage = None
        self.debt_list = []
        self.active_debate = []
        self.thought_history = []
        self.thought_tree = []

        # [Phase 3] System Inspector
        self.monitor = SystemMonitor(console)
        self.monitor_active = False

        # [Phase 3] Memory Explorer
        self.memory_viewer = MemoryViewer(console, None) # VectorStore는 지연 주입
        self.memory_active = False

        # [Phase 3] Logic Tracer
        self.trace_renderer = TraceTreeRenderer()
        self.trace_active = False

    def set_vector_store(self, store):
        self.memory_viewer.vector_store = store

    def update_sidebar(self, agent: str = "Idle", step: str = "N/A", tokens: int = 0, cost: float = 0.0, rules: int = 0, provider: str = "GEMINI", call_count: int = 0, avg_latency: int = 0, energy: int = 100, efficiency: float = 100.0, knowledge_lineage: list = None, suggested_actions: list = None, agent_economy: dict = None, capability: str = "N/A", predicted_usage: dict = None):
        self.current_agent = agent
        self.current_step = step
        self.current_capability = capability
        self.tokens_used = tokens
        self.total_cost = cost
        self.active_rules_count = rules
        self.provider = provider
        self.call_count = call_count
        self.energy = energy
        self.efficiency = efficiency
        if knowledge_lineage is not None:
            self.knowledge_lineage = knowledge_lineage
        if suggested_actions is not None:
            self.suggested_actions = suggested_actions
        if agent_economy is not None:
            self.agent_economy = agent_economy
        if predicted_usage is not None:
            self.current_predicted_usage = predicted_usage

    def update_main(self, messages: list):
        self.chat_history = messages

    def update_thought(self, thought: str, agent_name: str = "agent", tree: list = None):
        self.agent_thought = thought
        if tree:
            self.thought_tree = tree
        if agent_name:
            self.current_agent = agent_name
        self.thought_history.append((agent_name, thought, datetime.now().isoformat()))

    def update_logs(self, log_entry: dict):
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 8:
            self.recent_logs.pop(0)
        
    def toggle_monitor_mode(self):
        """Toggle System Inspector overlay."""
        self.monitor_active = not self.monitor_active
        self.memory_active = False
        self.trace_active = False
        mode_msg = "ON" if self.monitor_active else "OFF"
        self.chat_history.append(("system", f"🔍 System Monitor: [bold]{mode_msg}[/]"))

    def toggle_memory_mode(self, query=None):
        """Toggle Memory Explorer overlay."""
        if query:
            self.memory_active = True
            self.monitor_active = False
            self.trace_active = False
            self.memory_viewer.fetch_memories(query)
        else:
            self.memory_active = not self.memory_active
            self.monitor_active = False
            self.trace_active = False

        mode_msg = "ON" if self.memory_active else "OFF"
        self.chat_history.append(("system", f"🧠 Memory Explorer: [bold]{mode_msg}[/]"))
        if self.memory_active and not query:
             self.memory_viewer.fetch_memories("")

    def toggle_trace_mode(self):
        """Toggle Logic Tracer overlay."""
        self.trace_active = not self.trace_active
        if self.trace_active:
            self.monitor_active = False
            self.memory_active = False
            
        mode_msg = "ON" if self.trace_active else "OFF"
        self.chat_history.append(("system", f"🌱 Logic Tracer: [bold]{mode_msg}[/]"))

    def _render_chat(self, height: int, width: int) -> Group:
        if not self.chat_history:
            return Group(WelcomeScreen.render(width))
            
        elements = []
        limit = max(1, height // 10)
        max_content_lines = max(2, height // 4)

        for role, content in self.chat_history[-limit:]:
            content_str = str(content)
            lines = content_str.split("\n")
            if len(lines) > max_content_lines:
                content_str = "\n".join(lines[:max_content_lines]) + "\n[dim]...(Content truncated for UI stability)[/]"

            if role == "user":
                elements.append(Panel(
                    Text(content_str, style=Palette.FOREGROUND),
                    title=f" [bold {Palette.GREEN}]👤 USER[/] ",
                    border_style=Palette.GREEN,
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
            elif role == "ai":
                elements.append(Panel(
                    Markdown(content_str),
                    title=f" [bold {Palette.CYAN}]🤖 GORTEX[/] ",
                    border_style=Palette.CYAN,
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
            else:
                elements.append(Text.from_markup(f"  [dim]• {content_str[:100]}[/]", style=f"dim {Palette.GRAY}"))
        return Group(*elements)

    def _render_status_panel(self) -> Panel:
        status_text = Text()
        status_text.append("Agent: ", style="bold")
        agent_style = get_agent_style(self.current_agent)
        status_text.append(f"{self.current_agent.upper()}", style=agent_style if self.current_agent != "Idle" else "green")
        
        agent_id = self.current_agent.lower()
        if self.agent_economy and agent_id in self.agent_economy:
            eco = self.agent_economy[agent_id]
            lvl = eco.get("level", "N/A")
            pts = eco.get("points", 0)
            status_text.append(f" [{lvl}] {pts}pts", style="italic yellow")
            
            # [SKILL MATRIX] 숙련도 게이지 렌더링
            status_text.append("\n\n-- SKILL MATRIX --\n", style="dim")
            skills = eco.get("skill_points", {})
            for cat, pts in skills.items():
                # 3000pts를 마스터 기준으로 게이지 계산
                filled = min(10, int(pts / 3000 * 10))
                gauge = "█" * filled + "░" * (10 - filled)
                # 점수대에 따른 색상
                color = Palette.CYAN if pts > 1500 else (Palette.GREEN if pts > 500 else Palette.GRAY)
                status_text.append(f"{cat[:3].upper()} ", style="bold")
                status_text.append(f"[{gauge}]", style=color)
                status_text.append(f" {pts}p\n", style="dim")
        
        status_text.append("\n")
        if self.current_agent != "Idle":
            status_text.append("LLM  : ", style="bold")
            provider_style = "bold blue" if self.provider == "GEMINI" else "bold green"
            status_text.append(f"{self.provider}\n", style=provider_style)
            
            status_text.append("Step : ", style="bold")
            status_text.append(f"{self.current_step}\n")
        
        return Panel(status_text, title=" [bold]🛰️ STATUS[/] ", border_style=Palette.GRAY, box=box.ROUNDED)

    def _render_stats_panel(self) -> Panel:
        stats_group = []
        stats_group.append(Text.from_markup(f"[{Palette.CYAN}]⚡ Tokens[/]: [bold]{self.tokens_used:,}[/]"))
        stats_group.append(Text.from_markup(f"[{Palette.GREEN}]💰 Cost[/]  : [bold]${self.total_cost:.4f}[/]"))
        stats_group.append(Text.from_markup(f"[{Palette.YELLOW}]📜 Rules[/] : [bold]{self.active_rules_count}[/]"))
        stats_group.append(Text.from_markup(f"[{Palette.MAGENTA}]📈 Efficiency[/]: [bold]{self.efficiency:.1f}%[/]"))
        
        from gortex.utils.efficiency_monitor import EfficiencyMonitor
        try:
            health_hist = EfficiencyMonitor().get_health_history(limit=10)
            if health_hist:
                scores = [h.get("score", 0) for h in reversed(health_hist)]
                spark = render_sparkline(scores)
                current_health = scores[-1] if scores else 0
                trend_color = "green"
                if len(scores) > 1:
                    if scores[-1] < scores[-2]: trend_color = "red"
                    elif scores[-1] == scores[-2]: trend_color = "yellow"
                
                spark_text = Text("\nHealth: ", style="bold")
                spark_text.append(f"{current_health:.1f} ", style=trend_color)
                spark_text.append(f"{spark}", style=f"bold {trend_color}")
                stats_group.append(spark_text)
        except:
            pass

        return Panel(Group(*stats_group), title=" [bold]📊 STATS[/] ", border_style=Palette.GRAY, box=box.ROUNDED)

    @property
    def layout(self) -> Layout:
        width = self.console.width
        height = self.console.height
        
        main_layout = Layout()
        main_layout.split_column(
            Layout(name="header", size=10 if width >= 100 else 6),
            Layout(name="body")
        )
        
        header_comp = AppHeader(width, self.energy, self.provider)
        main_layout["header"].update(header_comp.render())

        if self.monitor_active:
            state_snapshot = {"agent_energy": self.energy, "total_tokens": self.tokens_used, "total_cost": self.total_cost}
            self.monitor.collect_metrics(state_snapshot)
            main_layout["body"].update(self.monitor.render())
            return main_layout

        if self.memory_active:
            main_layout["body"].update(self.memory_viewer.render())
            return main_layout

        if self.trace_active:
            main_layout["body"].update(self.trace_renderer.render_panel(self.recent_logs))
            return main_layout

        main_layout["body"].split_row(
            Layout(name="main", ratio=3),
            Layout(name="side", ratio=1)
        )
        
        main_layout["main"].split_column(
            Layout(name="chat", ratio=1),
            Layout(name="thought", size=5)
        )
        
        l_chat_height = height - 15
        main_layout["chat"].update(Panel(
            self._render_chat(l_chat_height, width), 
            title=f" [bold {Palette.BLUE}]⚡ AGENT CORE[/] ", 
            border_style=Palette.BLUE, 
            box=box.ROUNDED
        ))

        agent_style = get_agent_style(self.current_agent)
        thought_msg = self.agent_thought if self.agent_thought else "System idle. Awaiting neural input..."
        thought_content = Text.assemble(
            (f" {self.current_agent.upper()} ", f"bold {agent_style} reverse"),
            (f"  {thought_msg}", f"italic {agent_style}")
        )
        main_layout["thought"].update(Panel(
            thought_content, 
            title=" [bold italic]Thinking Scratchpad[/] ",
            border_style=agent_style, 
            box=box.ROUNDED,
            padding=(1, 2)
        ))

        side_l = Layout()
        side_l.split_column(
            Layout(name="status", size=8),
            Layout(name="stats", size=10),
            Layout(name="trace", ratio=1)
        )
        
        trace_logs = "\n".join([f"[{get_agent_style(log.get('agent',''))}]{log.get('agent','Sys')[:3].upper()}[/] {log.get('event','')[:20]}" for log in self.recent_logs])
        
        side_l["status"].update(self._render_status_panel())
        side_l["stats"].update(self._render_stats_panel())
        side_l["trace"].update(Panel(Text.from_markup(trace_logs), title=" [bold]🔍 TRACE[/] ", border_style=Palette.GRAY, box=box.ROUNDED))
        
        main_layout["side"].update(side_l)

        return main_layout

    # Stubs/Methods for origin/main compatibility
    def update_energy_visualizer(self, energy): self.energy = energy
    def update_auth_panel(self, *args): pass
    def update_impact_panel(self, target_symbol: str = None, dependents: list = None): pass
    def update_collaboration_heatmap(self, m): self.collab_matrix = m
    def update_debt_panel(self, debt_list: list): self.debt_list = debt_list
    def update_registry_panel(self, *args): pass
    def update_economy_panel(self, *args): pass
    def update_debate_monitor(self, debate_data: list): self.active_debate = debate_data
    def add_achievement(self, text: str): self.update_logs({"agent": "System", "event": text})
    def add_security_event(self, s, t): self.update_logs({"agent": "Security", "event": t})
    def set_mode(self, *args): pass
    def set_layout_mode(self, *args): pass
    def filter_thoughts(self, *args, **kwargs): return []
    def add_journal_entry(self, *args): pass
    def update_review_board(self, *args): pass
    def render_thought_tree(self): return Group()