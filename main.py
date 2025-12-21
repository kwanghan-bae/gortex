import os
import asyncio
import random
import logging
import json
import shutil
import time
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.align import Align
from dotenv import load_dotenv

from gortex.core.graph import compile_gortex_graph
from gortex.ui.dashboard import DashboardUI
from gortex.ui.dashboard_theme import GORTEX_THEME, ThemeManager
from gortex.core.observer import GortexObserver
from gortex.utils.token_counter import count_tokens, estimate_cost
from gortex.core.auth import GortexAuth
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.core.config import GortexConfig
from gortex.agents.analyst import AnalystAgent
from gortex.utils.tools import get_file_hash, deep_integrity_check
from gortex.utils.indexer import SynapticIndexer
from gortex.utils.docker_gen import DockerGenerator
from gortex.utils.git_tool import GitTool
from gortex.utils.notifier import Notifier

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GortexMain")

load_dotenv()

async def get_user_input(console: Console):
    """터미널 입력과 웹 입력 큐를 동시에 감시하며 비차단 방식으로 입력을 받음"""
    from gortex.ui.web_server import manager
    
    # 터미널 입력을 위한 비동기 태스크
    terminal_task = asyncio.create_task(
        asyncio.get_event_loop().run_in_executor(None, console.input, "[bold green]User > [/bold green]")
    )
    
    # 웹 큐 입력을 위한 비동기 태스크
    web_task = asyncio.create_task(manager.input_queue.get())
    
    # 먼저 도착하는 입력을 반환
    done, pending = await asyncio.wait(
        [terminal_task, web_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 나머지 태스크 취소
    for task in pending:
        task.cancel()
        
    result = done.pop().result()
    if isinstance(result, str):
        return result.strip()
    return ""

async def handle_command(user_input: str, ui: DashboardUI, observer: GortexObserver, all_sessions_cache: dict = None, thread_id: str = None, theme_manager: ThemeManager = None) -> str:
    """'/'로 시작하는 명령어를 처리합니다. 반환값에 따라 메인 루프의 행동을 결정합니다."""
    cmd_parts = user_input.lower().strip().split()
    cmd = cmd_parts[0]
    
    if cmd == "/clear":
        ui.chat_history = []
        ui.update_main([])
        ui.update_thought("Chat history cleared.")
        return "skip"
    
    elif cmd == "/theme":
        if not theme_manager:
            return "skip"
        if len(cmd_parts) < 2:
            themes = ", ".join(theme_manager.list_themes())
            ui.chat_history.append(("system", f"사용 가능한 테마: {themes}"))
        else:
            new_theme = cmd_parts[1]
            if theme_manager.set_theme(new_theme):
                ui.console.theme = theme_manager.get_theme()
                ui.chat_history.append(("system", f"✅ 테마가 '{new_theme}'(으)로 변경되었습니다."))
            else:
                ui.chat_history.append(("system", f"❌ 알 수 없는 테마: {new_theme}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/config":
        config = GortexConfig()
        if len(cmd_parts) < 2:
            settings_json = json.dumps(config.list_all(), indent=2, ensure_ascii=False)
            ui.chat_history.append(("system", f"⚙️ 현재 설정:\n{settings_json}"))
        elif len(cmd_parts) >= 3:
            key, val = cmd_parts[1], cmd_parts[2]
            # 타입 추론 (간단히)
            if val.lower() == "true": val = True
            elif val.lower() == "false": val = False
            elif val.isdigit(): val = int(val)
            
            config.set(key, val)
            ui.chat_history.append(("system", f"✅ 설정 변경됨: {key} = {val}"))
        else:
            ui.chat_history.append(("system", "사용법: /config [key] [value] 또는 /config (조회)"))
        ui.update_main(ui.chat_history)
        return "skip"
    
    elif cmd == "/index":
        ui.chat_history.append(("system", "🔍 프로젝트 코드 인덱싱을 시작합니다..."))
        ui.update_main(ui.chat_history)
        indexer = SynapticIndexer()
        indexer.scan_project()
        ui.chat_history.append(("system", f"✅ 인덱싱 완료! {len(indexer.index)}개의 파일이 분석되었습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/search":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /search [symbol_name]"))
        else:
            query = cmd_parts[1]
            indexer = SynapticIndexer()
            # 파일에서 인덱스 로드 로직이 indexer.__init__에 없으므로 수동 로드 또는 scan 필요
            if os.path.exists(indexer.index_path):
                with open(indexer.index_path, "r", encoding='utf-8') as f:
                    indexer.index = json.load(f)
            
            results = indexer.search(query)
            if not results:
                ui.chat_history.append(("system", f"❌ '{query}'에 대한 검색 결과가 없습니다."))
            else:
                table = Table(title=f"🔍 Synaptic Search: '{query}'", show_header=True, header_style="bold magenta")
                table.add_column("Type", style="cyan")
                table.add_column("Symbol", style="bold yellow")
                table.add_column("Location", style="green")
                table.add_column("Description", style="dim", overflow="ellipsis")
                
                for r in results[:15]: # 최대 15개 표시
                    type_style = "bold blue" if r["type"] == "class" else "bold green"
                    table.add_row(
                        Text(r["type"].upper(), style=type_style),
                        r["name"],
                        f"{r['file']}:{r['line']}",
                        (r.get("docstring") or "N/A").split("\n")[0]
                    )
                ui.chat_history.append(("system", table))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/map":
        indexer = SynapticIndexer()
        if os.path.exists(indexer.index_path):
            with open(indexer.index_path, "r", encoding='utf-8') as f:
                indexer.index = json.load(f)
        else:
            indexer.scan_project()
            
        proj_map = indexer.generate_map()
        root_tree = Tree("📁 [bold cyan]Gortex Project Map[/bold cyan]")
        
        # 모듈별 노드 추가
        for mod_name, info in proj_map["nodes"].items():
            mod_tree = root_tree.add(f"📦 [bold yellow]{mod_name}[/bold yellow] ([dim]{info['file']}[/dim])")
            if info["classes"]:
                cls_tree = mod_tree.add("🏛️ [cyan]Classes[/cyan]")
                for c in info["classes"]: cls_tree.add(f"[bold blue]{c}[/bold blue]")
            if info["functions"]:
                func_tree = mod_tree.add("λ [green]Functions[/green]")
                for f in info["functions"]: func_tree.add(f"[bold green]{f}[/bold green]")
        
        ui.chat_history.append(("system", root_tree))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/dockerize":
        gen = DockerGenerator()
        res1 = gen.generate_dockerfile()
        res2 = gen.generate_compose()
        ui.chat_history.append(("system", f"{res1}\n{res2}\n\n[bold yellow]Next Step:[/bold yellow] 'docker-compose up --build -d'를 실행하여 컨테이너를 가동하세요."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/bundle":
        import zipfile
        bundle_dir = "logs/bundles"
        os.makedirs(bundle_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_path = f"{bundle_dir}/gortex_project_{timestamp}.zip"
        
        ignore_patterns = {".git", "venv", "__pycache__", ".DS_Store", "logs/bundles", "logs/backups"}
        
        try:
            with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk("."):
                    dirs[:] = [d for d in dirs if d not in ignore_patterns]
                    for file in files:
                        if file in ignore_patterns: continue
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, "."))
            ui.chat_history.append(("system", f"📦 프로젝트 번들링 완료: {bundle_path}"))
        except Exception as e:
            ui.chat_history.append(("system", f"❌ 번들링 실패: {str(e)}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/deploy":
        gt = GitTool()
        if not gt.is_repo():
            ui.chat_history.append(("system", "❌ Git 저장소가 아닙니다. 'git init'을 먼저 수행하세요."))
        else:
            try:
                status = gt.status()
                if not status:
                    ui.chat_history.append(("system", "✅ 변경 사항이 없습니다."))
                else:
                    ui.chat_history.append(("system", f"🚀 배포 시작...\n{status}"))
                    ui.update_main(ui.chat_history)
                    
                    gt.add_all()
                    msg = f"feat: Gortex Auto-Deploy ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
                    gt.commit(msg)
                    branch = gt.get_current_branch()
                    gt.push(branch=branch)
                    
                    ui.chat_history.append(("system", f"✅ 배포 완료! ({branch} 브랜치로 푸시됨)"))
            except Exception as e:
                ui.chat_history.append(("system", f"❌ 배포 실패: {str(e)}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/pr":
        if len(cmd_parts) < 3:
            ui.chat_history.append(("system", "사용법: /pr [owner/repo] [pr_title]"))
        else:
            repo_full = cmd_parts[1]
            pr_title = " ".join(cmd_parts[2:])
            try:
                owner, repo = repo_full.split("/")
                gt = GitTool()
                branch = gt.get_current_branch()
                
                ui.chat_history.append(("system", f"🚀 PR 생성 중: {repo_full} ({branch} -> main)..."))
                ui.update_main(ui.chat_history)
                
                # 원격 푸시 먼저 수행
                gt.push(branch=branch)
                
                # PR 생성
                res = gt.create_github_pr(
                    repo_owner=owner,
                    repo_name=repo,
                    title=pr_title,
                    body=f"Generated by Gortex AI at {datetime.now().isoformat()}",
                    head=branch
                )
                ui.chat_history.append(("system", f"✅ PR이 성공적으로 생성되었습니다: {res.get('html_url')}"))
            except Exception as e:
                ui.chat_history.append(("system", f"❌ PR 생성 실패: {str(e)}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/report":
        ui.chat_history.append(("system", "📊 성과 리포트를 생성 중입니다..."))
        ui.update_main(ui.chat_history)
        
        analyst = AnalystAgent()
        report = analyst.generate_performance_report()
        
        # 화면 출력용 패널 구성
        from rich.markdown import Markdown
        report_panel = Panel(Markdown(report), title="🚀 GORTEX PERFORMANCE REPORT", border_style="magenta", padding=(1, 2))
        ui.chat_history.append(("system", report_panel))
        
        # 외부 알림 전송 (옵션)
        if "--notify" in cmd_parts:
            notifier = Notifier()
            notifier.send_notification(report, title="📊 Gortex Executive Report")
            ui.chat_history.append(("system", "🔔 리포트가 외부 채널로 전송되었습니다."))
            
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/notify":
        msg = user_input[8:].strip() if len(user_input) > 8 else "현재 Gortex 시스템이 정상 작동 중입니다."
        notifier = Notifier()
        notifier.send_notification(msg)
        ui.chat_history.append(("system", "🔔 알림 전송을 완료했습니다."))
        ui.update_main(ui.chat_history)
        return "skip"
    
    elif cmd == "/export":
        export_dir = "logs/exports"
        os.makedirs(export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"{export_dir}/session_{thread_id}_{timestamp}.json"
        
        # 직렬화 가능한 형태로 변환 (Rich 객체 제외)
        serializable_history = []
        for role, content in ui.chat_history:
            if isinstance(content, str):
                serializable_history.append((role, content))
            else:
                serializable_history.append((role, f"[Rich Object: {type(content).__name__}]"))

        data = {
            "thread_id": thread_id,
            "exported_at": datetime.now().isoformat(),
            "chat_history": serializable_history,
            "thought_history": ui.thought_history,
            "file_cache": all_sessions_cache.get(thread_id, {}) if all_sessions_cache else {}
        }
        
        try:
            with open(export_path, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            ui.chat_history.append(("system", f"✅ 세션이 성공적으로 내보내졌습니다: {export_path}"))
        except Exception as e:
            ui.chat_history.append(("system", f"❌ 내보내기 실패: {str(e)}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/import":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /import [file_path]"))
        else:
            import_path = cmd_parts[1]
            if os.path.exists(import_path):
                try:
                    with open(import_path, "r", encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 현재 세션에 데이터 주입
                    imported_history = [(r, f"[RESTORED] {c}" if r != "system" else c) for r, c in data.get("chat_history", [])]
                    ui.chat_history.extend(imported_history)
                    
                    if "thought_history" in data:
                        ui.thought_history.extend(data["thought_history"])
                        if data["thought_history"]:
                            last_thought = data["thought_history"][-1]
                            ui.update_thought(f"[RESTORED] {last_thought[1]}", agent_name=last_thought[0])

                    if all_sessions_cache is not None and thread_id:
                        all_sessions_cache[thread_id].update(data.get("file_cache", {}))
                    
                    ui.chat_history.append(("system", f"✅ 세션 데이터를 '{import_path}'에서 불러왔습니다."))
                except Exception as e:
                    ui.chat_history.append(("system", f"❌ 불러오기 실패: {str(e)}"))
            else:
                ui.chat_history.append(("system", f"❌ 파일을 찾을 수 없습니다: {import_path}"))
        ui.update_main(ui.chat_history)
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
    # 웹 대시보드 서버 시작 (백그라운드)
    from gortex.ui.web_server import run_server
    import threading
    web_thread = threading.Thread(target=run_server, kwargs={"port": 8000}, daemon=True)
    web_thread.start()
    logger.info("📡 Gortex Web Dashboard server started at http://localhost:8000")

    console = Console(theme=GORTEX_THEME)
    theme_manager = ThemeManager()
    ui = DashboardUI(console)
    observer = GortexObserver()
    total_tokens, total_cost = 0, 0.0
    total_latency_ms, node_count = 0, 0
    
    # 세션별 파일 캐시 관리 (Isolation)
    cache_path = "logs/file_cache.json"
    all_sessions_cache = {} # {thread_id: {path: hash}}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f: all_sessions_cache = json.load(f)
            logger.info(f"Loaded caches for {len(all_sessions_cache)} sessions.")
        except: pass

    workflow = compile_gortex_graph()
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    import aiosqlite
    
    # 부팅 시 자동 인덱싱 수행
    indexer = SynapticIndexer()
    indexer.scan_project()

    db_path = os.getenv("DB_PATH", "gortex_sessions.db")
    async with aiosqlite.connect(db_path) as db:
        memory = AsyncSqliteSaver(db)
        app = workflow.compile(checkpointer=memory)
        
        # 실제로는 사용자별/세션별 ID를 받아야 하지만, 여기서는 랜덤 생성
        thread_id = str(random.randint(1000, 9999))
        config = {"configurable": {"thread_id": thread_id}}
        
        # 현재 세션 캐시 초기화/로드
        if thread_id not in all_sessions_cache:
            all_sessions_cache[thread_id] = {}
        session_cache = all_sessions_cache[thread_id]
        
        # [INTEGRITY] 부팅 시 파일 시스템 정밀 무결성 검사 수행
        working_dir = os.getenv("WORKING_DIR", "./workspace")
        os.makedirs(working_dir, exist_ok=True)
        session_cache, changed = deep_integrity_check(working_dir, session_cache)
        all_sessions_cache[thread_id] = session_cache
        
        if changed:
            logger.info(f"🔍 Deep integrity check found {len(changed)} changes. Cache updated.")
            ui.chat_history.append(("system", f"파일 시스템 정밀 검사 완료: {len(changed)}개의 변경 사항이 캐시에 반영되었습니다."))

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
                        cmd_status = await handle_command(user_input, ui, observer, all_sessions_cache, thread_id, theme_manager)
                        if cmd_status == "skip": continue
                    
                    # 세션 캐시 유효성 검사
                    session_cache = {p: h for p, h in session_cache.items() if os.path.exists(p) and get_file_hash(p) == h}
                    evo_mem.gc_rules() # 오래된 규칙 정리

                    initial_state = {
                        "messages": [("user", actual_input)],
                        "working_dir": os.getenv("WORKING_DIR", "./workspace"),
                        "coder_iteration": 0,
                        "file_cache": session_cache,
                        "active_constraints": evo_mem.get_active_constraints(user_input),
                        "api_call_count": auth_engine.get_call_count()
                    }
                    if cmd_status == "summarize": initial_state["messages"] = [("system", "Manual summary trigger")] * 12
                    elif cmd_status == "scout": initial_state["next_node"] = "trend_scout"

                    try:
                        node_start_time = time.time()
                        async for event in app.astream(initial_state, config):
                            for node_name, output in event.items():
                                node_latency_ms = int((time.time() - node_start_time) * 1000)
                                node_start_time = time.time()
                                total_latency_ms += node_latency_ms
                                node_count += 1
                                avg_latency = total_latency_ms // node_count
                                
                                ui.current_agent = node_name
                                has_tool = any((isinstance(m, tuple) and m[0] == "tool") or (hasattr(m, 'type') and m.type == "tool") for m in output.get("messages", []))
                                ui.start_tool_progress("Executing tool...") if has_tool else ui.stop_tool_progress()

                                thought = output.get("thought") or output.get("thought_process")
                                tree = output.get("thought_tree")
                                if output.get("diagram_code"):
                                    ui.current_diagram = output["diagram_code"]
                                if thought: ui.update_thought(thought, agent_name=node_name, tree=tree)

                                node_tokens = 0
                                if "messages" in output:
                                    for msg in output["messages"]:
                                        role, content = (msg[0], msg[1]) if isinstance(msg, tuple) else (msg.type, msg.content)
                                        ui.chat_history.append((role, content))
                                        
                                        # [ACHIEVEMENT] 주요 마일스톤 감지
                                        if role == "ai":
                                            if "모든 계획된 작업을 완료했습니다" in str(content):
                                                ui.add_achievement("All planned tasks completed!", icon="✅")
                                                Notifier().send_notification(f"세션 {thread_id}의 모든 작업이 성공적으로 완료되었습니다.", title="✅ Task Completed")
                                            elif "계획을 수립했습니다" in str(content):
                                                ui.add_achievement(f"New plan established: {output.get('goal', 'Unknown Goal')}", icon="🗺️")
                                            elif "Successfully wrote to" in str(content):
                                                ui.add_achievement(f"File updated: {str(content).split('/')[-1]}", icon="📝")

                                        if isinstance(content, str):
                                            t = count_tokens(content)
                                            node_tokens += t
                                            total_tokens += t
                                            total_cost += estimate_cost(t)
                                
                                ui.update_main(ui.chat_history)
                                ui.update_sidebar(
                                    ui.current_agent, 
                                    str(output.get("current_step", "N/A")), 
                                    total_tokens, 
                                    total_cost, 
                                    len(initial_state["active_constraints"]),
                                    auth_engine.get_provider(),
                                    auth_engine.get_call_count(),
                                    avg_latency
                                )
                                ui.update_logs({"agent": node_name, "event": "node_complete"})
                                # 정밀 프로파일링 기록
                                observer.log_event(
                                    node_name, "node_complete", 
                                    {"goal": output.get("goal")}, 
                                    latency_ms=node_latency_ms,
                                    tokens={"output": node_tokens}
                                )
                                if "file_cache" in output: session_cache.update(output["file_cache"])
                                await asyncio.sleep(0.01)
                                ui.reset_thought_style()
                                
                    except KeyboardInterrupt:
                        interrupted_last_time = True
                        ui.chat_history.append(("system", "⚠️ 사용자에 의해 작업이 중단되었습니다."))
                        ui.update_main(ui.chat_history)
                        ui.stop_tool_progress(); ui.reset_thought_style()
                        all_sessions_cache[thread_id] = session_cache
                        save_global_cache(all_sessions_cache) # 중단 시에도 캐시 저장

                    ui.current_agent = "Idle"; ui.complete_thought_style()
                    ui.update_sidebar(
                        "Idle", 
                        "N/A", 
                        total_tokens, 
                        total_cost, 
                        len(initial_state["active_constraints"]),
                        auth_engine.get_provider(),
                        auth_engine.get_call_count(),
                        total_latency_ms // max(1, node_count)
                    )
                    
                    # 매 턴 종료 후 세션 캐시 영속화
                    all_sessions_cache[thread_id] = session_cache
                    save_global_cache(all_sessions_cache)

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
        all_sessions_cache[thread_id] = session_cache
        with open("logs/file_cache.json", "w") as f: json.dump(all_sessions_cache, f, ensure_ascii=False, indent=2)
    except: pass
    console.print("\n[bold cyan]👋 Gortex session ended.[/bold cyan]")

if __name__ == "__main__":
    try: asyncio.run(run_gortex())
    except KeyboardInterrupt: pass