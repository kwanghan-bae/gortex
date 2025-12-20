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
from rich.text import Text
from rich.align import Align
from dotenv import load_dotenv

from gortex.core.graph import compile_gortex_graph
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import GORTEX_THEME
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import count_tokens, estimate_cost
from gortex.core.auth import GortexAuth
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.utils.tools import get_file_hash

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
                        detail_panel = Panel(
                            Group(
                                Panel(f"TIME: {entry.get('timestamp')}\nAGENT: {entry.get('agent')}\nEVENT: {entry.get('event')}", title="Metadata", border_style="dim"),
                                Panel(JSON(json.dumps(entry.get("payload", {}), ensure_ascii=False)), title="Payload", border_style="blue")
                            ),
                            title=f"🔍 LOG DETAIL [#{actual_idx}]", border_style="magenta", padding=(1, 2)
                        )
                        ui.chat_history.append(("system", detail_panel))
                    else:
                        ui.chat_history.append(("system", f"인덱스 범위를 벗어났습니다. (0 ~ {total_logs-1})"))
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

    elif cmd == "/scout":
        ui.chat_history.append(("system", "기술 트렌드 수동 스캔을 요청하셨습니다."))
        ui.update_main(ui.chat_history)
        return "scout"

    elif cmd == "/logs":
        log_path = "logs/trace.jsonl"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    
                    # 필터링 로직 추가
                    filter_keyword = cmd_parts[3].lower() if len(cmd_parts) > 3 else None
                    
                    parsed_logs = []
                    for line in lines:
                        entry = json.loads(line)
                        if filter_keyword:
                            agent = entry.get("agent", "").lower()
                            event = entry.get("event", "").lower()
                            if filter_keyword not in agent and filter_keyword not in event:
                                continue
                        parsed_logs.append(entry)
                    
                    total_filtered = len(parsed_logs)
                    if total_filtered == 0:
                        ui.chat_history.append(("system", f"검색 결과가 없습니다. (필터: {filter_keyword})" if filter_keyword else "기록된 로그가 없습니다."))
                    else:
                        skip = int(cmd_parts[1]) if len(cmd_parts) > 1 else 0
                        limit = int(cmd_parts[2]) if len(cmd_parts) > 2 else 10
                        
                        end_idx = max(0, total_filtered - skip)
                        start_idx = max(0, end_idx - limit)
                        
                        recent_logs = parsed_logs[start_idx:end_idx]
                        
                        title = f"📜 Trace Logs"
                        if filter_keyword: title += f" (Filter: '{filter_keyword}')"
                        title += f" [{start_idx}~{end_idx-1} of {total_filtered}]"
                        
                        log_table = Table(
                            title=title, 
                            show_header=True, 
                            header_style="bold magenta",
                            caption="사용법: /logs [skip] [limit] [filter] | /log [index] 상세조회"
                        )
                        log_table.add_column("Idx", justify="right", style="dim")
                        log_table.add_column("Time", style="cyan")
                        log_table.add_column("Agent", style="bold yellow")
                        log_table.add_column("Event", style="green")
                        
                        for i, entry in enumerate(reversed(recent_logs)):
                            curr_idx = end_idx - 1 - i
                            timestamp = entry.get("timestamp", "").split("T")[-1][:8]
                            log_table.add_row(
                                str(curr_idx), 
                                timestamp, 
                                entry.get("agent", "N/A"), 
                                entry.get("event", "N/A")
                            )
                        ui.chat_history.append(("system", log_table))
            except ValueError:
                ui.chat_history.append(("system", "❌ 잘못된 인자입니다. 사용법: /logs [skip] [limit] [filter]"))
            except Exception as e:
                ui.chat_history.append(("system", f"❌ 로그 조회 중 오류 발생: {str(e)}"))
        else:
            ui.chat_history.append(("system", "로그 파일이 존재하지 않습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    return "continue"

def save_global_cache(cache):
    """전역 파일 캐시를 안전하게 저장합니다."""
    try:
        cache_path = "logs/file_cache.json"
        os.makedirs("logs", exist_ok=True)
        # 원자적 저장을 위해 임시 파일 사용
        tmp_path = cache_path + ".tmp"
        with open(tmp_path, "w", encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, cache_path)
    except Exception as e:
        logger.error(f"Failed to save global cache: {e}")

async def run_gortex():
    console = Console(theme=GORTEX_THEME)
    ui = DashboardUI(console)
    observer = GortexObserver()
    total_tokens, total_cost = 0, 0.0
    
    # 전역 파일 캐시 로드 (Persistence)
    cache_path = "logs/file_cache.json"
    global_file_cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f: global_file_cache = json.load(f)
            logger.info(f"Loaded {len(global_file_cache)} items from file cache.")
        except: pass

    workflow = compile_gortex_graph()
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    import aiosqlite
    
    db_path = os.getenv("DB_PATH", "gortex_sessions.db")
    async with aiosqlite.connect(db_path) as db:
        memory = AsyncSqliteSaver(db)
        app = workflow.compile(checkpointer=memory)
        thread_id = str(random.randint(1000, 9999))
        config = {"configurable": {"thread_id": thread_id}}
        auth_engine = GortexAuth()
        evo_mem = EvolutionaryMemory()
        
        console.print(f"[bold cyan]🚀 Gortex v1.0 Initialized. (ID: {thread_id})[/bold cyan]")
        with Live(ui.layout, console=console, refresh_per_second=4) as live:
            interrupted_last_time = False
            while True:
                try:
                    live.stop()
                    user_input = await get_user_input(console)
                    live.start()

                    if user_input.lower() in ["exit", "quit", "q"]:
                        break
                    
                    actual_input = f"[CONTEXT: 이전 작업 중단 후 재개됨] {user_input}" if interrupted_last_time else user_input
                    interrupted_last_time = False

                    cmd_status = "continue"
                    if user_input.startswith("/"):
                        cmd_status = await handle_command(user_input, ui, observer)
                        if cmd_status == "skip": continue
                    
                    # 상태 관리 및 최적화
                    global_file_cache = {p: h for p, h in global_file_cache.items() if os.path.exists(p) and get_file_hash(p) == h}
                    evo_mem.gc_rules() # 오래된 규칙 정리

                    initial_state = {
                        "messages": [("user", actual_input)],
                        "working_dir": os.getenv("WORKING_DIR", "./workspace"),
                        "coder_iteration": 0,
                        "file_cache": global_file_cache,
                        "active_constraints": evo_mem.get_active_constraints(user_input),
                        "api_call_count": auth_engine.get_call_count()
                    }
                    if cmd_status == "summarize": initial_state["messages"] = [("system", "Manual summary trigger")] * 12
                    elif cmd_status == "scout": initial_state["next_node"] = "trend_scout"

                    try:
                        async for event in app.astream(initial_state, config):
                            for node_name, output in event.items():
                                ui.current_agent = node_name
                                has_tool = any((isinstance(m, tuple) and m[0] == "tool") or (hasattr(m, 'type') and m.type == "tool") for m in output.get("messages", []))
                                ui.start_tool_progress("Executing tool...") if has_tool else ui.stop_tool_progress()

                                thought = output.get("thought") or output.get("thought_process")
                                if thought: ui.update_thought(thought, agent_name=node_name)

                                if "messages" in output:
                                    for msg in output["messages"]:
                                        role, content = (msg[0], msg[1]) if isinstance(msg, tuple) else (msg.type, msg.content)
                                        ui.chat_history.append((role, content))
                                        if isinstance(content, str):
                                            t = count_tokens(content)
                                            total_tokens += t
                                            total_cost += estimate_cost(t)
                                
                                ui.update_main(ui.chat_history)
                                ui.update_sidebar(ui.current_agent, str(output.get("current_step", "N/A")), total_tokens, total_cost, len(initial_state["active_constraints"]))
                                ui.update_logs({"agent": node_name, "event": "node_complete"})
                                observer.log_event(node_name, "node_complete", output)
                                if "file_cache" in output: global_file_cache.update(output["file_cache"])
                                await asyncio.sleep(0.01)
                                ui.reset_thought_style()
                                
                    except KeyboardInterrupt:
                        interrupted_last_time = True
                        ui.chat_history.append(("system", "⚠️ 사용자에 의해 작업이 중단되었습니다."))
                        ui.update_main(ui.chat_history)
                        ui.stop_tool_progress(); ui.reset_thought_style()
                        save_global_cache(global_file_cache) # 중단 시에도 캐시 저장

                    ui.current_agent = "Idle"; ui.complete_thought_style()
                    ui.update_sidebar("Idle", "N/A", total_tokens, total_cost, len(initial_state["active_constraints"]))
                    
                    # 매 턴 종료 후 캐시 영속화 강화
                    save_global_cache(global_file_cache)

                except KeyboardInterrupt: break
                except Exception as e:
                    if "할당량" in str(e) or "exhausted" in str(e).lower():
                        live.stop(); console.clear()
                        warning = Text.assemble(("\n🚫 API QUOTA EXHAUSTED\n\n", "bold red"), ("모든 Gemini API 키가 소진되었습니다.\n\n", "white"), ("[해결 방법]\n", "bold yellow"), ("1. gortex/.env에 새 키 추가\n2. 대기 후 재실행\n\n", "white"), ("상태는 저장되었습니다. 엔터를 누르세요...", "dim"))
                        console.print(Align.center(Panel(warning, title="EMERGENCY", border_style="red", padding=(1, 4)), vertical="middle"))
                        await asyncio.get_event_loop().run_in_executor(None, input, "")
                        break
                    console.print(f"[bold red]Error: {e}[/bold red]"); break

    try:
        archive_dir = "logs/archives"; os.makedirs(archive_dir, exist_ok=True)
        if os.path.exists("tech_radar.json"): shutil.copy2("tech_radar.json", f"{archive_dir}/tech_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open("logs/file_cache.json", "w") as f: json.dump(global_file_cache, f, ensure_ascii=False, indent=2)
    except: pass
    console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")

if __name__ == "__main__":
    try: asyncio.run(run_gortex())
    except KeyboardInterrupt: pass