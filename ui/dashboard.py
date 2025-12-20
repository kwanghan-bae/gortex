from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from datetime import datetime

def create_layout() -> Layout:
    """대시보드 기본 레이아웃 생성"""
    layout = Layout()
    layout.split_row(
        Layout(name="main", ratio=7),
        Layout(name="sidebar", ratio=3)
    )
    layout["sidebar"].split_column(
        Layout(name="status", size=10),
        Layout(name="stats"),
        Layout(name="evolution", size=12)
    )
    return layout

class DashboardUI:
    def __init__(self, console: Console):
        self.console = console
        self.layout = create_layout()
        self.chat_history = []
        self.current_agent = "Idle"
        self.current_step = "N/A"
        self.tokens_used = 0
        self.estimated_cost = 0.0
        self.active_rules_count = 0

    def update_main(self, messages: list):
        """메인 패널 업데이트 (채팅 내역)"""
        # 최근 20개 메시지만 표시
        display_msgs = messages[-20:]
        msg_group = []
        for role, content in display_msgs:
            if role == "user":
                msg_group.append(Panel(content, title="[bold green]User[/bold green]", border_style="green"))
            elif role == "ai":
                msg_group.append(Panel(content, title="[bold blue]Gortex[/bold blue]", border_style="blue"))
            elif role == "system":
                msg_group.append(Text(f"⚙️ {content}", style="dim white"))
        
        self.layout["main"].update(
            Panel(Group(*msg_group), title="[bold cyan]🧠 Gortex Terminal[/bold cyan]")
        )

    def update_sidebar(self, agent: str, step: str, tokens: int, cost: float, rules: int):
        """사이드바 정보 업데이트"""
        # Status
        status_text = Text()
        status_text.append(f"Current Agent: ", style="bold")
        status_text.append(f"{agent}\n", style="yellow" if agent != "Idle" else "green")
        status_text.append(f"Current Step: ", style="bold")
        status_text.append(f"{step}\n")
        status_text.append(f"Time: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        self.layout["status"].update(Panel(status_text, title="📡 System Status"))

        # Stats
        stats_table = Table.grid(expand=True)
        stats_table.add_row("Tokens Used:", f"[bold cyan]{tokens:,}[/bold cyan]")
        stats_table.add_row("Est. Cost:", f"[bold green]${cost:.6f}[/bold green]")
        self.layout["stats"].update(Panel(stats_table, title="📊 Usage Stats"))

        # Evolution
        evo_text = Text(f"Active Rules: {rules}", style="bold magenta")
        if rules > 0:
            evo_text.append("\n[LEARNED MODE]", style="blink magenta")
        self.layout["evolution"].update(Panel(evo_text, title="🧬 Evolution"))


    def render(self):
        """현재 상태를 Live UI에 출력할 준비"""
        return self.layout
