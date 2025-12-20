import os
import asyncio
import random
from rich.console import Console
from rich.live import Live
from dotenv import load_dotenv

from gortex.core.graph import compile_gortex_graph
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import GORTEX_THEME
from gortex.core.observer import GortexObserver

load_dotenv()

async def run_gortex():
    console = Console(theme=GORTEX_THEME)
    ui = DashboardUI(console)
    observer = GortexObserver()
    
    # 1. 그래프 컴파일
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
        console.print("Type 'exit' to quit.\n")

        with Live(ui.layout, console=console, refresh_per_second=4) as live:
            while True:
                try:
                    # 사용자 입력 받기 (Live UI 밖에서 처리)
                    live.stop()
                    user_input = console.input("[bold green]User > [/bold green]")
                    live.start()

                    if user_input.lower() in ["exit", "quit", "q"]:
                        break
                    
                    # 2. 실행 및 스트리밍 업데이트
                    # 초기 상태 설정
                    initial_state = {
                        "messages": [("user", user_input)],
                        "working_dir": os.getenv("WORKING_DIR", "./workspace"),
                        "coder_iteration": 0,
                        "active_constraints": []
                    }
                    
                    # 릴리즈 노트에서 활성 제약 조건 가져오기 (Analyst/Evolution 로직)
                    from gortex.core.evolutionary_memory import EvolutionaryMemory
                    evo_mem = EvolutionaryMemory()
                    initial_state["active_constraints"] = evo_mem.get_active_constraints(user_input)

                    async for event in app.astream(initial_state, config):
                        # 이벤트 데이터를 UI에 반영
                        for node_name, output in event.items():
                            ui.current_agent = node_name
                            if "messages" in output:
                                # 메시지 업데이트 (단순 추가 방식)
                                for msg in output["messages"]:
                                    if isinstance(msg, tuple):
                                        ui.chat_history.append(msg)
                                    else:
                                        # BaseMessage 객체인 경우
                                        role = "ai" if msg.type == "ai" else "system"
                                        ui.chat_history.append((role, msg.content))
                            
                            # 통계 업데이트
                            ui.update_main(ui.chat_history)
                            ui.update_sidebar(
                                agent=ui.current_agent,
                                step=str(output.get("current_step", "N/A")),
                                tokens=0, # 토큰 계산기 필요
                                rules=len(initial_state["active_constraints"])
                            )
                            
                            # 로그 기록
                            observer.log_event(node_name, "node_complete", output)

                    ui.current_agent = "Idle"
                    ui.update_sidebar("Idle", "N/A", 0, len(initial_state["active_constraints"]))

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                    observer.log_event("System", "error", str(e))
                    break

    console.print("\n[bold cyan]👋 Gortex session ended. State saved.[/bold cyan]")

if __name__ == "__main__":
    try:
        asyncio.run(run_gortex())
    except KeyboardInterrupt:
        pass
