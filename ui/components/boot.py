import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from gortex.ui.themes.palette import Palette
from gortex.ui.components.ascii_art import SHORT_LOGO

class BootManager:
    """Manages the OS boot sequence animation.

    Simulates neural kernel loading and system initialization.

    Args:
        console (Console): The rich console instance to use.
    """
    def __init__(self, console: Console):
        self.console = console

    async def run_sequence(self):
        """Executes the fluid boot sequence with progress bars."""
        """유려한 부팅 시퀀스 실행 (CI 환경에서는 건너뜀)"""
        # CI 환경이나 테스트 환경에서는 출력을 생략
        import os
        if os.getenv("GORTEX_CI") == "true":
            return
            
        self.console.clear()
        
        # 1. Brain/Kernel Loading Simulation
        header = Text(SHORT_LOGO, style=f"bold {Palette.GREEN}")
        self.console.print(header)
        self.console.print(f"\n[bold {Palette.CYAN}]Gortex Agent OS v3.0[/] - [italic {Palette.GRAY}]Neural Kernel Initializing...[/]\n")
        
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, complete_style=Palette.BLUE, finished_style=Palette.GREEN),
            TaskProgressColumn(),
            console=self.console,
            transient=True
        ) as progress:
            
            task1 = progress.add_task(f"[dim {Palette.GRAY}]Loading LLM Adapters...[/]", total=100)
            task2 = progress.add_task(f"[dim {Palette.GRAY}]Scanning Local Memory Shards...[/]", total=100)
            task3 = progress.add_task(f"[dim {Palette.GRAY}]Synchronizing Swarm Protocol...[/]", total=100)
            
            while not progress.finished:
                progress.update(task1, advance=2.5)
                progress.update(task2, advance=1.8)
                progress.update(task3, advance=3.2)
                await asyncio.sleep(0.05)

        # 2. Final Welcome Message
        welcome_panel = Panel(
            Text.assemble(
                ("SYSTEM READY\n\n", f"bold {Palette.GREEN}"),
                ("Gortex OS is now online. ", Palette.FOREGROUND),
                ("All agents are mobilized.", Palette.CYAN)
            ),
            border_style=Palette.BLUE,
            padding=(1, 2)
        )
        self.console.print(welcome_panel)
        time.sleep(1)
        self.console.clear()
