import os
import json
import asyncio
import logging
import uuid
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

from gortex.core.state import GortexState
from gortex.core.graph import compile_gortex_graph
from gortex.core.auth import GortexAuth
from gortex.core.commands import handle_command
from gortex.core.engine import GortexEngine
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import ThemeManager
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import estimate_cost
from gortex.utils.tools import deep_integrity_check
from gortex.utils.vocal_bridge import VocalBridge
from gortex.utils.translator import i18n
from gortex.agents.analyst import AnalystAgent

logger = logging.getLogger("GortexMain")
console = Console()

async def get_user_input(ui):
    terminal_task = asyncio.create_task(asyncio.get_event_loop().run_in_executor(None, input, "👤 You: "))
    done, pending = await asyncio.wait([terminal_task], return_when=asyncio.FIRST_COMPLETED)
    for t in pending: t.cancel()
    return done.pop().result().strip() if done else ""

def save_sessions_cache(all_sessions_cache: dict):
    """세션 캐시 데이터를 파일로 영구 저장"""
    try:
        with open("logs/file_cache.json", "w", encoding='utf-8') as f:
            json.dump(all_sessions_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save session cache: {e}")

async def energy_recovery_loop(state_vars: dict, ui: DashboardUI):
    """Idle 시간 동안 에너지를 점진적으로 회복하는 루프"""
    while True:
        await asyncio.sleep(2) # 2초마다 체크
        if state_vars["agent_energy"] < 100:
            # 2초당 1포인트 회복
            state_vars["agent_energy"] = min(100, state_vars["agent_energy"] + 1)
            # UI 실시간 반영 (Idle 상태일 때만)
            if ui.current_agent == "Idle":
                ui.update_sidebar("Idle", "Recovering...", state_vars["total_tokens"], state_vars["total_cost"], 0, 
                                  energy=state_vars["agent_energy"], efficiency=state_vars["last_efficiency"], 
                                  agent_economy=state_vars.get("agent_economy"))

async def run_gortex():
    theme_manager = ThemeManager()
    ui = DashboardUI(console=console)
    observer = GortexObserver(); vocal = VocalBridge()
    engine = GortexEngine(ui, observer, vocal)
    
    cache_path = "logs/file_cache.json"
    all_sessions_cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f:
                all_sessions_cache = json.load(f)
        except:
            pass

    workflow = compile_gortex_graph()
    thread_id = str(uuid.uuid4())[:8]
    
    state_vars = {
        "agent_energy": 100, "last_efficiency": 100.0,
        "total_tokens": 0, "total_cost": 0.0,
        "session_cache": all_sessions_cache.get(thread_id, {}),
        "pinned_messages": [],
        "last_event_id": None,
        "last_question": None,
        "agent_economy": {} # 초기 경제 데이터 빈값 설정
    }
    
    working_dir = os.getenv("WORKING_DIR", "./workspace")
    os.makedirs(working_dir, exist_ok=True)
    state_vars["session_cache"], _ = deep_integrity_check(working_dir, state_vars["session_cache"])
    
    console.print(f"[bold cyan]🚀 {i18n.t('system.initialized', thread_id=thread_id)}[/bold cyan]")
    
    # 에너지 회복 루프 시작
    recovery_task = asyncio.create_task(energy_recovery_loop(state_vars, ui))
    
    with Live(ui.layout, console=console, refresh_per_second=4) as live:
        while True:
            try:
                user_input = await get_user_input(ui)
                if not user_input: continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    break

                # [INTERACTIVE LEARNING] 유실 복구
                if state_vars["last_question"] and user_input:
                    try:
                        AnalystAgent().learn_from_interaction(state_vars["last_question"], user_input)
                        state_vars["last_question"] = None
                    except:
                        pass

                if user_input.startswith("/"):
                    status = await handle_command(user_input, ui, observer, all_sessions_cache, thread_id, theme_manager)
                    if status == "skip": continue

                initial_state = {
                    "messages": [("user", user_input)],
                    "pinned_messages": state_vars["pinned_messages"],
                    "working_dir": working_dir,
                    "file_cache": state_vars["session_cache"],
                    "agent_energy": state_vars["agent_energy"],
                    "last_efficiency": state_vars["last_efficiency"]
                }

                async for event in workflow.astream(initial_state, config={"configurable": {"thread_id": thread_id}}):
                    for node_name, output in event.items():
                        # Engine에서 인과 관계, UI 모드, 보안, 스트리밍 일괄 처리
                        node_tokens = await engine.process_node_output(node_name, output, state_vars)
                        
                        state_vars["total_tokens"] += node_tokens
                        state_vars["total_cost"] += estimate_cost(node_tokens)
                        
                        # 질문 캡처 (다음 턴 대화형 학습용)
                        if node_name == "manager" and output.get("question_to_user"):
                            state_vars["last_question"] = output["question_to_user"]

                        ui.update_main(ui.chat_history)
                        ui.update_sidebar(node_name, "Active", state_vars["total_tokens"], state_vars["total_cost"], 0, energy=state_vars["agent_energy"], efficiency=state_vars["last_efficiency"], agent_economy=state_vars.get("agent_economy"))

                # 매 턴 종료 후 세션 캐시 영속화
                all_sessions_cache[thread_id] = state_vars["session_cache"]
                save_sessions_cache(all_sessions_cache)

                ui.update_sidebar("Idle", "N/A", state_vars["total_tokens"], state_vars["total_cost"], 0, energy=state_vars["agent_energy"], efficiency=state_vars["last_efficiency"], agent_economy=state_vars.get("agent_economy"))

            except KeyboardInterrupt:
                break
            except Exception as e:
                # [QUOTA UI] 유실 복구
                if "할당량" in str(e).lower() or "exhausted" in str(e).lower():
                    live.stop(); console.clear()
                    warning = Text.assemble(("\n🚫 API QUOTA EXHAUSTED\n\n", "bold red"), ("모든 API 키가 소진되었습니다. 대기 후 재실행하세요.\n", "white"))
                    console.print(Align.center(Panel(warning, title="EMERGENCY", border_style="red"), vertical="middle"))
                    break
                logger.error(f"Loop error: {e}")
                ui.chat_history.append(("system", f"❌ Error: {e}"))

    # 세션 종료 시 아카이빙
    AnalystAgent().auto_finalize_session(initial_state)
    all_sessions_cache[thread_id] = state_vars["session_cache"]
    with open(cache_path, "w") as f:
        json.dump(all_sessions_cache, f, indent=2)
    console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")

if __name__ == "__main__":
    asyncio.run(run_gortex())