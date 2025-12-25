
import psutil
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich import box
from gortex.ui.themes.palette import Palette

class SystemMonitor:
    """시스템 리소스 및 에이전트 상태를 실시간으로 모니터링하는 컴포넌트"""

    def __init__(self, console: Console):
        self.console = console
        self.latest_metrics = {}

    def collect_metrics(self, state_vars: dict) -> dict:
        """시스템 상태 및 내부 변수를 수집하여 반환합니다."""
        try:
            # System Metrics
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()

            # Agent State Metrics
            energy = state_vars.get("agent_energy", 0)
            tokens = state_vars.get("total_tokens", 0)
            cost = state_vars.get("total_cost", 0.0)

            self.latest_metrics = {
                "cpu": cpu_usage,
                "memory": mem_info.percent,
                "energy": energy,
                "tokens": tokens,
                "cost": cost
            }
            return self.latest_metrics
        except Exception as e:
            # 오류 발생 시 기본값 반환
            return {
                "cpu": 0.0,
                "memory": 0.0,
                "energy": 0,
                "tokens": 0,
                "cost": 0.0
            }

    def render(self) -> Panel:
        """현재 메트릭을 시각화 패널로 렌더링합니다."""
        if not self.latest_metrics:
            return Panel(Text("Initializing monitoring...", style=Palette.GRAY), title="System Inspector")

        # Layout using Table
        table = Table.grid(expand=True, padding=(0, 2))
        table.add_column(ratio=1)
        table.add_column(ratio=1)

        # 1. System Resources
        cpu_gauge = self._make_gauge(self.latest_metrics.get('cpu', 0), 100, Palette.RED)
        mem_gauge = self._make_gauge(self.latest_metrics.get('memory', 0), 100, Palette.MAGENTA)
        
        # 2. Agent Resources
        energy_gauge = self._make_gauge(self.latest_metrics.get('energy', 0), 100, Palette.GREEN)
        
        info_text = Text.assemble(
            (f"CPU  ", "bold"), (f"{self.latest_metrics.get('cpu',0):.1f}% ", Palette.RED), cpu_gauge, "\n",
            (f"MEM  ", "bold"), (f"{self.latest_metrics.get('memory',0):.1f}% ", Palette.MAGENTA), mem_gauge, "\n",
            (f"NRG  ", "bold"), (f"{self.latest_metrics.get('energy',0)}%   ", Palette.GREEN), energy_gauge
        )

        stats_text = Text.assemble(
            (f"\nTOKENS: ", "bold"), (f"{self.latest_metrics.get('tokens',0):,}", Palette.CYAN),
            (f"\nCOST:   ", "bold"), (f"${self.latest_metrics.get('cost',0):.4f}", Palette.YELLOW),
        )

        table.add_row(info_text, stats_text)

        return Panel(
            table,
            title=f" [bold {Palette.CYAN}]System Inspector[/] ",
            border_style=Palette.CYAN,
            box=box.ROUNDED
        )

    def _make_gauge(self, value, max_value, color, width=20):
        if max_value == 0: return ""
        filled = int((value / max_value) * width)
        filled = max(0, min(filled, width)) # Clamp
        bar = "█" * filled + "░" * (width - filled)
        return Text(bar, style=color)
