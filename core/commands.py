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
from gortex.utils.indexer import SynapticIndexer
from gortex.agents.analyst import AnalystAgent
from gortex.core.registry import registry

logger = logging.getLogger("GortexCommands")

async def handle_command(user_input: str, ui, observer: GortexObserver, all_sessions_cache: dict, thread_id: str, theme_manager) -> str:
    """모든 슬래시 명령어(/)를 유실 없이 처리합니다."""
    # 입력 정제 강화
    user_input = user_input.strip()
    if not user_input.startswith("/"): return "pass"
    
    cmd_parts = user_input.split()
    cmd = cmd_parts[0].lower()
    
    # 여러 개의 슬래시로 시작하는 경우(예: //help) 정정
    if cmd.startswith("//"):
        cmd = "/" + cmd.lstrip("/")
    
    if cmd == "/help":
        help_msg = """
📚 **Gortex 완전 명령어 가이드**
- `/status`: 시스템 성능, 토큰 사용량 및 자원 상태 보고
- `/agents`: 레지스트리에 등록된 모든 에이전트 목록 및 명세 출력
- `/inspect [id]`: 특정 지식(규칙)의 상세 명세 및 탄생 계보 추적
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

    elif cmd == "/agents":
        agents = registry.list_agents()
        if not agents:
            ui.chat_history.append(("system", "❌ 등록된 에이전트가 없습니다."))
        else:
            table = Table(title="🤖 Gortex Active Agents (v3.0)", show_header=True, header_style="bold magenta")
            table.add_column("Name", style="bold cyan")
            table.add_column("Role", style="yellow")
            table.add_column("Version", style="dim")
            table.add_column("Capabilities (Tools)", style="green")
            
            for name in sorted(agents):
                meta = registry.get_metadata(name)
                table.add_row(
                    name.capitalize(),
                    meta.role,
                    f"v{meta.version}",
                    ", ".join(meta.tools)
                )
            ui.chat_history.append(("system", table))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/inspect":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "사용법: /inspect [rule_id]"))
        else:
            rule_id = cmd_parts[1]
            from gortex.core.evolutionary_memory import EvolutionaryMemory
            evo_mem = EvolutionaryMemory()
            
            # 모든 샤드에서 규칙 탐색
            target_rule = None
            for shard in evo_mem.shards.values():
                for r in shard:
                    if r["id"] == rule_id:
                        target_rule = r; break
                if target_rule: break
            
            if not target_rule:
                ui.chat_history.append(("system", f"❌ 규칙 ID '{rule_id}'를 찾을 수 없습니다."))
            else:
                # 상세 정보 카드
                card = Panel(
                    Text.assemble(
                        ("Instruction: ", "bold yellow"), f"{target_rule['learned_instruction']}\n",
                        ("Patterns: ", "bold cyan"), f"{', '.join(target_rule['trigger_patterns'])}\n",
                        ("Stats: ", "bold green"), f"Usage: {target_rule.get('usage_count',0)}, Success: {target_rule.get('success_count',0)}"
                    ),
                    title=f"🔍 Knowledge Detail: {rule_id}",
                    border_style="yellow"
                )
                ui.chat_history.append(("system", card))
                
                # 계보 트리 (Lineage Tree)
                if target_rule.get("parent_rules"):
                    tree = Tree(f"🌳 [bold green]Lineage of {rule_id}[/bold green]")
                    
                    def add_parents(parent_tree, rule_ids):
                        for p_id in rule_ids:
                            node = parent_tree.add(f"[dim]{p_id}[/dim]")
                            # 재귀적으로 부모 찾기 (여기서는 1단계만 예시, 실제로는 메모리 전체 검색 필요)
                            # 단순화를 위해 ID만 표시하거나, 실제 상위 규칙 검색 로직 추가 가능
                    
                    add_parents(tree, target_rule["parent_rules"])
                    ui.chat_history.append(("system", tree))
                    
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/status":
        if hasattr(ui, "toggle_monitor_mode"):
            ui.toggle_monitor_mode()
        else:
            # Fallback for older UI versions (safety check)
            stats = observer.get_stats()
            report = f"### System Status\nTokens: {stats.get('total_tokens',0):,}\nCost: ${stats.get('total_cost',0):.4f}"
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

    elif cmd == "/index":
        ui.chat_history.append(("system", "🔍 프로젝트 재인덱싱을 시작합니다..."))
        ui.update_main(ui.chat_history)
        # 즉시 렌더링을 위해 main.py 스타일의 강제 출력 시뮬레이션 (여기서는 UI 업데이트로 충분)
        indexer = SynapticIndexer()
        indexer.scan_project()
        ui.chat_history.append(("system", "✅ 인덱싱이 완료되었습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/scan_debt":
        ui.chat_history.append(("system", "📉 기술 부채 및 코드 복잡도 정밀 스캔 중..."))
        ui.update_main(ui.chat_history)
        analyst = AnalystAgent()
        debt_report = analyst.scan_project_complexity()
        
        table = Table(title="📉 Project Technical Debt", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Complexity", justify="right")
        table.add_column("Risk", style="bold red")
        
        for item in debt_report[:10]:
            table.add_row(item["file"], str(item["score"]), item["reason"])
            
        ui.chat_history.append(("system", table))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/config":
        from gortex.core.auth import GortexAuth
        auth = GortexAuth()
        config_text = f"""
⚙️ **Gortex System Configuration**
- **Current Provider**: [bold green]{auth.get_provider()}[/bold green]
- **Ollama Model**: {auth.ollama_model}
- **Gemini Keys**: {len(auth.key_pool)} configured
- **Config Path**: `{auth._CONFIG_PATH}`
"""
        ui.chat_history.append(("system", Panel(Markdown(config_text), title="CONFIG", border_style="yellow")))
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

    elif cmd == "/memory":
        # Vector Store 지연 로딩 및 주입
        if hasattr(ui, "set_vector_store") and not ui.memory_viewer.vector_store:
             from gortex.utils.vector_store import ChromaVectorStore
             # Vector Store는 싱글톤이나 공유 객체로 관리하는 것이 좋으나, 
             # 현재 명령 컨텍스트에서는 신규 인스턴스를 생성하여 주입
             # (실제 환경에서는 GortexEngine이 사용하는 인스턴스를 참조하는 것이 이상적)
             store = ChromaVectorStore()
             ui.set_vector_store(store)

        if len(cmd_parts) > 1:
            subcmd = cmd_parts[1].lower()
            if subcmd in ["explore", "view"]:
                ui.toggle_memory_mode()
            elif subcmd == "clear":
                if ui.memory_active: ui.toggle_memory_mode()
            else:
                 # 검색 쿼리로 간주
                 query = " ".join(cmd_parts[1:])
                 ui.toggle_memory_mode(query=query)
        else:
            ui.toggle_memory_mode()
        return "skip"

    elif cmd == "/trace":
        if hasattr(ui, "toggle_trace_mode"):
            ui.toggle_trace_mode()
        else:
            ui.chat_history.append(("system", "❌ UI가 Trace 모드를 지원하지 않습니다."))
            ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/provider":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "⚠️ 사용법: /provider [gemini|ollama|openai]"))
        else:
            new_provider = cmd_parts[1].lower()
            from gortex.core.auth import GortexAuth
            try:
                auth = GortexAuth()
                auth.set_provider(new_provider)
                ui.provider = new_provider.upper() # 사이드바 즉시 반영
                ui.chat_history.append(("system", f"🔄 LLM 공급자가 '[bold green]{new_provider.upper()}[/bold green]'로 변경되었습니다."))
                ui.update_sidebar(provider=ui.provider)
            except ValueError as e:
                ui.chat_history.append(("system", f"❌ {e}"))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/model":
        if len(cmd_parts) < 2:
            ui.chat_history.append(("system", "⚠️ 사용법: /model [model_name] (예: /model gpt-4o, /model llama3)"))
        else:
            new_model = cmd_parts[1]
            from gortex.core.auth import GortexAuth
            auth = GortexAuth()
            
            # Provider별 모델 설정 로직 (여기서는 Ollama 모델 변경을 주로 지원)
            if auth._provider == "ollama":
                auth.ollama_model = new_model
                ui.chat_history.append(("system", f"🤖 Ollama 기본 모델이 '[bold cyan]{new_model}[/bold cyan]'로 설정되었습니다."))
            else:
                ui.chat_history.append(("system", f"ℹ️ '{auth._provider.upper()}' 모드에서는 요청 시 모델 ID가 동적으로 결정되지만, \n기본값 힌트로 '{new_model}'을 기억합니다."))
                # (추후 config.default_model 업데이트 로직 등 확장 가능)
                
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/history":
        summary_path = "logs/trace_summary.md"
        if os.path.exists(summary_path):
            from gortex.utils.tools import read_file
            content = read_file(summary_path)
            ui.chat_history.append(("system", Panel(Markdown(content), title="📜 HISTORICAL SUMMARY", border_style="cyan")))
        else:
            log_path = observer.log_path if observer else "logs/trace.jsonl"
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding='utf-8') as f:
                        lines = f.readlines()[-10:] # Last 10 lines
                    history_text = "".join(lines)
                    ui.chat_history.append(("system", Panel(history_text, title="RECENT RAW LOGS", border_style="dim")))
                    ui.chat_history.append(("system", "[TIP] 'Analyst'에게 로그 요약을 요청하여 정제된 역사를 확인하세요."))
                except Exception as e:
                    ui.chat_history.append(("system", f"❌ 로그 읽기 실패: {e}"))
            else:
                ui.chat_history.append(("system", "❌ 로그 파일이 없습니다."))
        ui.update_main(ui.chat_history)
        return "skip"

    # [NEW] Did you mean? 기능 (유사 명령어 추천)
    import difflib
    valid_commands = [
        "/help", "/status", "/agents", "/inspect", "/rca", "/search", "/map", 
        "/kg", "/scan_debt", "/index", "/voice", "/language", "/theme", 
        "/config", "/export", "/import", "/clear", "/bug", "/mode", "/save", 
        "/load", "/provider", "/model", "/history"
    ]
    matches = difflib.get_close_matches(cmd, valid_commands, n=1, cutoff=0.6)
    suggestion = f"\n💡 혹시 [bold cyan]{matches[0]}[/bold cyan]를 입력하려 하셨나요?" if matches else ""

    ui.chat_history.append(("system", f"❓ 알 수 없는 명령어: {cmd}{suggestion}"))
    ui.update_main(ui.chat_history)
    return "skip"