import os
import asyncio
import random
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from dotenv import load_dotenv

from gortex.core.graph import compile_gortex_graph
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import GORTEX_THEME
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import count_tokens, estimate_cost

load_dotenv()

async def get_user_input(console: Console):
    """비차단 방식으로 사용자 입력을 받음"""
    return await asyncio.get_event_loop().run_in_executor(None, console.input, "[bold green]User > [/bold green]")

async def handle_command(user_input: str, ui: DashboardUI, observer: GortexObserver) -> bool:
    "'/'로 시작하는 명령어를 처리합니다. 에이전트 실행이 필요 없으면 True 반환."
    cmd = user_input.lower().strip()
    
    if cmd == "/clear":
        ui.chat_history = []
        ui.update_main([])
        ui.update_thought("Chat history cleared.")
        return True
    
    elif cmd == "/history":
        ui.chat_history.append(("system", "현재 세션의 대화 내역이 유지되고 있습니다."))
        ui.update_main(ui.chat_history)
        return True
        
    elif cmd == "/radar":
        import json
        if os.path.exists("tech_radar.json"):
            with open("tech_radar.json", "r") as f:
                radar = json.load(f)
                ui.chat_history.append(("system", f"Tech Radar: {json.dumps(radar, indent=2, ensure_ascii=False)}"))
        else:
            ui.chat_history.append(("system", "Tech Radar 데이터가 없습니다."))
        ui.update_main(ui.chat_history)
        return True

    return False

async def run_gortex():
    console = Console(theme=GORTEX_THEME)
    ui = DashboardUI(console)
    observer = GortexObserver()
    
    # 누적 토큰 및 비용
    total_tokens = 0
    total_cost = 0.0

    workflow = compile_gortex_graph()
    # Persistence 설정 (SQLite)
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    import aiosqlite
    
    db_path = os.getenv("DB_PATH", "gortex_sessions.db")
    
    async with aiosqlite.connect(db_path) as db:
        memory = AsyncSqliteSaver(db)
        app = workflow.compile(checkpointer=memory)
        
        thread_id = str(random.randint(1000, 9999))
        config = {"configurable": {"thread_id": thread_id}}
        
        console.print(f"[bold cyan]🚀 Gortex v1.0 Initialized. (Thread ID: {thread_id})[/bold cyan]")
        console.print("Type 'exit' to quit. Press 'Ctrl+C' to stop current task.\n")

        with Live(ui.layout, console=console, refresh_per_second=4) as live:
            while True:
                try:
                    # 사용자 입력 받기
                    live.stop()
                    user_input = await get_user_input(console)
                    live.start()

                    if user_input.lower() in ["exit", "quit", "q"]:
                        break
                    
                    # 명령어 처리
                    if user_input.startswith("/"):
                        if await handle_command(user_input, ui, observer):
                            continue
                    
                    # 2. 실행 및 스트리밍 업데이트
                    initial_state = {
                        "messages": [("user", user_input)],
                        "working_dir": os.getenv("WORKING_DIR", "./workspace"),
                        "coder_iteration": 0,
                        "active_constraints": []
                    }
                    
                    from gortex.core.evolutionary_memory import EvolutionaryMemory
                    evo_mem = EvolutionaryMemory()
                    initial_state["active_constraints"] = evo_mem.get_active_constraints(user_input)

                    async for event in app.astream(initial_state, config):
                        # 이벤트 데이터를 UI에 반영
                        for node_name, output in event.items():
                            ui.current_agent = node_name
                            
                            # 도구 실행 감지
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

                            # 사고 과정(Thought) 추출 및 UI 반영 (에이전트 이름 포함)
                            thought = output.get("thought") or output.get("thought_process")
                            if thought:
                                ui.update_thought(thought, agent_name=node_name)

                            if "messages" in output:
                                # 메시지 업데이트 및 토큰 계산
                                for msg in output["messages"]:
                                    content = ""
                                    if isinstance(msg, tuple):
                                        role, content = msg
                                        ui.chat_history.append(msg)
                                    else:
                                        role = msg.type
                                        content = msg.content
                                        ui.chat_history.append((role, content))
                                    
                                    # 토큰 누적
                                    new_tokens = count_tokens(content)
                                    total_tokens += new_tokens
                                    total_cost += estimate_cost(new_tokens)
                            
                            # 통계 및 UI 업데이트
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
                            
                            # UI 효과 리셋 (다음 노드 실행 전 잠시 대기하며 반전 효과 유지)
                            await asyncio.sleep(0.1)
                            ui.reset_thought_style()

                    ui.current_agent = "Idle"
                    ui.complete_thought_style()
                    ui.update_sidebar("Idle", "N/A", total_tokens, total_cost, len(initial_state["active_constraints"]))

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "🚫 모든 API 계정의 할당량이 소진되었습니다." in error_msg or "exhausted" in error_msg.lower():
                        live.stop()
                        console.print("\n")
                        console.print(Panel(
                            "[bold red]🚫 API 할당량 긴급 소진![/bold red]\n\n" 
                            "모든 Gemini API 키의 무료 할당량이 바닥났습니다.\n" 
                            "1. [yellow].env[/yellow] 파일에 새로운 API 키를 추가해주세요.\n" 
                            "2. 일정 시간 대기 후 다시 실행해주세요.\n\n" 
                            "[dim]시스템을 안전하게 중단합니다.[/dim]",
                            title="Quota Emergency",
                            border_style="red",
                            expand=False
                        ))
                        break
                    
                    console.print(f"[bold red]Error: {e}[/bold red]")
                    observer.log_event("System", "error", str(e))
                    break

    console.print("\n[bold cyan]👋 Gortex session ended. State saved.[/bold cyan]")

if __name__ == "__main__":
    try:
        asyncio.run(run_gortex())
    except KeyboardInterrupt:
        pass