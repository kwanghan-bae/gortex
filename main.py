import os
import json
import asyncio
import time
import logging
import uuid
import re
import argparse
import traceback
import warnings
from typing import Optional

# 불필요한 라이브러리 경고 숨기기
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pkg_resources is deprecated.*")

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich import box
from rich.text import Text

# 자동완성을 위한 prompt_toolkit
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PromptStyle

from gortex.core.state import GortexState
from gortex.core.graph import compile_gortex_graph
from gortex.core.auth import GortexAuth
from gortex.core.commands import handle_command
from gortex.core.engine import GortexEngine
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import ThemeManager
from gortex.ui.components.header import AppHeader
from gortex.ui.themes.palette import Palette
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import estimate_cost
from gortex.utils.tools import deep_integrity_check
from gortex.utils.vocal_bridge import VocalBridge
from gortex.utils.translator import i18n
from gortex.agents.analyst import AnalystAgent
from gortex.ui.components.boot import BootManager

logger = logging.getLogger("GortexMain")
console = Console()

# 자동완성 후보 명령어
COMMANDS = [
    "/help", "/status", "/agents", "/inspect", "/rca", "/search", "/map", 
    "/kg", "/scan_debt", "/index", "/voice", "/language", "/theme", 
    "/config", "/export", "/import", "/clear", "/bug", "/mode", "/save", 
    "/load", "/provider", "/model", "/history"
]

class GortexCommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith('/') and ' ' not in text:
            for cmd in COMMANDS:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text))

command_completer = GortexCommandCompleter()
prompt_session = PromptSession(
    history=FileHistory("logs/input_history.txt"),
    completer=command_completer,
    complete_while_typing=True
)

async def get_user_input(console: Console) -> Optional[str]:
    """사용자 입력을 안전하게 획득 (자동완성 지원)"""
    try:
        style = PromptStyle.from_dict({'prompt': 'ansigreen bold'})
        user_input = await prompt_session.prompt_async("\n👤 You: ", style=style)
        return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input.strip())
    except (KeyboardInterrupt, EOFError):
        return None

def save_sessions_cache(all_sessions_cache: dict):
    try:
        with open("logs/file_cache.json", "w", encoding='utf-8') as f:
            json.dump(all_sessions_cache, f, ensure_ascii=False, indent=2)
    except: pass

async def energy_recovery_loop(state_vars: dict, ui: DashboardUI):
    while True:
        await asyncio.sleep(2)
        if state_vars["agent_energy"] < 100:
            state_vars["agent_energy"] = min(100, state_vars["agent_energy"] + 1)
            ui.energy = state_vars["agent_energy"]

async def trend_scout_loop(ui: DashboardUI):
    from gortex.agents.trend_scout import TrendScoutAgent
    scout = TrendScoutAgent()
    while True:
        await asyncio.sleep(1)
        interval = int(os.getenv("TREND_SCAN_INTERVAL_HOURS", "24"))
        if scout.should_scan(interval):
            try:
                notifications = await scout.scan_trends()
                for msg in notifications: ui.add_achievement(f"Trend: {msg}")
            except: pass
        await asyncio.sleep(3600)

async def run_gortex():
    # [CLI ARGS]
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["gemini", "ollama", "openai"])
    parser.add_argument("--setup", action="store_true")
    args, _ = parser.parse_known_args()

    ui = DashboardUI(console)
    auth = GortexAuth()
    
    # [OS BOOT]
    boot = BootManager(console)
    await boot.run_sequence()

    if args.provider: auth.set_provider(args.provider)
    
    # 설정 파일이 없거나 --setup 인자가 있으면 초기 설정 실행
    if not os.path.exists(auth._CONFIG_PATH) or args.setup:
        console.clear()
        setup_header = AppHeader(console.width, 100, "INITIALIZING")
        console.print(setup_header.render())
        console.print(f"\n[bold {Palette.YELLOW}]🛠️ Gortex Agent OS Setup[/]\n")
        
        console.print(f"[{Palette.CYAN}]1.[/] Gemini (API Key required)")
        console.print(f"[{Palette.CYAN}]2.[/] Ollama (Local LLM)")
        
        try:
            choice = console.input(f"\n[bold {Palette.GREEN}]Select Provider (1/2): [/]")
            if choice == "2":
                auth.set_provider("ollama")
                if not auth.list_ollama_models():
                    confirm = console.input(f"\n[bold {Palette.YELLOW}]Ollama models missing. Pull recommended stack? (y/N): [/]")
                    if confirm.lower() in ['y', 'yes', 'ㅇㅇ']:
                        auth.pull_recommended_stack()
            else:
                auth.set_provider("gemini")
        except (KeyboardInterrupt, EOFError):
            pass

    observer = GortexObserver()
    engine = GortexEngine(ui, observer, VocalBridge())
    workflow = compile_gortex_graph()
    thread_id = str(uuid.uuid4())[:8]
    
    state_vars = {"agent_energy": 100, "total_tokens": 0, "total_cost": 0.0, "session_cache": {}}
    working_dir = os.getenv("WORKING_DIR", "./workspace")
    os.makedirs(working_dir, exist_ok=True)

    # 태스크 시작
    asyncio.create_task(energy_recovery_loop(state_vars, ui))
    asyncio.create_task(trend_scout_loop(ui))

    current_task = None

    async def execute_workflow(user_input):
        nonlocal current_task
        ui.chat_history.append(("user", user_input))
        initial_state = {
            "messages": [("user", user_input)],
            "working_dir": working_dir,
            "file_cache": state_vars["session_cache"],
            "agent_energy": state_vars["agent_energy"]
        }
        try:
            async for event in workflow.astream(initial_state, config={"configurable": {"thread_id": thread_id}}):
                for node_name, output in event.items():
                    ui.update_sidebar(agent=node_name, step="Processing", provider=auth.get_provider())
                    
                    tokens = await engine.process_node_output(node_name, output, state_vars)
                    state_vars["total_tokens"] += tokens
                    state_vars["total_cost"] += estimate_cost(tokens)
                    
                    # [FIX] 즉시 UI 반영하여 응답성 확보
                    ui.update_main(ui.chat_history)
                    ui.update_sidebar(agent="Idle", step="Ready", tokens=state_vars["total_tokens"], cost=state_vars["total_cost"])
        except Exception as e:
            ui.chat_history.append(("system", f"❌ Execution Error: {str(e)}"))
        finally:
            current_task = None

    # [LIVE UI] Perfect Full-screen Experience
    # [Fix] Input Blocking Issue: screen=False로 변경하고 입력 중에는 리프레시 중단
    with Live(ui.layout, console=console, refresh_per_second=4, screen=False) as live:
        while True:
            live.stop() # 입력 프롬프트를 위해 잠시 렌더링 중단 (커서 뺏김 방지)
            try:
                user_input = await get_user_input(console)
            finally:
                live.start() # 입력 완료/취소 후 다시 렌더링 재개
            
            if user_input is None: break
            if not user_input: continue
            
            if user_input.startswith("/"):
                # [Fix] ConfigUI 등 TUI 충돌 방지를 위해 리턴값 처리
                cmd_result = await handle_command(user_input, ui, observer, {}, thread_id, None)
                if cmd_result == "config_ui":
                    live.stop()
                    try:
                        from gortex.ui.components.config_manager import ConfigManagerUI
                        config_ui = ConfigManagerUI(console)
                        config_ui.run_menu()
                    except Exception as e:
                        ui.chat_history.append(("system", f"❌ Config UI Error: {e}"))
                    finally:
                        live.start()
                        ui.update_main(ui.chat_history) # 복귀 후 화면 갱신
                
                # [Fix] Force refresh after command execution
                live.refresh()
                continue
            
            if current_task and not current_task.done():
                ui.chat_history.append(("system", "⏳ Busy..."))
                continue
                
            current_task = asyncio.create_task(execute_workflow(user_input))

if __name__ == "__main__":
    try:
        asyncio.run(run_gortex())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        from rich.markup import escape
        print(f"\nFatal Error: {escape(str(e))}")
