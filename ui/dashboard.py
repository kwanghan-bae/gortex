from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.markdown import Markdown
from rich import box
import logging
import json
from datetime import datetime
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
    if not data: return ""
    min_val, max_val = min(data), max(data)
    if min_val == max_val: return "█" * len(data)
    chars = "  ▂▃▄▅▆▇█"
    steps = len(chars) - 1
    result = ""
    for val in data:
        normalized = (val - min_val) / (max_val - min_val)
        idx = int(normalized * steps)
        result += chars[idx]
    return result

class DashboardUI:
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
        self.target_language = "ko"
        
        self.agent_economy = {}
        self.current_capability = "N/A"
        self.active_rules_count = 0
        
        self.monitor = SystemMonitor(console)
        self.monitor_active = False
        self.memory_viewer = MemoryViewer(console, None)
        self.memory_active = False
        self.trace_renderer = TraceTreeRenderer()
        self.trace_active = False

    def set_vector_store(self, store):
        self.memory_viewer.vector_store = store

    def update_sidebar(self, agent: str = "Idle", step: str = "N/A", tokens: int = 0, cost: float = 0.0, rules: int = 0, provider: str = "GEMINI", energy: int = 100, efficiency: float = 100.0, agent_economy: dict = None, capability: str = "N/A", predicted_usage: dict = None):
        self.current_agent = agent
        self.current_step = step
        self.current_capability = capability
        self.tokens_used = tokens
        self.total_cost = cost
        self.active_rules_count = rules
        self.provider = provider
        self.energy = energy
        self.efficiency = efficiency
        if agent_economy: self.agent_economy = agent_economy

    def update_main(self, messages: list):
        self.chat_history = messages

    def update_thought(self, thought: str, agent_name: str = "agent"):
        self.agent_thought = thought
        if agent_name: self.current_agent = agent_name

    def update_logs(self, log_entry: dict):
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 8: self.recent_logs.pop(0)
        
    def toggle_monitor_mode(self):
        self.monitor_active = not self.monitor_active
        self.memory_active = self.trace_active = False

    def toggle_memory_mode(self, query=None):
        self.memory_active = not self.memory_active
        self.monitor_active = self.trace_active = False
        if self.memory_active: self.memory_viewer.fetch_memories(query or "")

    def toggle_trace_mode(self):
        self.trace_active = not self.trace_active
        self.monitor_active = self.memory_active = False

    def _render_chat(self, height: int, width: int) -> Group:
        if not self.chat_history: return Group(WelcomeScreen.render(width))
        elements = []
        limit = max(1, height // 10)
        max_content_lines = max(2, height // 4)
        for role, content in self.chat_history[-limit:]:
            content_str = str(content)
            if isinstance(content, dict) and self.target_language in content:
                content_str = f"🌐 [italic]{content[self.target_language]}[/]"
            lines = content_str.split("\n")
            if len(lines) > max_content_lines:
                content_str = "\n".join(lines[:max_content_lines]) + "\n[dim]...(Truncated)[/]"
            if role == "user":
                elements.append(Panel(Text(content_str, style=Palette.FOREGROUND), title=" 👤 USER ", border_style=Palette.GREEN))
            elif role == "ai":
                elements.append(Panel(Markdown(content_str), title=" 🤖 GORTEX ", border_style=Palette.CYAN))
            else:
                elements.append(Text.from_markup(f"  [dim]• {content_str[:100]}[/]", style=f"dim {Palette.GRAY}"))
        return Group(*elements)

    def _render_status_panel(self) -> Panel:
        status_text = Text()
        status_text.append("Agent: ", style="bold")
        agent_style = get_agent_style(self.current_agent)
        
        meta = registry.get_metadata(self.current_agent)
        display_name = self.current_agent.upper()
        if meta and "+slm" in meta.version:
            display_name = f"💎 {display_name} (v{meta.version})"
            agent_style = f"bold {Palette.MAGENTA}"
        
        status_text.append(f"{display_name}", style=agent_style if self.current_agent != "Idle" else "green")
        
        agent_id = self.current_agent.lower()
        if self.agent_economy and agent_id in self.agent_economy:
            eco = self.agent_economy[agent_id]
            lvl, pts, balance = eco.get("level", "N/A"), eco.get("points", 0), eco.get("credits", 0.0)
            
            from gortex.utils.economy import get_economy_manager
            trust_score = get_economy_manager().get_trust_score({}, self.current_agent)
            trust_label = "STANDARD"
            if trust_score > 0.9: trust_label = "ELITE"
            elif trust_score > 0.7: trust_label = "TRUSTED"
            
            status_text.append(f" [{lvl}] {pts}p | 💰 ${balance:.4f} | [{trust_label}]", style="italic yellow")
            
            status_text.append("\n\n-- SKILL MATRIX --\n", style="dim")
            skills = eco.get("skill_points", {})
            for cat, s_pts in skills.items():
                filled = min(10, int(s_pts / 3000 * 10))
                gauge = "█" * filled + "░" * (10 - filled)
                status_text.append(f"{cat[:3].upper()} [{gauge}] {s_pts}p\n", style=Palette.CYAN)
        
        status_text.append(f"\nLLM  : {self.provider}\nStep : {self.current_step}", style="bold white")
        return Panel(status_text, title=" 🛰️ STATUS ", border_style=Palette.GRAY, box=box.ROUNDED)

    def _render_stats_panel(self) -> Panel:
        stats_group = []
        stats_group.append(Text.from_markup(f"[{Palette.CYAN}]⚡ Tokens[/]: {self.tokens_used:,}"))
        stats_group.append(Text.from_markup(f"[{Palette.GREEN}]💰 Cost[/]  : ${self.total_cost:.4f}"))
        stats_group.append(Text.from_markup(f"[{Palette.MAGENTA}]📈 Efficiency[/]: {self.efficiency:.1f}%"))
        
        try:
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            analyst = AnalystAgent()
            maturity = analyst.calculate_system_maturity({"agent_economy": self.agent_economy})
            score = maturity["score"]
            stats_group.append(Text(f"\nMATURITY: {score}%", style="bold magenta"))
            
            from gortex.utils.hardware import sensor
            vitals = sensor.get_system_vitals()
            stats_group.append(Text(f"🔋 {vitals['battery_percent']}% | THERMAL: {vitals['thermal_status'].upper()}", style="green"))
        except: pass

        return Panel(Group(*stats_group), title=" 📊 STATS ", border_style=Palette.GRAY, box=box.ROUNDED)

    @property
    def layout(self) -> Layout:
        width, height = self.console.width, self.console.height
        main_layout = Layout()
        main_layout.split_column(Layout(name="header", size=10 if width >= 100 else 6), Layout(name="body"))
        
        main_layout["header"].update(AppHeader(width, self.energy, self.provider).render())

        if self.monitor_active:
            self.monitor.collect_metrics({"agent_energy": self.energy, "total_tokens": self.tokens_used, "total_cost": self.total_cost})
            main_layout["body"].update(self.monitor.render())
            return main_layout

        if self.memory_active:
            main_layout["body"].update(self.memory_viewer.render())
            return main_layout

        main_layout["body"].split_row(Layout(name="main", ratio=3), Layout(name="side", ratio=1))
        main_layout["main"].split_column(Layout(name="chat", ratio=1), Layout(name="thought", size=8))
        
        main_layout["chat"].update(Panel(self._render_chat(height - 18, width), title=" ⚡ AGENT CORE ", border_style=Palette.BLUE))
        
        agent_style = get_agent_style(self.current_agent)
        thought_content = Text.assemble((f" {self.current_agent.upper()} ", f"bold {agent_style} reverse"), (f"  {self.agent_thought}", f"italic {agent_style}"))
        main_layout["thought"].update(Panel(thought_content, title=" Thinking Scratchpad ", border_style=agent_style))

        side_l = Layout()
        side_l.split_column(Layout(name="status", size=14), Layout(name="stats", size=10), Layout(name="swarm", size=8), Layout(name="trace", ratio=1))
        
        from gortex.core.mq import mq_bus
        workers = mq_bus.list_active_workers()
        swarm_table = Table.grid(expand=True)
        for w in workers[:3]:
            swarm_table.add_row(f"🌐 ID:{w['worker_id'][-4:]}", f"{w['cpu_percent']}% ")
        
        side_l["status"].update(self._render_status_panel())
        side_l["stats"].update(self._render_stats_panel())
        side_l["swarm"].update(Panel(swarm_table, title=" 📡 SWARM MAP ", border_style=Palette.GRAY))
        
        logs = "\n".join([f"[{get_agent_style(log.get('agent',''))}]{log.get('agent','Sys')[:3].upper()}[/] {log.get('event','')[:20]}" for log in self.recent_logs])
        side_l["trace"].update(Panel(Text.from_markup(logs), title=" 🔍 TRACE ", border_style=Palette.GRAY))
        
        main_layout["side"].update(side_l)
        return main_layout

    def update_energy_visualizer(self, energy): self.energy = energy
    def update_collaboration_heatmap(self, m): pass
    def add_achievement(self, text: str): self.update_logs({"agent": "System", "event": text})
    def add_security_event(self, s, t): self.update_logs({"agent": "Security", "event": t})
    def set_mode(self, *args): pass
    def render_thought_tree(self): return Group()
