from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.spinner import Spinner
from datetime import datetime

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
        Layout(name="stats", size=10),
        Layout(name="evolution")
    )
    return layout

class DashboardUI:
    def __init__(self, console: Console):
        self.console = console
        self.layout = create_layout()
        self.chat_history = []
        self.agent_thought = ""
        self.current_agent = "Idle"
        self.current_step = "N/A"
        self.tokens_used = 0
        self.total_cost = 0.0
        self.active_rules_count = 0

    def update_main(self, messages: list):
        """메인 채팅 패널 업데이트 (역할별 구분 강화)"""
        display_msgs = messages[-10:] # 최근 10개만 표시하여 가독성 유지
        msg_group = []
        for role, content in display_msgs:
            if role == "user":
                msg_group.append(Panel(content, title="[bold green]User[/bold green]", border_style="green"))
            elif role == "ai":
                # 에이전트 응답 (결과)
                msg_group.append(Panel(content, title="[bold blue]Gortex[/bold blue]", border_style="blue"))
            elif role == "tool":
                # 도구 실행 결과 (Observation)
                msg_group.append(Panel(content, title="🛠️ [bold yellow]Observation[/bold yellow]", border_style="yellow", style="dim"))
            elif role == "system":
                msg_group.append(Text(f"⚙️ {content}", style="dim white"))
        
        self.layout["main"].update(
            Panel(Group(*msg_group), title="[bold cyan]🧠 Gortex Terminal[/bold cyan]")
        )

    def update_thought(self, thought: str):
        """에이전트의 사고 과정 실시간 업데이트"""
        self.agent_thought = thought
        self.layout["thought"].update(
            Panel(Text(thought, style="italic cyan"), title="💭 [bold cyan]Agent reasoning[/bold cyan]", border_style="cyan")
        )

    def update_sidebar(self, agent: str, step: str, tokens: int, cost: float, rules: int):
        """사이드바 정보 업데이트"""
        self.current_agent = agent
        self.current_step = step
        self.tokens_used = tokens
        self.total_cost = cost
        self.active_rules_count = rules

        # Status
        status_text = Text()
        status_text.append(f"Agent: ", style="bold")
        status_text.append(f"{agent}\n", style="yellow" if agent != "Idle" else "green")
        status_text.append(f"Step: ", style="bold")
        status_text.append(f"{step}\n")
        status_text.append(f"Time: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        status_group = [status_text]
        if agent != "Idle":
            status_group.append(Spinner("dots", text=f"[bold yellow]{agent} is active[/bold yellow]"))

        self.layout["status"].update(Panel(Group(*status_group), title="📡 System Status"))

        # Stats
        stats_table = Table.grid(expand=True)
        stats_table.add_row("Tokens:", f"[bold cyan]{tokens:,}[/bold cyan]")
        stats_table.add_row("Cost:", f"[bold green]${cost:.6f}[/bold green]")
        self.layout["stats"].update(Panel(stats_table, title="📊 Usage Stats"))

        # Evolution
        evo_text = Text(f"Active Rules: {rules}\n", style="bold magenta")
        if rules > 0:
            evo_text.append("[LEARNED MODE]", style="blink magenta")
        self.layout["evolution"].update(Panel(evo_text, title="🧬 Evolution"))

    def render(self):
        return self.layout