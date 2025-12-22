from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.json import JSON
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from gortex.utils.table_detector import try_render_as_table
from gortex.utils.asset_manager import SynapticAssetManager
from gortex.ui.dashboard_theme import ThemeManager
from datetime import datetime
import logging
import json

logger = logging.getLogger("GortexDashboard")

def render_sparkline(data: list[float]) -> str:
    """Renders a simple unicode sparkline."""
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

def create_layout() -> Layout:
    """대시보드 레이아웃 생성: 채팅(Main), 사고(Thought), 사이드바(Sidebar)"""
    layout = Layout()
    layout.split_row(
        Layout(name="content", ratio=7),
        Layout(name="sidebar", ratio=3)
    )
    layout["content"].split_column(
        Layout(name="main", ratio=7),
        Layout(name="thought", ratio=3)
    )
    layout["sidebar"].split_column(
        Layout(name="status", size=10),
        Layout(name="stats", size=12),
        Layout(name="economy", size=8), # Reputation Leaderboard
        Layout(name="evolution", size=8),
        Layout(name="debt", size=10),
        Layout(name="logs")
    )
    return layout

class DashboardUI:
    def __init__(self, console: Console):
        self.console = console
        self.assets = SynapticAssetManager()
        self.theme = ThemeManager()
        self.layout = create_layout()
        self.chat_history = []
        self.agent_thought = ""
        self.thought_tree = []
        self.thought_history = [] 
        self.current_agent = "Idle"
        self.last_agent = "Idle"
        self.current_step = "N/A"
        self.tokens_used = 0
        self.total_cost = 0.0
        self.active_rules_count = 0
        self.recent_logs = []
        self.provider = "GEMINI"
        self.call_count = 0
        self.energy = 100
        self.efficiency = 100.0
        self.achievements = []
        self.debt_list = []
        self.active_debate = []
        self.knowledge_lineage = []
        self.suggested_actions = []
        
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
            TimeElapsedColumn(),
            transient=True
        )
        self.tool_task = None

        self.agent_colors = {
            "manager": "agent.manager",
            "planner": "agent.planner",
            "coder": "agent.coder",
            "researcher": "agent.researcher",
            "analyst": "agent.analyst",
            "trend_scout": "agent.trend_scout",
            "summarizer": "agent.summarizer",
            "optimizer": "agent.optimizer"
        }
        
        self.agent_spinners = {
            "manager": "dots",
            "planner": "bouncingBar",
            "coder": "simpleDotsScrolling",
            "researcher": "earth",
            "analyst": "pulse",
            "trend_scout": "moon",
            "summarizer": "aesthetic",
            "optimizer": "runner"
        }

    def update_debate_monitor(self, debate_data: list):
        self.active_debate = debate_data
        if not debate_data: return

        debate_group = []
        debate_group.append(Text("⚔️ [bold red]MULTI-AGENT DEBATE IN PROGRESS[/bold red]", justify="center"))
        
        for entry in debate_data:
            persona = entry.get("persona", "Neutral")
            color = "magenta" if persona == "Innovation" else "cyan"
            title = f"🎭 {persona.upper()}"
            content = entry.get("report", "")[:500] + "..." if len(entry.get("report", "")) > 500 else entry.get("report", "")
            debate_group.append(Panel(content, title=title, border_style=color, padding=(0, 1)))

        self.layout["main"].update(Panel(Group(*debate_group), title="[bold red]⚖️ CONSENSUS DEBATE[/bold red]", border_style="red"))

    def update_debt_panel(self, debt_list: list):
        self.debt_list = debt_list
        if not debt_list:
            self.layout["debt"].update(Panel("No debt scanned.", title="📉 TECHNICAL DEBT", border_style="dim"))
            return

        table = Table.grid(expand=True)
        for item in debt_list[:5]:
            file_name = item.get("file", "").split("/")[-1]
            score = item.get("score", 0)
            color = "red" if score > 50 else ("yellow" if score > 20 else "green")
            table.add_row(f"{file_name}", f"[{color}]{score}[/{color}]")
            
        self.layout["debt"].update(Panel(table, title="📉 [bold red]TECHNICAL DEBT[/]", border_style="red"))

    def update_main(self, messages: list):
        if len(messages) > 50: del messages[:-50]

        display_msgs = messages[-15:]
        msg_group = []
        
        if len(messages) > 15:
            msg_group.append(Text(f"⬆️ (이전 대화 기록은 /logs 또는 /history로 확인 가능)", style="dim white italic", justify="center"))

        for item in display_msgs:
            try:
                if not isinstance(item, (list, tuple)) or len(item) < 2: continue
                role, content = item
            except Exception: continue

            if role == "user":
                icon = self.assets.get_icon("user")
                msg_group.append(Panel(content, title=f"{icon} [bold green]USER[/bold green]", border_style="green", padding=(0, 1)))
            elif role == "ai":
                icon = self.assets.get_icon("robot")
                msg_group.append(Panel(content, title=f"{icon} [bold blue]GORTEX[/bold blue]", border_style="blue", padding=(0, 1)))
            elif role == "tool":
                icon = self.assets.get_icon("info")
                if isinstance(content, str):
                    display_content = content
                    if len(content) > 2000:
                        display_content = content[:1000] + f"\n\n[... {len(content)-2000} characters truncated ...]\n\n" + content[-1000:]
                    
                    try:
                        stripped = display_content.strip()
                        if (stripped.startswith("{}") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                            json.loads(stripped)
                            renderable = JSON(stripped)
                            msg_group.append(Panel(renderable, title=f"{icon} [bold yellow]OBSERVATION (JSON)[/bold yellow]", border_style="yellow", style="dim"))
                            continue
                    except:
                        pass

                    table_renderable = try_render_as_table(display_content)
                    if table_renderable:
                        msg_group.append(Panel(table_renderable, title=f"{icon} [bold yellow]OBSERVATION (TABLE)[/bold yellow]", border_style="yellow", style="dim"))
                        continue

                    code_keywords = ["import ", "def ", "class ", "void ", "public ", "{", "}", "const ", "SELECT ", "INSERT ", "UPDATE ", "DELETE ", "#!", "bash", "npm "]
                    if any(x in display_content for x in code_keywords):
                        lang = "python"
                        if "SELECT " in display_content or "UPDATE " in display_content: lang = "sql"
                        elif "void " in display_content or "public class " in display_content: lang = "java"
                        elif "#!" in display_content or "npm " in display_content or "$ " in display_content: lang = "bash"
                        elif "const " in display_content or "function " in display_content: lang = "javascript"
                        
                        syntax_content = Syntax(display_content, lang, theme="monokai", line_numbers=True, word_wrap=True)
                        msg_group.append(Panel(syntax_content, title=f"{icon} [bold yellow]OBSERVATION ({lang.upper()})[/bold yellow]", border_style="yellow", style="dim"))
                    else:
                        msg_group.append(Panel(display_content, title=f"{icon} [bold yellow]OBSERVATION[/bold yellow]", border_style="yellow", style="dim"))
                else:
                    msg_group.append(Panel(content, title=f"{icon} [bold yellow]OBSERVATION[/bold yellow]", border_style="yellow", style="dim"))
            elif role == "system":
                icon = self.assets.get_icon("info")
                if isinstance(content, str):
                    msg_group.append(Text(f"{icon} {content}", style="dim white"))
                else:
                    msg_group.append(content)
        
        self.layout["main"].update(Panel(Group(*msg_group), title="[bold cyan]🧠 GORTEX TERMINAL[/bold cyan]", border_style="cyan"))

    def render_thought_tree(self) -> Group:
        if not self.thought_tree: return Group(Text("No thought tree available.", style="dim"))

        tree_display = []
        children = {}
        roots = []
        for item in self.thought_tree:
            p_id = item.get("parent_id")
            if not p_id:
                roots.append(item)
            else:
                if p_id not in children: children[p_id] = []
                children[p_id].append(item)

        def add_node(node, indent=0):
            prefix = "  " * indent + ("┗━ " if indent > 0 else "● ")
            type_color = "cyan" if node["type"] == "analysis" else ("yellow" if node["type"] == "design" else "green")
            line = Text(prefix)
            line.append(node["text"], style=f"bold {type_color}")
            tree_display.append(line)
            
            for child in children.get(node["id"], []):
                add_node(child, indent + 1)

        for root in roots:
            add_node(root)
            
        return Group(*tree_display)

    def update_thought(self, thought: str, agent_name: str = "agent", tree: list = None):
        self.agent_thought = thought
        if tree: self.thought_tree = tree
        
        timestamp = datetime.now().isoformat()
        self.thought_history.append((agent_name, thought, timestamp))
        
        style = self.agent_colors.get(agent_name.lower(), "agent.manager")
        title = f"💭 [{style}]AGENT REASONING ({agent_name.upper()})[/{style}]"
        
        if self.thought_tree:
            thought_group = Group(
                Text(thought, style="italic cyan"),
                Text("\n[Thought Tree Structure]", style="bold dim"),
                self.render_thought_tree()
            )
            self.layout["thought"].update(Panel(thought_group, title=title, border_style="cyan", padding=(1, 2)))
        else:
            self.layout["thought"].update(Panel(Text(thought, style="italic cyan"), title=title, border_style="cyan", padding=(1, 2)))

    def update_logs(self, log_entry: dict):
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 8: self.recent_logs.pop(0)
            
        log_table = Table.grid(expand=True)
        for i, entry in enumerate(self.recent_logs):
            agent = entry.get("agent", "Sys")
            event = entry.get("event", "event")
            style = self.agent_colors.get(agent.lower(), "dim white")
            
            if i == len(self.recent_logs) - 1:
                log_table.add_row(f"[bold reverse {style}]{agent.upper()}[/]", f"[bold reverse white]{event}[/]")
            else:
                log_table.add_row(f"[{style}]{agent.upper()}[/{style}]", f"[dim]{event}[/dim]")
            
        self.layout["logs"].update(Panel(log_table, title="📜 [bold white]TRACE LOGS[/bold white]", border_style="white"))

    def start_tool_progress(self, description: str):
        if self.tool_task is None:
            self.tool_task = self.progress.add_task(description, total=None)
        else:
            self.progress.update(self.tool_task, description=description)

    def stop_tool_progress(self):
        if self.tool_task is not None:
            self.progress.remove_task(self.tool_task)
            self.tool_task = None

    def update_sidebar(self, agent: str = "Idle", step: str = "N/A", tokens: int = 0, cost: float = 0.0, rules: int = 0, provider: str = "GEMINI", call_count: int = 0, avg_latency: int = 0, energy: int = 100, efficiency: float = 100.0, knowledge_lineage: list = None, suggested_actions: list = None, agent_economy: dict = None):
        """사이드바 정보 업데이트 (에이전트, 성능, 경제 상태 시각화)"""
        self.current_agent = agent
        self.current_step = step
        self.tokens_used = tokens
        self.total_cost = cost
        self.active_rules_count = rules
        self.provider = provider
        self.call_count = call_count
        self.energy = energy
        self.efficiency = efficiency
        if knowledge_lineage is not None: self.knowledge_lineage = knowledge_lineage
        if suggested_actions is not None: self.suggested_actions = suggested_actions
        
        agent_style_name = self.agent_colors.get(agent.lower(), "dim white")
        try:
            border_color = self.console.get_style(agent_style_name).color.name
        except:
            border_color = "cyan" if agent != "Idle" else "white"

        # [ECONOMY] 현재 에이전트 경제 정보
        rep_text = ""
        if agent_economy and agent.lower() in agent_economy:
            eco = agent_economy[agent.lower()]
            lvl = eco.get("level", "N/A")
            pts = eco.get("points", 0)
            rep_text = f" [{lvl}] {pts}pts"

        # Status
        status_text = Text()
        status_text.append(f"Agent: ", style="bold")
        agent_style = self.agent_colors.get(agent.lower(), "dim white")
        agent_label = self.assets.get_agent_label(agent)
        status_text.append(f"{agent_label}", style=agent_style if agent != "Idle" else "green")
        if rep_text: status_text.append(rep_text, style="italic yellow")
        status_text.append("\n")
        
        status_text.append(f"LLM  : ", style="bold")
        provider_style = "bold blue" if provider == "GEMINI" else "bold green"
        status_text.append(f"{provider}\n", style=provider_style)
        
        if self.knowledge_lineage:
            status_text.append(f"Source: ", style="bold")
            for item in self.knowledge_lineage[:2]:
                source = item.get("source", "N/A")
                score = item.get("score", 0)
                status_text.append(f"{source}({score}) ", style="italic magenta")
            status_text.append("\n")

        status_text.append(f"Load : ", style="bold")
        bars = min(10, (call_count + 1) // 2)
        load_color = "green" if bars < 4 else ("yellow" if bars < 8 else "red")
        status_text.append("█" * bars, style=load_color)
        status_text.append("░" * (10 - bars), style="dim")
        status_text.append(f" ({call_count}/min)\n", style="dim")

        status_text.append(f"Step : ", style="bold")
        status_text.append(f"{step}\n")
        
        if self.suggested_actions:
            status_text.append(f"🚀 Next? \n", style="bold yellow")
            for i, act in enumerate(self.suggested_actions):
                status_text.append(f" {i+1}. {act.get('label')}\n", style="dim cyan")

        status_text.append(f"Time : {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        status_group = [status_text]
        if agent != "Idle":
            spinner_style = self.agent_spinners.get(agent.lower(), "dots")
            status_group.append(Spinner(spinner_style, text=f"[{agent_style}]{agent} is active[/{agent_style}]"))

        self.layout["status"].update(Panel(Group(*status_group), title=f"📡 [bold {border_color}]SYSTEM STATUS[/]", border_style=border_color))

        # Stats
        stats_table = Table.grid(expand=True)
        stats_table.add_row("Tokens:", f"[bold cyan]{tokens:,}[/bold cyan]")
        stats_table.add_row("Cost  :", f"[bold green]${cost:.6f}[/bold green]")
        
        latency_color = "green" if avg_latency < 3000 else ("yellow" if avg_latency < 7000 else "red")
        stats_table.add_row("Avg Lat:", f"[{latency_color}]{avg_latency}ms[/{latency_color}]")
        
        # Energy & Efficiency Visualization
        energy_color = "green" if energy > 70 else ("yellow" if energy > 30 else "red")
        is_recovering = step == "Recovering..."
        energy_suffix = " [pulse]⚡[/]" if is_recovering else f" {energy}%"
        stats_table.add_row("Energy:", f"[{energy_color}]{'⚡' * (energy // 20)}{' ' * (5 - energy // 20)}{energy_suffix}[/{energy_color}]")
        
        eff_color = "cyan" if efficiency >= 80 else ("yellow" if efficiency >= 50 else "red")
        stats_table.add_row("Effic.:", f"[{eff_color}]{efficiency:.1f}[/{eff_color}]")
        
        stats_group = [stats_table]
        
        try:
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
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
        except Exception as e:
            logger.error(f"Failed to render health sparkline: {e}")

        if self.tool_task is not None:
            stats_group.append(Text("\n"))
            stats_group.append(self.progress)

        self.layout["stats"].update(Panel(Group(*stats_group), title=f"📊 [bold {border_color}]USAGE STATS[/]", border_style="green" if tokens > 0 else border_color))

        if agent_economy:
            self.update_economy_panel(agent_economy)

    def update_economy_panel(self, agent_economy: dict):
        """에이전트 평판 및 스킬 트리 업데이트"""
        if not agent_economy:
            self.layout["economy"].update(Panel("No data.", title="🏆 REPUTATION", border_style="dim"))
            return

        # 1. Leaderboard Table
        table = Table.grid(expand=True)
        sorted_agents = sorted(agent_economy.items(), key=lambda x: x[1].get("points", 0), reverse=True)
        
        for name, data in sorted_agents[:3]:
            lvl = data.get("level", "B")
            pts = data.get("points", 0)
            color = "yellow" if lvl == "Gold" else ("white" if lvl == "Silver" else "magenta")
            table.add_row(f"{name[:8]}", f"[{color}]{lvl}[/]", f"{pts}p")
            
        # 2. Skill Tree for Current Agent
        skill_group = []
        target = self.current_agent.lower()
        if target != "idle" and target in agent_economy:
            skills = agent_economy[target].get("skill_points", {})
            if skills:
                skill_group.append(Text(f"\n[ {target.upper()} SKILLS ]", style="bold cyan"))
                for cat, val in skills.items():
                    # 100점당 █ 하나 (최대 5개)
                    bars = min(5, (val // 100) + 1) if val > 0 else 0
                    bar_str = "█" * bars + "░" * (5 - bars)
                    skill_group.append(Text(f"{cat:8} {bar_str} {val}", style="dim"))

        economy_content = Group(table, *skill_group)
        self.layout["economy"].update(Panel(economy_content, title="🏆 [bold yellow]REPUTATION[/]", border_style="yellow"))

    def render(self):
        return self.layout

    def set_mode(self, mode: str):
        if mode == "coding":
            self.layout["content"]["main"].ratio = 6
            self.layout["content"]["thought"].ratio = 4
            self.layout["sidebar"].ratio = 3
        elif mode == "research":
            self.layout["content"]["main"].ratio = 7
            self.layout["sidebar"].ratio = 4
        elif mode == "debugging":
            self.layout["sidebar"]["logs"].size = 20
            self.layout["sidebar"]["status"].size = 8
        elif mode == "analyst":
            self.layout["sidebar"]["stats"].size = 15
        else:
            self.layout["content"]["main"].ratio = 7
            self.layout["content"]["thought"].ratio = 3
            self.layout["sidebar"].ratio = 3
            self.layout["sidebar"]["logs"].size = None
            
        logger.info(f"🎭 UI Layout adjusted to: {mode}")
