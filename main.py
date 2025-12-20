import os
import asyncio
import random
import logging
import json
import shutil
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

from gortex.core.graph import compile_gortex_graph
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import GORTEX_THEME
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import count_tokens, estimate_cost

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GortexMain")

load_dotenv()

async def get_user_input(console: Console):
    """비차단 방식으로 사용자 입력을 받음"""
    return await asyncio.get_event_loop().run_in_executor(None, console.input, "[bold green]User > [/bold green]")

async def handle_command(user_input: str, ui: DashboardUI, observer: GortexObserver) -> str:
    """'/'로 시작하는 명령어를 처리합니다. 반환값에 따라 메인 루프의 행동을 결정합니다."""
    cmd_parts = user_input.lower().strip().split()
    cmd = cmd_parts[0]
    
    if cmd == "/clear":
        ui.chat_history = []
        ui.update_main([])
        ui.update_thought("Chat history cleared.")
        return "skip"
    
    elif cmd == "/history":
        ui.chat_history.append(("system", "현재 세션의 대화 내역이 유지되고 있습니다."))
        ui.update_main(ui.chat_history)
        return "skip"
        
    elif cmd == "/radar":
        if os.path.exists("tech_radar.json"):
            with open("tech_radar.json", "r") as f:
                radar = json.load(f)
                ui.chat_history.append(("system", f"Tech Radar: {json.dumps(radar, indent=2, ensure_ascii=False)}"))
        else:
            ui.chat_history.append(("system", "Tech Radar 데이터가 없습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/log":
        log_path = "logs/trace.jsonl"
        if os.path.exists(log_path):
            try:
                index = int(cmd_parts[1]) if len(cmd_parts) > 1 else -1
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    total_logs = len(lines)
                    
                    if total_logs == 0:
                        ui.chat_history.append(("system", "기록된 로그가 없습니다."))
                    elif -total_logs <= index < total_logs:
                        actual_idx = index if index >= 0 else total_logs + index
                        entry = json.loads(lines[actual_idx])
                        
                        from rich.json import JSON
                        from rich.columns import Columns
                        
                        # 메타데이터와 페이로드 분리 표시
                        meta_text = Text.assemble(
                            ("TIME: ", "bold white"), (entry.get("timestamp", "").split("T")[-1][:8], "cyan"), "\n",
                            ("AGENT: ", "bold white"), (entry.get("agent", "Unknown").upper(), "magenta"), "\n",
                            ("EVENT: ", "bold white"), (entry.get("event", ""), "yellow")
                        )
                        
                        detail_panel = Panel(
                            Group(
                                Panel(meta_text, title="Metadata", border_style="dim"),
                                Panel(JSON(json.dumps(entry.get("payload", {}), ensure_ascii=False)), title="Payload", border_style="blue")
                            ),
                            title=f"🔍 LOG DETAIL [#{actual_idx}]", 
                            border_style="magenta"
                        )
                        ui.chat_history.append(("system", detail_panel))
                    else:
                        ui.chat_history.append(("system", f"인덱스 범위를 벗어났습니다. (현재 0 ~ {total_logs-1})"))
            except (ValueError, IndexError):
                ui.chat_history.append(("system", "사용법: /log [index]"))
        else:
            ui.chat_history.append(("system", "로그 파일이 존재하지 않습니다."))
        ui.update_main(ui.chat_history)
        return "skip"



    elif cmd == "/summarize":
        ui.chat_history.append(("system", "수동 요약을 요청하셨습니다. 다음 실행 시 요약이 수행됩니다."))
        ui.update_main(ui.chat_history)
        return "summarize"

    elif cmd == "/logs":
        log_path = "logs/trace.jsonl"
        if os.path.exists(log_path):
            try:
                # /logs [skip] [limit] 파싱
                skip = int(cmd_parts[1]) if len(cmd_parts) > 1 else 0
                limit = int(cmd_parts[2]) if len(cmd_parts) > 2 else 10
                
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    total_lines = len(lines)
                    
                    # 최신순 페이징 계산
                    end_idx = max(0, total_lines - skip)
                    start_idx = max(0, end_idx - limit)
                    
                    recent_lines = lines[start_idx:end_idx]
                    recent_logs = [json.loads(line) for line in recent_lines]
                    
                    log_table = Table(title=f"Trace Logs (Page: {start_idx}~{end_idx-1} / Total: {total_lines})", show_header=True, header_style="bold magenta")
                    log_table.add_column("Idx", style="dim", justify="right")
                    log_table.add_column("Time", style="dim")
                    log_table.add_column("Agent", style="cyan")
                    log_table.add_column("Event")
                    
                    # 표시도 최신순(역순)으로
                    for i, entry in enumerate(reversed(recent_logs)):
                        actual_line_idx = end_idx - 1 - i
                        ts = entry.get("timestamp", "").split("T")[-1][:8]
                        log_table.add_row(str(actual_line_idx), ts, entry.get("agent", ""), entry.get("event", ""))
                    
                    ui.chat_history.append(("system", log_table))
            except (ValueError, IndexError):
                ui.chat_history.append(("system", "사용법: /logs [skip] [limit] (예: /logs 10 5)"))
        else:
            ui.chat_history.append(("system", "로그 파일이 존재하지 않습니다."))
        ui.update_main(ui.chat_history)
        return "skip"


    return "continue"

async def run_gortex():
    console = Console(theme=GORTEX_THEME)
    ui = DashboardUI(console)
    observer = GortexObserver()
    
    total_tokens = 0
    total_cost = 0.0
    global_file_cache = {} # 세션 간 파일 캐시 유지 (현재 메모리 기반)

    workflow = compile_gortex_graph()

    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    import aiosqlite
    
    db_path = os.getenv("DB_PATH", "gortex_sessions.db")
    
    async with aiosqlite.connect(db_path) as db:
        memory = AsyncSqliteSaver(db)
        app = workflow.compile(checkpointer=memory)
        
        thread_id = str(random.randint(1000, 9999))
        config = {"configurable": {"thread_id": thread_id}}
        
        console.print(f"[bold cyan]🚀 Gortex v1.0 Initialized. (Thread ID: {thread_id})[/bold cyan]")
        console.print("Type 'exit' to quit. Press 'Ctrl+C' during execution to interrupt current task.\n")

        with Live(ui.layout, console=console, refresh_per_second=4) as live:
            interrupted_last_time = False
            while True:
                try:
                    live.stop()
                    user_input = await get_user_input(console)
                    live.start()

                    if user_input.lower() in ["exit", "quit", "q"]:
                        break
                    
                    if interrupted_last_time:
                        actual_input = f"[CONTEXT: 이전 작업이 사용자에 의해 중단된 후 재개됨] {user_input}"
                        interrupted_last_time = False
                    else:
                        actual_input = user_input

                    cmd_status = "continue"
                    if user_input.startswith("/"):
                        cmd_status = await handle_command(user_input, ui, observer)
                        if cmd_status == "skip":
                            continue
                    
                    # 2. 실행 및 스트리밍 업데이트
                    # 캐시 무결성 검사 (부팅/재개 시 디스크 상태와 대조)
                    from gortex.utils.tools import get_file_hash
                    valid_cache = {}
                    for path, cached_hash in global_file_cache.items():
                        if os.path.exists(path) and get_file_hash(path) == cached_hash:
                            valid_cache[path] = cached_hash
                    global_file_cache = valid_cache

                    initial_state = {
                        "messages": [("user", actual_input)],
                        "working_dir": os.getenv("WORKING_DIR", "./workspace"),
                        "coder_iteration": 0,
                        "file_cache": global_file_cache,
                        "active_constraints": []
                    }
                    
                    if cmd_status == "summarize":
                        initial_state["messages"] = [("system", "Manual summary trigger")] * 12

                    from gortex.core.evolutionary_memory import EvolutionaryMemory
                    evo_mem = EvolutionaryMemory()
                    initial_state["active_constraints"] = evo_mem.get_active_constraints(user_input)

                    try:
                        async for event in app.astream(initial_state, config):
                            for node_name, output in event.items():
                                ui.current_agent = node_name
                                
                                has_tool_call = False
                                if "messages" in output:
                                    for m in output["messages"]:
                                        if (isinstance(m, tuple) and m[0] == "tool") or (hasattr(m, 'type') and m.type == "tool"):
                                            has_tool_call = True
                                            break
                                
                                if has_tool_call:
                                    ui.start_tool_progress(f"Agent {node_name} is using tools...")
                                else:
                                    ui.stop_tool_progress()

                                thought = output.get("thought") or output.get("thought_process")
                                if thought:
                                    ui.update_thought(thought, agent_name=node_name)

                                if "messages" in output:
                                    for msg in output["messages"]:
                                        if isinstance(msg, tuple):
                                            role, content = msg
                                            ui.chat_history.append(msg)
                                        else:
                                            role = msg.type
                                            content = msg.content
                                            ui.chat_history.append((role, content))
                                        
                                        if isinstance(content, str):
                                            new_tokens = count_tokens(content)
                                            total_tokens += new_tokens
                                            total_cost += estimate_cost(new_tokens)
                                
                                ui.update_main(ui.chat_history)
                                ui.update_sidebar(
                                    agent=ui.current_agent,
                                    step=str(output.get("current_step", "N/A")),
                                    tokens=total_tokens,
                                    cost=total_cost,
                                    rules=len(initial_state["active_constraints"])
                                )
                                
                                # 로그 기록 및 UI 업데이트
                                log_entry = {"agent": node_name, "event": "node_complete"}
                                ui.update_logs(log_entry)
                                observer.log_event(node_name, "node_complete", output)
                                
                                # 전역 파일 캐시 동기화
                                if "file_cache" in output:
                                    global_file_cache.update(output["file_cache"])
                                
                                await asyncio.sleep(0.1)
                                ui.reset_thought_style()
                                
                    except KeyboardInterrupt:

                        interrupted_last_time = True
                        ui.chat_history.append(("system", "⚠️ 사용자에 의해 작업이 중단되었습니다. 상태가 보존되었습니다."))
                        ui.update_main(ui.chat_history)
                        ui.stop_tool_progress()
                        ui.reset_thought_style()
                        logger.info("Agent execution interrupted.")

                    ui.current_agent = "Idle"
                    ui.complete_thought_style()
                    ui.update_sidebar("Idle", "N/A", total_tokens, total_cost, len(initial_state["active_constraints"]))

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "할당량" in error_msg or "exhausted" in error_msg.lower():
                        live.stop()
                        console.clear()
                        console.print("\n" * 3)
                        console.print(Panel(
                            "[bold red]🚫 API QUOTA EXHAUSTED[/bold red]\n\n" 
                            "Gemini API 할당량이 모두 소진되었습니다.\n" 
                            "1. .env 파일의 API 키를 확인해주세요.\n" 
                            "2. 일정 시간 대기 후 다시 시도해주세요.\n\n" 
                            "[dim]시스템을 안전하게 종료합니다. 엔터를 누르세요...[/dim]",
                            title="System Emergency", border_style="red"
                        ))
                        await asyncio.get_event_loop().run_in_executor(None, input, "")
                        break
                    
                    console.print(f"[bold red]Error: {e}[/bold red]")
                    observer.log_event("System", "error", str(e))
                    break

    # 세션 아카이빙 (종료 전 백업)
    try:
        archive_dir = "logs/archives"
        os.makedirs(archive_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists("tech_radar.json"):
            shutil.copy2("tech_radar.json", f"{archive_dir}/tech_radar_{ts}.json")
            
        logger.info(f"Session data archived to {archive_dir}")
    except Exception as e:
        logger.error(f"Archiving failed: {e}")

    console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")


if __name__ == "__main__":
    try:
        asyncio.run(run_gortex())
    except KeyboardInterrupt:
        pass