from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.console import Group
from gortex.ui.themes.palette import Palette

class WelcomeScreen:
    """Renders the initial welcome screen for Gortex OS.
    
    Displays quick commands, OS status, and a welcome message.
    """
    @staticmethod
    def render(width: int) -> Panel:
        """Renders the welcome screen content.

        Args:
            width (int): Current terminal width.

        Returns:
            Panel: The rendered welcome panel.
        """
        table = Table.grid(expand=True, padding=1)
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        
        # Shortcuts / Tips
        shortcuts = Table(show_header=False, box=box.SIMPLE, border_style=Palette.GRAY)
        shortcuts.add_row(f"[{Palette.YELLOW}]/help[/]", "Show all available OS commands")
        shortcuts.add_row(f"[{Palette.YELLOW}]/clear[/]", "Purge local workspace session")
        shortcuts.add_row(f"[{Palette.YELLOW}]/theme[/]", "Switch visual style profile")
        
        # System Info
        sys_info = Table(show_header=False, box=box.SIMPLE, border_style=Palette.GRAY)
        sys_info.add_row(f"[{Palette.CYAN}]Kernel[/]", "v3.0 (Sovereign)")
        sys_info.add_row(f"[{Palette.CYAN}]Status[/]", f"[bold {Palette.GREEN}]ONLINE[/]")
        sys_info.add_row(f"[{Palette.CYAN}]Memory[/]", "Evolutionary Shards Active")

        table.add_row(
            Panel(shortcuts, title=f" [{Palette.YELLOW}]⚡ Quick Commands[/] ", border_style=Palette.GRAY),
            Panel(sys_info, title=f" [{Palette.CYAN}]🔍 OS Status[/] ", border_style=Palette.GRAY)
        )
        
        welcome_text = Text.assemble(
            ("\nWelcome to Gortex Agent OS.\n", f"bold {Palette.BLUE}"),
            ("Type your objective below to begin the neural orchestration.\n", Palette.GRAY)
        )
        
        return Panel(
            Group(welcome_text, table),
            border_style=Palette.BLUE,
            box=box.DOUBLE,
            padding=(1, 2)
        )
