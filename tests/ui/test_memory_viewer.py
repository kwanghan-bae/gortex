
import unittest
from unittest.mock import MagicMock
from rich.panel import Panel
from rich.table import Table
from gortex.ui.components.memory_viewer import MemoryViewer

class TestMemoryViewer(unittest.TestCase):
    def setUp(self):
        self.mock_vector_store = MagicMock()
        self.console = MagicMock()
        self.viewer = MemoryViewer(self.console, self.mock_vector_store)

    def test_fetch_memories_default(self):
        """기본 검색 동작 테스트 (최신순)"""
        # Mocking return value
        self.mock_vector_store.search.return_value = [
            {"id": "doc1", "content": "memory 1", "metadata": {"created_at": "2024-01-01"}},
            {"id": "doc2", "content": "memory 2", "metadata": {"created_at": "2024-01-02"}}
        ]
        
        memories = self.viewer.fetch_memories(limit=5)
        
        self.mock_vector_store.search.assert_called_with(query="", limit=5)
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0]['id'], "doc1")

    def test_render_with_data(self):
        """데이터가 있을 때 테이블 렌더링 테스트"""
        self.viewer.memories = [
            {"id": "1", "content": "test memory", "metadata": {"type": "fact", "confidence": 0.9}}
        ]
        
        panel = self.viewer.render()
        
        self.assertIsInstance(panel, Panel)
        self.assertIsInstance(panel.renderable, Table)
        # Table 컬럼 확인은 rich 객체 구조상 복잡하므로 타입 체크 위주로 진행

    def test_render_empty(self):
        """데이터가 없을 때 안내 메시지 렌더링 테스트"""
        self.viewer.memories = []
        panel = self.viewer.render()
        
        self.assertIsInstance(panel, Panel)
        # Empty state should be rendered
        
if __name__ == '__main__':
    unittest.main()
