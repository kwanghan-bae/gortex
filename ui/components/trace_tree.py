
from typing import List, Dict, Optional
from rich.tree import Tree
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box
from gortex.ui.themes.palette import Palette, get_agent_style
import json

class TraceTreeRenderer:
    """에이전트 로그를 Rich Tree 구조로 시각화하는 렌더러"""

    def build_tree(self, logs: List[Dict], title: str = "Execution Trace") -> Tree:
        """로그 리스트를 트리 객체로 변환합니다."""
        root = Tree(f"🌱 [bold cyan]{title}[/bold cyan]")
        
        if not logs:
            root.add("[dim]No trace data available.[/dim]")
            return root

        # 1. 딕셔너리 매핑 (ID 기반 계층 구조 지원)
        node_map = {}
        # 먼저 모든 노드를 생성
        for log in logs:
            log_id = log.get("id", str(id(log))) # ID 없으면 메모리 주소 사용(임시)
            node_label = self._create_label(log)
            # parent_id가 없으면 루트에 직접 추가될 것임
            # 하지만 트리 구조 생성을 위해 먼저 Tree 객체로Wrapping하지 않고, 
            # 나중에 관계를 맺어줌. Rich Tree는 add()가 자식 Tree를 리턴함.
            # 여기서는 부모-자식 관계가 명확하지 않은 단순 선형 로그일 경우가 많으므로
            # 선형 순회를 기본으로 하되, parent_id가 보이면 중첩.
        
        # 간단한 선형 + 일부 계층 처리 방식
        # (복잡한 그래프보다는 로그 스트림의 시각화에 집중)
        
        for log in logs:
            agent = log.get("agent", "Unknown")
            event = log.get("event", "")
            details = log.get("details", {})
            
            style = get_agent_style(agent)
            label = Text.assemble(
                (f"[{agent}] ", f"bold {style}"),
                (f"{event}", "white"),
            )
            
            branch = root.add(label)
            
            # 상세 정보가 있으면 하위 노드로 추가
            if details:
                # 텍스트나 간단한 딕셔너리는 보기 좋게 변환
                if isinstance(details, str):
                    branch.add(Text(details, style="dim"))
                elif isinstance(details, dict):
                     for k, v in details.items():
                         branch.add(f"[dim]{k}: {v}[/dim]")

        return root

    def _create_label(self, log):
        agent = log.get("agent", "System")
        event = log.get("event", "Event")
        return f"[{agent}] {event}"

    def render_panel(self, logs: List[Dict]) -> Panel:
        """Dashboard용 Panel 형태로 렌더링"""
        tree = self.build_tree(logs)
        return Panel(
            tree,
            title=f" [bold {Palette.MAGENTA}]Logic Tracer[/] ",
            border_style=Palette.MAGENTA,
            box=box.ROUNDED,
            padding=(1, 2)
        )
