import asyncio
import logging
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.panel import Panel

from gortex.core.engine import GortexEngine
from gortex.core.state import GortexState
from gortex.core.tools.editor import ReplaceFileContentTool

# --- UI Adapter ---
class CliAdapterUI:
    def __init__(self, console: Console):
        self.console = console
        self.chat_history = []
        self.current_agent = "User"
        self.layout = None # Not used

    def update_energy_visualizer(self, energy: int):
        pass # Optional for CLI

    def add_achievement(self, text: str):
        self.console.print(f"[bold yellow]🏆 {text}[/bold yellow]")

    def update_thought(self, text: str, agent_name: str = "System"):
        self.console.print(f"[dim]{agent_name}: {text}[/dim]")

    def set_mode(self, mode: str):
        self.console.print(f"[bold blue]Mode switched to: {mode}[/bold blue]")

    def update_logs(self, log_entry: Dict[str, Any]):
        pass # Keep logs silent in CLI unless verbose

    def update_main(self, history: List[Any]):
        # In CLI, we print incrementally, so this might be redundant if engine calls it frequently.
        # But engine calls it after processing node output.
        # We can ignore this or print the last message if not printed.
        pass

    def add_security_event(self, level: str, msg: str):
        self.console.print(f"[bold red]🚨 {level}: {msg}[/bold red]")
        
    def update_sidebar(self, agent, step):
        pass
        
    def update_economy_panel(self, data):
        pass

# --- Safety Patching ---
def patch_tools_for_safety(console: Console):
    original_replace = ReplaceFileContentTool.execute

    def safe_replace(self, path: str, target_content: str, replacement_content: str) -> str:
        console.print(Panel(f"File: {path}\n\n[red]- {target_content[:100]}...[/red]\n[green]+ {replacement_content[:100]}...[/green]", title="[bold red]Tool Request: Replace Content[/bold red]"))
        if Confirm.ask("Allow this change?", default=False):
            return original_replace(self, path, target_content, replacement_content)
        else:
            return "❌ Error: User refused execution."

    ReplaceFileContentTool.execute = safe_replace
    console.print("[dim]🔒 Safety protocols engaged: specific tools are now guarded.[/dim]")

# --- REPL Loop ---
async def run_repl():
    console = Console()
    ui = CliAdapterUI(console)
    
    # [Zero-Config] API Key Check
    from gortex.config.settings import settings
    if not settings.GEMINI_API_KEY_1 and not settings.OPENAI_API_KEY:
        # Check environment variables directly as fallback
        import os
        if not os.getenv("GEMINI_API_KEY_1") and not os.getenv("OPENAI_API_KEY"):
            console.print(Panel("[bold yellow]⚠️  No Cloud API Keys Detected[/bold yellow]\nGortex will run in [bold cyan]Local Mode (Ollama)[/bold cyan] unless you provide a key.", title="Configuration Check"))
            if Confirm.ask("Would you like to provide a Gemini API Key for better performance?", default=True):
                key = Prompt.ask("Enter Gemini API Key", password=True)
                if key:
                    settings.GEMINI_API_KEY_1 = key
                    console.print("[green]✅ Key loaded into memory.[/green]")
            else:
                console.print("[dim]Using local models only.[/dim]")

    # Init Engine
    console.print("[bold green]🧠 Gortex CLI v1.0 (Awakened)[/bold green]")
    engine = GortexEngine(ui=ui)
    
    # Patch Tools
    patch_tools_for_safety(console)

    console.print("[dim]Type '/exit' to quit, '/add <file>' to load context.[/dim]")

    # Initial Context
    state: GortexState = {
        "messages": [],
        "pinned_messages": [],
        "plan": [],
        "current_step": 0,
        "working_dir": ".",
        "file_cache": {},
        "agent_energy": 100,
        "api_call_count": 0,
        "token_credits": {},
        "agent_economy": {},
        "risk_score": 0.5
    }

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]➜[/bold green]")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ("/exit", "/quit", "exit"):
                console.print("👋 Goodbye.")
                break
                
            if user_input.startswith("/add "):
                file_path = user_input[5:].strip()
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                    state["file_cache"][file_path] = content
                    console.print(f"[green]✅ Added {file_path} to context ({len(content)} chars)[/green]")
                except Exception as e:
                    console.print(f"[red]❌ Failed to read file: {e}[/red]")
                continue
                
            if user_input == "/clear":
                state["messages"] = []
                state["file_cache"] = {}
                console.print("[yellow]🧹 Context cleared.[/yellow]")
                continue

            # Run Engine
            console.print("[dim]Thinking...[/dim]")
            result_state = await engine.run_async(user_input, initial_state=state)
            
            # Update local state with result
            # Note: GortexEngine.run returns the final state, but we should merge it carefully.
            # Especially 'messages'.
            state = result_state 
            
            # Print AI Response
            # We look for the last message from AI
            messages = state.get("messages", [])
            if messages and isinstance(messages[-1], (tuple, list)) and messages[-1][0] == "ai":
                console.print(Markdown(str(messages[-1][1])))
            elif messages and hasattr(messages[-1], 'content'): # LangChain message object
                console.print(Markdown(messages[-1].content))

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type /exit to quit.[/yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")
