import os
import json
import logging
import asyncio
import shutil
from datetime import datetime
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from gortex.core.config import GortexConfig
from gortex.core.observer import GortexObserver
from gortex.utils.notifier import Notifier
from gortex.ui.three_js_bridge import ThreeJsBridge
from gortex.utils.indexer import SynapticIndexer
from gortex.agents.analyst import AnalystAgent

logger = logging.getLogger("GortexCommands")

async def handle_command(user_input: str, ui, observer: GortexObserver, all_sessions_cache: dict, thread_id: str, theme_manager) -> str:
    """모든 슬래시 명령어(/)를 유실 없이 처리합니다."""
    cmd_parts = user_input.split()
    cmd = cmd_parts[0].lower()
    
    if cmd == "/help":
        help_msg = """
📚 **Gortex 완전 명령어 가이드**
- `/status`: 시스템 성능, 토큰 사용량 및 자원 상태 보고
- `/rca [id]`: 특정 이벤트의 인과 관계(Root Cause) 역추적
- `/search [query]`: 프로젝트 내 의미 기반(Semantic) 심볼 검색
- `/map`: 프로젝트 전체 구조(파일/클래스/함수) 트리 출력
- `/kg`: 통합 지식 그래프(Knowledge Graph) 생성 및 시각화
- `/scan_debt`: 기술 부채 및 코드 복잡도 정밀 스캔
- `/index`: 프로젝트 코드베이스 재인덱싱 수행
- `/voice`: 음성 인터랙션 활성화/비활성화 토글
- `/language [ko|en]`: UI 및 응답 언어 즉시 변경
- `/theme [name]`: 대시보드 테마 변경
- `/config [key] [val]`: 시스템 설정 조회 및 변경
- `/export` / `/import`: 세션 데이터 내보내기/가져오기
- `/clear`: 화면 초기화
"""
        ui.chat_history.append(("system", Panel(Markdown(help_msg), title="HELP CENTER", border_style="cyan")))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/status":
        stats = observer.get_stats()
        report = f"### 📊 Gortex Status\n- **Tokens**: {stats.get('total_tokens')}\n- **Cost**: ${stats.get('total_cost')}\n- **Uptime**: {stats.get('uptime')}"
        ui.chat_history.append(("system", Panel(Markdown(report), title="STATUS", border_style="magenta")))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/rca":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /rca [event_id]"))
        else:
            event_id = cmd_parts[1]
            chain = observer.get_causal_chain(event_id)
            if not chain:
                ui.chat_history.append(("system", f"❌ 이벤트 ID '{event_id}'의 계보를 찾을 수 없습니다."))
            else:
                rca_tree = Tree(f"🛡️ [bold magenta]Root Cause Analysis: {event_id}[/bold magenta]")
                for ev in reversed(chain):
                    rca_tree.add(f"[bold cyan]{ev['agent']}[/bold cyan] -> {ev['event']} ([dim]{ev['id']}[/dim])")
                ui.chat_history.append(("system", rca_tree))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/search":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /search [검색어]"))
        else:
            query = " ".join(cmd_parts[1:])
            indexer = SynapticIndexer()
            results = indexer.search(query, normalize=True)
            if not results:
                ui.chat_history.append(("system", f"❌ '{query}'에 대한 검색 결과가 없습니다."))
            else:
                table = Table(title="🔍 Search Results", show_header=True)
                table.add_column("Symbol", style="bold yellow")
                table.add_column("Location", style="green")
                for r in results[:5]:
                    table.add_row(r["name"], f"{r['file']}:{r['line']}")
                ui.chat_history.append(("system", table))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/map":
        indexer = SynapticIndexer()
        if os.path.exists(indexer.index_path):
            with open(indexer.index_path, "r", encoding='utf-8') as f: indexer.index = json.load(f)
        else: indexer.scan_project()
        proj_map = indexer.generate_map()
        root_tree = Tree("📁 [bold cyan]Gortex Project Map[/bold cyan]")
        for mod_name, info in proj_map["nodes"].items():
            mod_tree = root_tree.add(f"📦 [bold yellow]{mod_name}[/bold yellow] ([dim]{info['file']}[/dim])")
            if info.get("classes"):
                cls_tree = mod_tree.add("🏛️ [cyan]Classes[/cyan]")
                for c in info["classes"]:
                    cls_tree.add(f"[bold blue]{c}[/bold blue]")
            if info.get("functions"):
                func_tree = mod_tree.add("λ [green]Functions[/green]")
                for f in info["functions"]:
                    func_tree.add(f"[bold green]{f}[/bold green]")
        ui.chat_history.append(("system", root_tree))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/kg":
        ui.chat_history.append(("system", "🧠 통합 지식 그래프 생성 중..."))
        ui.update_main(ui.chat_history)
        indexer = SynapticIndexer()
        kg_data = indexer.generate_knowledge_graph()
        kg_summary = f"### Knowledge Map\n- **Nodes**: {len(kg_data['nodes'])}\n- **Edges**: {len(kg_data['edges'])}"
        ui.chat_history.append(("system", Panel(Markdown(kg_summary), title="BRAIN MAP", border_style="blue")))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/language":
        if len(cmd_parts) > 1:
            lang = cmd_parts[1]
            from gortex.utils.translator import i18n
            i18n.current_lang = lang
            ui.target_language = lang
            ui.chat_history.append(("system", f"🌐 언어가 '{lang}'으로 변경되었습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/export":
        export_dir = "logs/exports"; os.makedirs(export_dir, exist_ok=True)
        export_path = f"{export_dir}/session_{thread_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        serializable = [(r, c if isinstance(c, str) else f"[Rich Object]") for r, c in ui.chat_history]
        data = {"thread_id": thread_id, "chat_history": serializable, "file_cache": all_sessions_cache.get(thread_id, {})}
        with open(export_path, "w", encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
        ui.chat_history.append(("system", f"✅ Exported: {export_path}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/clear":
        ui.chat_history = []
        ui.update_main([])
        return "skip"

    elif cmd == "/bug":
        bug_report_msg = "🐛 **버그 리포트**: [이슈 리포트 링크](https://github.com/kwanghan-bae/gortex/issues/new)"
        ui.chat_history.append(("system", bug_report_msg))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/mode":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "⚠️ 사용 가능한 모드: coding, research, debugging, analyst, standard"))
        else:
            mode = cmd_parts[1]
            valid_modes = ["coding", "research", "debugging", "analyst", "standard"]
            if mode in valid_modes:
                ui.set_mode(mode)
                ui.chat_history.append(("system", f"🎭 UI가 '{mode}' 모드로 전환되었습니다."))
            else:
                ui.chat_history.append(("system", f"❌ 잘못된 모드입니다. 사용 가능: {', '.join(valid_modes)}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/theme":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /theme [dark|light|dracula|...]"))
        else:
            theme_name = cmd_parts[1]
            if theme_manager:
                theme_manager.apply_theme(theme_name)
                ui.chat_history.append(("system", f"🎨 테마가 '{theme_name}'으로 변경되었습니다."))
            else:
                ui.chat_history.append(("system", "❌ 테마 매니저를 사용할 수 없습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/save":
        save_path = f"logs/sessions/snapshot_{thread_id}.json"
        try:
            with open(save_path, "w", encoding='utf-8') as f:
                json.dump(all_sessions_cache.get(thread_id, {}), f, indent=2)
            ui.chat_history.append(("system", f"💾 세션 상태가 저장되었습니다: {save_path}"))
        except Exception as e:
            ui.chat_history.append(("system", f"❌ 저장 실패: {e}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/load":
        save_path = f"logs/sessions/snapshot_{thread_id}.json"
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
                    all_sessions_cache[thread_id] = data
                ui.chat_history.append(("system", f"📂 세션 상태가 복원되었습니다."))
            except Exception as e:
                ui.chat_history.append(("system", f"❌ 복원 실패: {e}"))
        else:
            ui.chat_history.append(("system", "❌ 저장된 세션 스냅샷이 없습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/history":
        log_path = observer.log_path if observer else "logs/trace.jsonl"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding='utf-8') as f:
                    lines = f.readlines()[-10:] # Last 10 lines
                history_text = "".join(lines)
                ui.chat_history.append(("system", Panel(history_text, title="RECENT LOGS", border_style="dim")))
            except Exception as e:
                ui.chat_history.append(("system", f"❌ 로그 읽기 실패: {e}"))
        else:
            ui.chat_history.append(("system", "❌ 로그 파일이 없습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    ui.chat_history.append(("system", f"❓ 알 수 없는 명령어: {cmd}"))
    ui.update_main(ui.chat_history)
    return "skip"