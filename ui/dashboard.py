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
        Layout(name="evolution", size=8),
        Layout(name="debt", size=10), # Technical Debt Panel
        Layout(name="logs")
    )
    return layout

class DashboardUI:
    def __init__(self, console: Console):
        self.console = console
        self.assets = SynapticAssetManager()
        self.layout = create_layout()
        self.chat_history = []
        self.agent_thought = ""
        self.thought_tree = [] # 사고 과정 트리 데이터
        self.current_diagram = "" # 아키텍처 다이어그램 코드
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
        self.achievements = [] # 주요 마일스톤 성과 기록
        self.security_events = [] # 보안 이벤트 기록
        self.thought_timeline = [] # 타임라인 스냅샷 기록
        self.activity_stream = [] # 저널 스타일 활동 일지
        self.review_board = {} # 에이전트 승인 현황 관리
        self.debt_list = [] # 기술 부채(복잡도) 목록
        
        # Progress bar for tools
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=None),
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

        # Web Streaming support
        self.web_manager = None
        try:
            from gortex.ui.web_server import manager
            self.web_manager = manager
        except ImportError:
            pass

    def _generate_thought_graph(self) -> Dict[str, Any]:
        """사고 트리를 그래프(Nodes/Edges) 구조로 변환"""
        nodes = []
        edges = []
        for item in self.thought_tree:
            node_id = item.get("id")
            nodes.append({
                "id": node_id,
                "label": item.get("text")[:30] + "..." if len(item.get("text", "")) > 30 else item.get("text"),
                "full_text": item.get("text"),
                "type": item.get("type", "analysis")
            })
            if item.get("parent_id"):
                edges.append({"from": item["parent_id"], "to": node_id})
        return {"nodes": nodes, "edges": edges}

    async def _broadcast_to_web(self):
        """현재 UI 상태를 웹 대시보드로 전송"""
        if not self.web_manager:
            return
            
        from gortex.ui.three_js_bridge import ThreeJsBridge
        bridge_3d = ThreeJsBridge()
        
        state = {
            "agent": self.current_agent,
            "step": self.current_step,
            "tokens": self.tokens_used,
            "cost": self.total_cost,
            "provider": self.provider,
            "call_count": self.call_count,
            "energy": self.energy,
            "efficiency": self.efficiency,
            "thought": self.agent_thought,
            "thought_tree": self.thought_tree,
            "thought_tree_3d": bridge_3d.convert_thought_to_3d(self.thought_tree), # 3D 신경망 추가
            "thought_graph": self._generate_thought_graph(), # 마인드맵용 그래프 데이터 추가
            "diagram": self.current_diagram,
            "achievements": self.achievements,
            "security": self.security_events, # 보안 이벤트 추가
            "activity": self.activity_stream, # 활동 일지 추가
            "review": self.review_board, # 리뷰 현황 추가
            "debt": self.debt_list, # 기술 부채 추가
            "chat_history": [
                (r, c if isinstance(c, str) else "[Rich Object]") 
                for r, c in self.chat_history[-10:]
            ]
        }
        try:
            await self.web_manager.broadcast(json.dumps(state, ensure_ascii=False))
        except:
            pass

    def update_debt_panel(self, debt_list: list):
        """기술 부채(복잡도) 패널 업데이트"""
        self.debt_list = debt_list
        if not debt_list:
            self.layout["debt"].update(Panel("No debt scanned.", title="📉 TECHNICAL DEBT", border_style="dim"))
            return

        table = Table.grid(expand=True)
        for item in debt_list[:5]: # 상위 5개만 표시
            file_name = item.get("file", "").split("/")[-1]
            score = item.get("score", 0)
            color = "red" if score > 50 else ("yellow" if score > 20 else "green")
            table.add_row(f"{file_name}", f"[{color}]{score}[/{color}]")
            
        self.layout["debt"].update(Panel(table, title="📉 [bold red]TECHNICAL DEBT[/]", border_style="red"))

    def update_main(self, messages: list):
        """메인 채팅 패널 업데이트 (역할별 구분 및 자동 요약 표시)"""
        if len(messages) > 50:
            del messages[:-50]

        display_msgs = messages[-15:]
        msg_group = []
        
        if len(messages) > 15:
            msg_group.append(Text(f"⬆️ (이전 대화 기록은 /logs 또는 /history로 확인 가능)", style="dim white italic", justify="center"))

        for role, content in display_msgs:
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
                    
                    # 1. JSON 검사
                    try:
                        stripped = display_content.strip()
                        if (stripped.startswith("{}") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                            json.loads(stripped)
                            renderable = JSON(stripped)
                            msg_group.append(Panel(renderable, title=f"{icon} [bold yellow]OBSERVATION (JSON)[/bold yellow]", border_style="yellow", style="dim"))
                            continue
                    except:
                        pass

                    # 2. 테이블 형식 검사
                    table_renderable = try_render_as_table(display_content)
                    if table_renderable:
                        msg_group.append(Panel(table_renderable, title=f"{icon} [bold yellow]OBSERVATION (TABLE)[/bold yellow]", border_style="yellow", style="dim"))
                        continue

                    # 3. 코드 형태인 경우 하이라이팅
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
        
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def update_thought(self, thought: str, agent_name: str = "agent", tree: list = None):
        """에이전트의 사고 과정 실시간 업데이트 (타임라인 스냅샷 포함)"""
        self.agent_thought = thought
        if tree:
            self.thought_tree = tree
        
        timestamp = datetime.now().isoformat()
        self.thought_history.append((agent_name, thought, timestamp))
        
        # [TIMELINE] 현재 상태 스냅샷 저장
        snapshot = {
            "timestamp": timestamp,
            "agent": agent_name,
            "thought": thought,
            "tree": self.thought_tree,
            "diagram": self.current_diagram,
            "step": self.current_step
        }
        self.thought_timeline.append(snapshot)
        if len(self.thought_timeline) > 50: # 최대 50개 유지
            self.thought_timeline.pop(0)

        style = self.agent_colors.get(agent_name.lower(), "agent.manager")
        title = f"💭 [{style}]AGENT REASONING ({agent_name.upper()})[/{style}]"
        self.layout["thought"].update(Panel(Text(thought, style="italic cyan"), title=title, border_style="cyan", padding=(1, 2)))
        
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def update_logs(self, log_entry: dict):
        """최근 로그 업데이트 (최신 항목 하이라이트)"""
        self.recent_logs.append(log_entry)
        if len(self.recent_logs) > 8:
            self.recent_logs.pop(0)
            
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

    def reset_thought_style(self):
        """사고 패널의 스타일을 평상시로 복구"""
        if self.agent_thought:
            self.layout["thought"].update(
                Panel(Text(self.agent_thought, style="italic cyan"), title="💭 [bold cyan]AGENT REASONING[/bold cyan]", border_style="cyan", padding=(1, 2))
            )

    def complete_thought_style(self):
        """사고 완료 시 시각 효과 (녹색 강조)"""
        if self.agent_thought:
            self.layout["thought"].update(
                Panel(Text(self.agent_thought, style="italic green"), title="✅ [bold green]THOUGHT COMPLETE[/bold green]", border_style="green", padding=(1, 2))
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

    def update_sidebar(self, agent: str, step: str, tokens: int, cost: float, rules: int, provider: str = "GEMINI", call_count: int = 0, avg_latency: int = 0, energy: int = 100, efficiency: float = 100.0):
        """사이드바 정보 업데이트 (에이전트, LLM, 성능 상태 및 에너지/효율성 시각화)"""
        self.current_agent = agent
        self.current_step = step
        self.tokens_used = tokens
        self.total_cost = cost
        self.active_rules_count = rules
        self.provider = provider
        self.call_count = call_count
        self.energy = energy
        self.efficiency = efficiency
        
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

        agent_style_name = self.agent_colors.get(agent.lower(), "dim white")
        try:
            border_color = self.console.get_style(agent_style_name).color.name
        except:
            border_color = "cyan" if agent != "Idle" else "white"

        # Status
        status_text = Text()
        status_text.append(f"Agent: ", style="bold")
        agent_style = self.agent_colors.get(agent.lower(), "dim white")
        agent_label = self.assets.get_agent_label(agent)
        status_text.append(f"{agent_label}\n", style=agent_style if agent != "Idle" else "green")
        status_text.append(f"LLM  : ", style="bold")
        provider_style = "bold blue" if provider == "GEMINI" else "bold green"
        status_text.append(f"{provider}\n", style=provider_style)
        
        # 호출 빈도 시각화
        status_text.append(f"Load : ", style="bold")
        bars = min(10, (call_count + 1) // 2)
        load_color = "green" if bars < 4 else ("yellow" if bars < 8 else "red")
        status_text.append("█" * bars, style=load_color)
        status_text.append("░" * (10 - bars), style="dim")
        status_text.append(f" ({call_count}/min)\n", style="dim")

        status_text.append(f"Step : ", style="bold")
        status_text.append(f"{step}\n")
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
        stats_table.add_row("Energy:", f"[{energy_color}]{'⚡' * (energy // 20)}{' ' * (5 - energy // 20)} {energy}%[/{energy_color}]")
        
        eff_color = "cyan" if efficiency >= 80 else ("yellow" if efficiency >= 50 else "red")
        stats_table.add_row("Effic.:", f"[{eff_color}]{efficiency:.1f}[/{eff_color}]")
        
        stats_group = [stats_table]
        if self.tool_task is not None:
            stats_group.append(Text("\n"))
            stats_group.append(self.progress)

        self.layout["stats"].update(Panel(Group(*stats_group), title=f"📊 [bold {border_color}]USAGE STATS[/]", border_style="green" if tokens > 0 else border_color))

        # Evolution
        evo_text = Text(f"Active Rules: {rules}\n", style="bold magenta")
        if rules > 0:
            evo_text.append("[LEARNED MODE]", style="blink magenta")
        self.layout["evolution"].update(Panel(evo_text, title=f"🧬 [bold {border_color}]EVOLUTION[/]", border_style="magenta" if rules > 0 else border_color))

    def add_achievement(self, text: str, icon: str = "🏆"):
        """새로운 성과(마일스톤)를 타임라인에 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.achievements.append({
            "time": timestamp,
            "text": text,
            "icon": icon
        })
        # 최신 5개만 보존 고려 가능하나, 여기서는 전체 보존
        logger.info(f"✨ Achievement Unlocked: {text}")
        
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def filter_thoughts(self, agent_name: str = None, keyword: str = None) -> list:
        """사고 히스토리를 필터링하여 반환"""
        results = self.thought_history
        if agent_name:
            results = [t for t in results if t[0].lower() == agent_name.lower()]
        if keyword:
            results = [t for t in results if keyword.lower() in t[1].lower()]
        return results

    def add_security_event(self, event_type: str, details: str):
        """보안 관련 이벤트(차단 등)를 기록"""
        self.security_events.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": event_type,
            "details": details
        })
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def add_journal_entry(self, entry: str):
        """저널 스타일 활동 항목 추가"""
        self.activity_stream.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "content": entry
        })
        if len(self.activity_stream) > 20:
            self.activity_stream.pop(0)
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def update_review_board(self, task_id: str, agent_name: str, approved: bool, feedback: str):
        """다중 에이전트 승인 현황 업데이트"""
        if task_id not in self.review_board:
            self.review_board[task_id] = {"title": task_id, "approvals": {}}
            
        self.review_board[task_id]["approvals"][agent_name] = {
            "approved": approved,
            "feedback": feedback,
            "time": datetime.now().strftime("%H:%M:%S")
        }
        if self.web_manager:
            asyncio.create_task(self._broadcast_to_web())

    def render(self):
        return self.layout
