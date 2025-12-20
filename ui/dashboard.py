from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.json import JSON
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from gortex.utils.table_detector import try_render_as_table
from datetime import datetime
import json

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
        Layout(name="status", size=8),
        Layout(name="stats", size=8),
        Layout(name="evolution", size=8),
        Layout(name="logs")
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
        self.recent_logs = []
        
        # Progress bar for tools
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True
        )
        self.tool_task = None

        # 에이전트별 색상 매핑
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
        
        # 에이전트별 애니메이션 스타일 매핑
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
                # 도구 실행 결과 (Observation) 요약 및 시각화 처리
                if isinstance(content, str):
                    display_content = content
                    if len(content) > 2000:
                        display_content = content[:1000] + f"\n\n[... {len(content)-2000} characters truncated ...]\n\n" + content[-1000:]
                    
                    # 1. JSON 검사
                    try:
                        stripped = display_content.strip()
                        if (stripped.startswith("{}") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                            json.loads(stripped)
                            renderable = JSON(stripped)
                            msg_group.append(Panel(renderable, title="🛠️ [bold yellow]Observation (JSON)[/bold yellow]", border_style="yellow", style="dim"))
                            continue
                    except:
                        pass

                    # 2. 테이블 형식 검사
                    table_renderable = try_render_as_table(display_content)
                    if table_renderable:
                        msg_group.append(Panel(table_renderable, title="🛠️ [bold yellow]Observation (Table)[/bold yellow]", border_style="yellow", style="dim"))
                        continue

                    # 3. 코드 형태인 경우 하이라이팅
                    if any(x in display_content for x in ["import ", "def ", "class ", "void ", "public ", "{", "}", "const ", "SELECT ", "INSERT "]):
                        lang = "python"
                        if "SELECT " in display_content: lang = "sql"
                        elif "void " in display_content: lang = "java"
                        
                        syntax_content = Syntax(display_content, lang, theme="monokai", line_numbers=True, word_wrap=True)
                        msg_group.append(Panel(syntax_content, title=f"🛠️ [bold yellow]Observation ({lang})[/bold yellow]", border_style="yellow", style="dim"))
                    else:
                        msg_group.append(Panel(display_content, title="🛠️ [bold yellow]Observation[/bold yellow]", border_style="yellow", style="dim"))
                else:
                    # 문자열이 아닌 경우 (예: 이미 Rich 객체인 경우)
                    msg_group.append(Panel(content, title="🛠️ [bold yellow]Observation[/bold yellow]", border_style="yellow", style="dim"))
            elif role == "system":
                # 시스템 메시지도 Rich 객체 지원
                if isinstance(content, str):
                    msg_group.append(Text(f"⚙️ {content}", style="dim white"))
                else:
                    msg_group.append(content)
        
        self.layout["main"].update(
            Panel(Group(*msg_group), title="[bold cyan]🧠 Gortex Terminal[/bold cyan]")
        )

    def update_thought(self, thought: str, agent_name: str = "agent"):
        """에이전트의 사고 과정 실시간 업데이트 (시각 효과 추가)"""
        self.agent_thought = thought
        
        # 에이전트별 색상 적용
        style = self.agent_colors.get(agent_name.lower(), "agent.manager")
        title = f"💭 [{style}]Agent reasoning ({agent_name})[/{style}]"
        # 테두리 색상은 cyan으로 고정 (가독성 목적)
        self.layout["thought"].update(
            Panel(Text(thought, style="italic cyan"), title=title, border_style="cyan")
        )

    def update_logs(self, log_entry: dict):
        """최근 로그 업데이트"""
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 5:
            self.recent_logs.pop(0)
            
        log_table = Table.grid(expand=True)
        for entry in self.recent_logs:
            agent = entry.get("agent", "Sys")
            event = entry.get("event", "event")
            style = self.agent_colors.get(agent.lower(), "dim white")
            log_table.add_row(f"[{style}]{agent}[/{style}]", f"[dim]{event}[/dim]")
            
        self.layout["logs"].update(Panel(log_table, title="📜 Trace Logs"))

    def reset_thought_style(self):
        """사고 패널의 스타일을 평상시로 복구"""
        if self.agent_thought:
            self.layout["thought"].update(
                Panel(Text(self.agent_thought, style="italic cyan"), title="💭 [bold cyan]Agent reasoning[/bold cyan]", border_style="cyan")
            )

    def complete_thought_style(self):
        """사고 완료 시 시각 효과 (녹색 강조)"""
        if self.agent_thought:
            self.layout["thought"].update(
                Panel(Text(self.agent_thought, style="italic green"), title="✅ [bold green]Thought complete[/bold green]", border_style="green")
            )

    def start_tool_progress(self, description: str):
        """도구 실행 진행 바 시작"""
        if self.tool_task is None:
            self.tool_task = self.progress.add_task(description, total=None)
        else:
            self.progress.update(self.tool_task, description=description)

    def stop_tool_progress(self):
        """도구 실행 진행 바 중단"""
        if self.tool_task is not None:
            self.progress.remove_task(self.tool_task)
            self.tool_task = None

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
        agent_style = self.agent_colors.get(agent.lower(), "dim white")
        status_text.append(f"{agent}\n", style=agent_style if agent != "Idle" else "green")
        status_text.append(f"Step: ", style="bold")
        status_text.append(f"{step}\n")
        status_text.append(f"Time: {datetime.now().strftime('%H:%M:%S')}", style="dim")
        
        status_group = [status_text]
        if agent != "Idle":
            spinner_style = self.agent_spinners.get(agent.lower(), "dots")
            status_group.append(Spinner(spinner_style, text=f"[{agent_style}]{agent} is active[/{agent_style}]"))

        self.layout["status"].update(Panel(Group(*status_group), title="📡 System Status"))

        # Stats
        stats_table = Table.grid(expand=True)
        stats_table.add_row("Tokens:", f"[bold cyan]{tokens:,}[/bold cyan]")
        stats_table.add_row("Cost:", f"[bold green]${cost:.6f}[/bold green]")
        
        stats_group = [stats_table]
        if self.tool_task is not None:
            stats_group.append(Text("\n"))
            stats_group.append(self.progress)

        self.layout["stats"].update(Panel(Group(*stats_group), title="📊 Usage Stats"))

        # Evolution
        evo_text = Text(f"Active Rules: {rules}\n", style="bold magenta")
        if rules > 0:
            evo_text.append("[LEARNED MODE]", style="blink magenta")
        self.layout["evolution"].update(Panel(evo_text, title="🧬 Evolution"))

    def render(self):
        return self.layout