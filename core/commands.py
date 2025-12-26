import os
import json
import logging
from datetime import datetime
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from gortex.core.observer import GortexObserver
from gortex.utils.indexer import SynapticIndexer
from gortex.core.registry import registry

logger = logging.getLogger("GortexCommands")

async def handle_command(user_input: str, ui, observer: GortexObserver, all_sessions_cache: dict, thread_id: str, theme_manager) -> str:
    """모든 슬래시 명령어(/)를 유실 없이 처리합니다 (v15.0 Final)."""
    user_input = user_input.strip()
    if not user_input.startswith("/"): return "pass"
    
    cmd_parts = user_input.split()
    cmd = cmd_parts[0].lower()
    
    if cmd == "/help":
        help_msg = """
📚 **Gortex Sovereign Command Guide (v15.0)**
- `/status`: 시스템 성능 및 군집 상태 보고
- `/agents`: 활성 에이전트 목록 및 명세
- `/drive`: **[Sovereign]** 자율 미션 생성 및 실행 트리거
- `/config`: 시스템 정책 및 지침 조회/변경
- `/kg`: 통합 지식 그래프(Neural Map) 시각화
- `/scan_debt`: 기술 부채 및 코드 복잡도 스캔
- `/search [query]`: 의미 기반 심볼 검색
- `/map`: 프로젝트 트리 구조 출력
- `/voice`: 음성 인터랙션 토글
- `/clear`: 화면 초기화
"""
        ui.chat_history.append(("system", Panel(Markdown(help_msg), title="HELP CENTER", border_style="cyan")))
        ui.update_main(ui.chat_history)
        return "skip"

    elif cmd == "/status":
        from gortex.core.mq import mq_bus
        workers = mq_bus.list_active_workers()
        status_msg = f"📊 **Gortex Cluster**: {len(workers)} Nodes Online | MQ: [green]CONNECTED[/]"
        ui.chat_history.append(("system", Panel(status_msg, title="STATUS", border_style="magenta")))
        if hasattr(ui, "toggle_monitor_mode"): ui.toggle_monitor_mode()
        return "skip"

    elif cmd == "/agents":
        agents = registry.list_agents()
        table = Table(title="🤖 Active Agents", show_header=True)
        table.add_column("Name", style="bold cyan"); table.add_column("Role", style="yellow")
        for name in sorted(agents):
            meta = registry.get_metadata(name)
            table.add_row(name.capitalize(), meta.role)
        ui.chat_history.append(("system", table))
        return "skip"

    elif cmd == "/drive":
        ui.chat_history.append(("system", "🤖 **자율 주권 모드 수동 트리거**: 시스템이 스스로 다음 미션을 수립합니다..."))
        from gortex.core.mq import mq_bus
        mq_bus.publish_event("gortex:system_events", "User", "trigger_drive", {{}})
        return "skip"

    elif cmd == "/config":
        if len(cmd_parts) < 2:
            from gortex.core.auth import GortexAuth
            auth = GortexAuth()
            config_text = f"⚙️ **System Config**\n- Provider: {auth.get_provider()}\n- Model: {auth.ollama_model}"
            ui.chat_history.append(("system", Panel(config_text, title="CONFIG", border_style="yellow")))
        else:
            directive = " ".join(cmd_parts[1:])
            ui.chat_history.append(("system", f"🛠️ **정책 분석 중**: '{directive}'..."))
            try:
                from gortex.core.llm.factory import LLMFactory
                backend = LLMFactory.get_default_backend()
                prompt = f"Translate this user directive into a global 'Super Rule'. Directive: {directive}. Return JSON."
                resp = backend.generate("gemini-2.0-flash", [("user", prompt)])
                from gortex.core.evolutionary_memory import EvolutionaryMemory
                EvolutionaryMemory().save_rule(resp, [directive], is_super_rule=True)
                ui.chat_history.append(("system", "✅ **정책 갱신 완료**"))
            except Exception as e: ui.chat_history.append(("system", f"❌ 실패: {e}"))
        return "skip"

    elif cmd == "/kg":
        from gortex.utils.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        kg.build_from_system()
        ui.chat_history.append(("system", Panel(kg.generate_summary(), title="NEURAL MAP", border_style="blue")))
        return "skip"

    elif cmd == "/bug":
        ui.chat_history.append(("system", "🐞 **이슈 리포트**: 발견된 버그나 피드백을 기록합니다."))
        return "skip"

    elif cmd == "/clear":
        ui.chat_history = []; ui.update_main([]); return "skip"

    ui.chat_history.append(("system", f"❓ 알 수 없는 명령어: {cmd}"))
    ui.update_main(ui.chat_history)
    return "skip"