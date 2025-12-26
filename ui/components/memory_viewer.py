
from typing import List, Dict, Optional
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group
from rich import box
from gortex.ui.themes.palette import Palette

class MemoryViewer:
    """Vector Memory(ChromaDB)의 내용을 시각화하여 탐색하는 컴포넌트"""

    def __init__(self, console: Console, vector_store):
        """
        Args:
            console (Console): Rich console instance
            vector_store: Gortex VectorStore instance (must have search method)
        """
        self.console = console
        self.vector_store = vector_store
        self.memories: List[Dict] = []
        self.last_query = ""

    def fetch_memories(self, query: str = "", limit: int = 10) -> List[Dict]:
        """벡터 스토어에서 메모리를 검색합니다."""
        self.last_query = query
        try:
            # VectorStore.search(query, limit) 인터페이스 가정
            # 실제 구현에서는 search_similarity 등을 사용해야 할 수 있음. 
            # 여기서는 인터페이스 추상화에 의존.
            self.memories = self.vector_store.search(query=query, limit=limit)
            return self.memories
        except Exception as e:
            self.memories = []
            return []

    def render(self) -> Panel:
        """현재 로드된 메모리를 테이블 형태로 렌더링합니다."""
        if not self.memories:
            msg = "📭 No memories found." if self.last_query else "Ready to explore. Use /memory [query] to search."
            return Panel(Text(msg, style=Palette.GRAY), title="Memory Explorer", border_style="dim")

        table = Table(title=f"🔍 Memory Search: '{self.last_query}'" if self.last_query else "📚 Recent Memories",
                      box=box.SIMPLE_HEAD, expand=True)

        table.add_column("ID", style="dim", width=8)
        table.add_column("Sync", justify="center", width=6)
        table.add_column("Content", style="cyan", ratio=3)
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Date", style="green", width=12)

        for mem in self.memories:
            meta = mem.get("metadata", {})
            content = mem.get("content", "")
            is_global = mem.get("is_global", False)
            sync_icon = f"[bold {Palette.GREEN}]🌐[/]" if is_global else f"[{Palette.GRAY}]🏠[/]"
            
            # 긴 내용 자르기
            if len(content) > 80: content = content[:77] + "..."
            
            table.add_row(
                str(mem.get("id", "N/A"))[:8],
                sync_icon,
                content,
                meta.get("type", "General"),
                meta.get("created_at", meta.get("timestamp", ""))[:10]
            )

        return Panel(
            table,
            title=f" [bold {Palette.MAGENTA}]Vector Memory Explorer[/] ",
            border_style=Palette.MAGENTA,
            box=box.ROUNDED
        )
