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
        
        # [NEW] Check for Custom SLM version
        from gortex.core.registry import registry
        meta = registry.get_metadata(self.current_agent)
        display_name = self.current_agent.upper()
        if meta and "+slm" in meta.version:
            display_name = f"💎 {display_name} (v{meta.version})"
            agent_style = f"bold {Palette.MAGENTA}"
        
        status_text.append(f"{display_name}", style=agent_style if self.current_agent != "Idle" else "green")
        
        agent_id = self.current_agent.lower()
        if self.agent_economy and agent_id in self.agent_economy:
            eco = self.agent_economy[agent_id]
            lvl = eco.get("level", "N/A")
            pts = eco.get("points", 0)
            balance = eco.get("credits", 0.0)
            
            # [WALLET] 잔고 표시
            balance_color = Palette.GREEN if balance > 1.0 else (Palette.YELLOW if balance > 0.1 else Palette.RED)
            status_text.append(f" [{lvl}] {pts}pts", style="italic yellow")
            status_text.append(f" | 💰 ${balance:.4f}", style=f"bold {balance_color}")
            
            # [TRUST BADGE] 신뢰 지수 시각화
            from gortex.utils.economy import get_economy_manager
            trust_score = get_economy_manager().get_trust_score({}, self.current_agent)
            trust_label = "STANDARD"
            trust_color = Palette.GRAY
            if trust_score > 0.9: trust_label = "ELITE"; trust_color = "bold " + Palette.MAGENTA
            elif trust_score > 0.7: trust_label = "TRUSTED"; trust_color = "bold " + Palette.CYAN
            elif trust_score > 0.5: trust_label = "VERIFIED"; trust_color = Palette.GREEN
            
            status_text.append(f" [{trust_label}]", style=trust_color)
            
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
        
        # [ACTIVE TASKS] 비동기 작업 목록 표시
        if self.suggested_actions: # suggested_actions 필드를 활성 태스크 표시용으로 재활용하거나 확장
            stats_group.append(Text("\n⚙️ ACTIVE TASKS", style="bold yellow"))
            for task in self.suggested_actions[:3]:
                stats_group.append(Text(f" ● {task.get('label', 'Task')}", style="cyan dim"))

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
                
                stats_group.append(Text("\nHealth: ", style="bold"))
                stats_group.append(Text(f"{current_health:.1f} ", style=trend_color))
                stats_group.append(Text(f"{spark}", style=f"bold {trend_color}"))
        except: pass

        # [NEURAL BENCHMARKS] 모델별 실전 성과 랭킹 표시
        try:
            model_scores = EfficiencyMonitor().calculate_model_scores()
            if model_scores:
                stats_group.append(Text("\n\n-- NEURAL BENCHMARKS --", style="dim"))
                # 점수 높은 순으로 상위 3개만
                sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
                for model, score in sorted_models[:3]:
                    # 모델명 축약 (예: gemini-2.0-flash -> G-Flash)
                    m_short = model.replace("gemini-", "G-").replace("ollama/", "O-")[:10]
                    stats_group.append(Text(f" {m_short:<10} {score:>5.1f}p", style="cyan dim"))
        except: pass

        # [SYSTEM MATURITY] 성숙도 지표 시각화 (v10.1)
        try:
            from gortex.agents.analyst import AnalystAgent
            maturity = AnalystAgent().calculate_system_maturity(getattr(self, "last_state", {}))
            score = maturity["score"]
            filled = int(score / 100 * 15)
            gauge = "█" * filled + "░" * (15 - filled)
            color = Palette.MAGENTA if score > 80 else (Palette.CYAN if score > 50 else Palette.YELLOW)
            stats_group.append(Text(f"\nMATURITY: [{gauge}] {score}%", style=f"bold {color}"))
        except: pass

        # [HARDWARE VITALS] 물리 상태 시각화 (v10.4)
        try:
            from gortex.utils.hardware import sensor
            vitals = sensor.get_system_vitals()
            eco_mult = sensor.get_eco_multiplier()
            
            thermal_color = Palette.GREEN if vitals["thermal_status"] == "nominal" else (Palette.YELLOW if vitals["thermal_status"] == "warning" else Palette.RED)
            battery_icon = "🔋" if vitals["is_charging"] else "🪫"
            
            vitals_text = Text(f"\n{battery_icon} {vitals['battery_percent']}% | THERMAL: {vitals['thermal_status'].upper()}", style=thermal_color)
            if eco_mult < 1.0:
                vitals_text.append(f" [ECO:{int(eco_mult*100)}%]", style=f"bold {Palette.CYAN} blink")
            stats_group.append(vitals_text)
        except: pass

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

                # 3. Thought Panel
                agent_style = get_agent_style(self.current_agent)
                thought_msg = self.agent_thought if self.agent_thought else "System idle. Awaiting neural input..."
                thought_content = Text.assemble(
                    (f" {self.current_agent.upper()} ", f"bold {agent_style} reverse"),
                    (f"  {thought_msg}", f"italic {agent_style}")
                )
                
                # [NEW] Architectural Blueprint Visualization
                from gortex.core.state import GortexState # (Type hint placeholder)
                blueprint_code = getattr(self, "current_blueprint", "")
                if blueprint_code:
                    blueprint_panel = Panel(
                        Text(blueprint_code, style="dim cyan"),
                        title=" [bold yellow]📐 ARCHITECTURAL BLUEPRINT[/] ",
                        border_style="yellow"
                    )
                    thought_group = Group(thought_content, Text("\n"), blueprint_panel)
                else:
                    thought_group = thought_content
        
                main_layout["thought"].update(Panel(
                    thought_group,
                    title=" [bold italic]Thinking Scratchpad[/] ",
                    border_style=agent_style,
                    box=box.ROUNDED,
                    padding=(1, 2)
                ))
        side_l = Layout()
        side_l.split_column(
            Layout(name="status", size=8),
            Layout(name="stats", size=12), # Increased size for SMI
            Layout(name="galactic", size=6), # [NEW] Galactic Mission Panel
            Layout(name="swarm", size=8),
            Layout(name="trace", ratio=1)
        )
        
        # [GALACTIC MISSIONS] 연합 미션 현황 렌더링
        gal_table = Table.grid(expand=True)
        gal_table.add_column(style="bold magenta")
        # (실제 구현 시 state에서 active_agendas 목록을 가져와서 표시)
        gal_table.add_row("🌌 Project Singularity")
        gal_table.add_row("[dim]Status: Voting (85% YES)[/]")
        
        side_l["galactic"].update(Panel(gal_table, title=" [bold]🌌 GLOBAL[/] ", border_style=Palette.GRAY, box=box.ROUNDED))
        
        trace_logs = "\n".join([f"[{get_agent_style(log.get('agent',''))}]{log.get('agent','Sys')[:3].upper()}[/] {log.get('event','')[:20]}" for log in self.recent_logs])
        
        # [SWARM MONITOR] 연결된 워커 목록 렌더링
        swarm_table = Table.grid(expand=True)
        swarm_table.add_column(ratio=1)
        swarm_table.add_column(justify="right")
        
        from gortex.core.mq import mq_bus
        active_workers = mq_bus.list_active_workers()
        if not active_workers:
            swarm_table.add_row("[dim]No remote workers.[/]", "")
        else:
            for w in active_workers[:3]: # 상위 3개만 표시
                w_id = w.get("worker_id", "???")[-4:]
                cpu = w.get("cpu_percent", 0)
                tasks = w.get("total_tasks_done", 0)
                color = "green" if cpu < 50 else ("yellow" if cpu < 80 else "red")
                swarm_table.add_row(f"🌐 ID:{w_id} ({tasks}t)", f"[{color}]{cpu}%[/]")
        
        side_l["status"].update(self._render_status_panel())
        side_l["stats"].update(self._render_stats_panel())
        side_l["swarm"].update(Panel(swarm_table, title=" [bold]📡 SWARM MAP[/] ", border_style=Palette.GRAY, box=box.ROUNDED))
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