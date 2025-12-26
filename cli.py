import typer
import os
import sys
import asyncio
from rich.console import Console
from rich.prompt import Prompt

from gortex.config.settings import settings
from gortex.core.system import GortexSystem

app = typer.Typer(
    help="Gortex: Advanced AI Agent System",
    add_completion=False,
    no_args_is_help=True
)
console = Console()

@app.command()
def start():
    """
    Start the Gortex master system (TUI + Core).
    """
    if not os.path.exists(".env"):
        console.print("[bold yellow]⚠️  No .env file found. Running init first...[/bold yellow]")
        init(force=False)

    try:
        system = GortexSystem()
        asyncio.run(system.run())
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Goodbye![/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]❌ Critical Error: {e}[/bold red]")
        sys.exit(1)

@app.command()
def worker():
    """
    Start a distributed worker node.
    """
    console.print("[bold green]🚀 Starting Gortex Distributed Worker...[/bold green]")
    try:
        from scripts.gortex_worker import main as worker_main
        asyncio.run(worker_main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Worker shutting down.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Worker Error: {e}[/bold red]")

@app.command()
def dashboard(
    port: int = typer.Option(8000, help="Port to run the API server on")
):
    """
    Start the Gortex Web API & Dashboard server.
    """
    console.print(f"[bold blue]📡 Starting Gortex Web API on port {port}...[/bold blue]")
    try:
        from gortex.core.web_api import start_web_server
        asyncio.run(start_web_server(port=port))
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Dashboard shutting down.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ Dashboard Error: {e}[/bold red]")

@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .env file")
):
    """
    Initialize the Gortex environment (create .env, install dependencies).
    """
    if os.path.exists(".env") and not force:
        console.print("[yellow]ℹ️  .env file already exists. Use --force to overwrite.[/yellow]")
        return

    console.print("[bold blue]🚀 Initializing Gortex Environment...[/bold blue]")

    api_key_1 = Prompt.ask("Enter Primary Gemini API Key", password=True)
    api_key_2 = Prompt.ask("Enter Secondary Gemini API Key (Optional)", password=True, default="")

    env_content = f"""GEMINI_API_KEY_1={api_key_1}
GEMINI_API_KEY_2={api_key_2}
WORKING_DIR=./workspace
LOG_LEVEL=INFO
MAX_CODER_ITERATIONS=30
TREND_SCAN_INTERVAL_HOURS=24
"""

    with open(".env", "w") as f:
        f.write(env_content)

    console.print("[green]✅ .env file created.[/green]")

    # Check for playwright
    console.print("[blue]🌐 Checking browser engine...[/blue]")
    try:
        import playwright
        # We assume if package is there, browsers might need install.
        # Running the install command is safer.
        console.print("[dim]Running playwright install...[/dim]")
        os.system("playwright install chromium")
        console.print("[green]✅ Browser engine ready.[/green]")
    except ImportError:
        console.print("[red]❌ Playwright not installed. Please run `pip install playwright`[/red]")

@app.command()
def config():
    """
    Show current configuration.
    """
    console.print(settings.model_dump())

@app.command()
def inherit(
    seed_path: str = typer.Argument(..., help="Path to the Neural Seed (.zip) to inherit from")
):
    """
    Inherit intelligence from a Neural Seed package.
    (Imports rules, tools, and specialist agents)
    """
    if not os.path.exists(seed_path):
        console.print(f"[bold red]❌ Seed file not found: {seed_path}[/bold red]")
        return

    console.print(f"[bold magenta]🌌 Inheriting Intelligence from {os.path.basename(seed_path)}...[/bold magenta]")
    
    import zipfile
    try:
        with zipfile.ZipFile(seed_path, 'r') as zipf:
            # 1. 지식 복원
            for f in zipf.namelist():
                if f.startswith("memory/"):
                    zipf.extract(f, path=".")
                if f == "tools/forged.py":
                    zipf.extract(f, path="gortex/core/")
                if f.startswith("agents/"):
                    zipf.extract(f, path=".")
            
            console.print("[green]✅ Experience shards and forged tools inherited.[/green]")
            console.print("[green]✅ Specialist agents recruited from seed.[/green]")
            console.print("[bold cyan]🚀 Intelligence transplant complete. Run 'gortex start' to begin.[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]❌ Inheritance failed: {e}[/bold red]")

if __name__ == "__main__":
    app()
