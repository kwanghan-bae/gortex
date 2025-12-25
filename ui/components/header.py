from rich.panel import Panel
from rich.text import Text
from rich import box
from datetime import datetime
from gortex.ui.components.ascii_art import SHORT_LOGO, TINY_LOGO, get_ascii_width
from gortex.ui.themes.palette import Palette

class AppHeader:
    """Renders the top header bar for Gortex OS.

    Includes a gradated logo and real-time system status indicators.

    Args:
        width (int): Current terminal width.
        energy (int): Agent OS energy level (0-100).
        provider (str): Active LLM provider name.
    """
    def __init__(self, width: int, energy: int, provider: str):
        self.width = width
        self.energy = energy
        self.provider = provider

    def render(self) -> Panel:
        """Renders the header as a Rich Panel object.

        Returns:
            Panel: The rendered header panel.
        """
        w = self.width if isinstance(self.width, int) else 80
        logo = SHORT_LOGO if w >= 80 else TINY_LOGO
        color = Palette.GREEN if self.energy > 70 else (Palette.YELLOW if self.energy > 30 else Palette.RED)
        
        # Gradient simulation for Logo
        grad_chars = " 🍀 GORTEX Agent OS " if w < 80 else SHORT_LOGO.strip("\n")
        
        # Simple gradient rendering for text
        header_text = Text()
        lines = grad_chars.split("\n")
        colors = Palette.GRADIENT_GORTEX
        
        for i, line in enumerate(lines):
            c = colors[i % len(colors)]
            header_text.append(line + "\n", style=f"bold {c}")
        
        # Status Bar
        energy_val = self.energy if isinstance(self.energy, (int, float)) else 100
        gauge_w = min(40, w // 3)
        filled = int(energy_val/100*gauge_w)
        gauge = "█" * filled + "░" * (gauge_w - filled)
        
        status_line = Text.assemble(
            (f"  {gauge} ", f"bold {color}"),
            (f" {energy_val}% ", f"bold {color}"),
            (f" │ {self.provider} ", f"dim {Palette.GRAY}"),
            (f" │ {datetime.now().strftime('%H:%M:%S')} ", f"italic {Palette.CYAN}")
        )
        
        header_text.append("\n")
        header_text.append(status_line)
        
        return Panel(header_text, border_style=Palette.GRAY, box=box.HORIZONTALS, padding=(0, 1))
