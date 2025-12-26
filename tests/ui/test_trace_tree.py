
import unittest
from rich.tree import Tree
from gortex.ui.components.trace_tree import TraceTreeRenderer

class TestTraceTreeRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = TraceTreeRenderer()

    def test_build_tree_standard_log(self):
        """표준 로그 리스트를 트리로 변환하는지 테스트"""
        logs = [
            {"agent": "Planner", "event": "Goal Decomposed", "details": {"subtasks": 3}},
            {"agent": "Coder", "event": "File Created", "details": {"path": "test.py"}}
        ]
        
        tree = self.renderer.build_tree(logs, title="Execution Trace")
        
        if hasattr(tree.label, "plain"):
            self.assertEqual(tree.label.plain, "Execution Trace")
        else:
            # Rich Tree label이 문자열인 경우 마크업이 포함될 수 있음
            self.assertIn("Execution Trace", str(tree.label))
            
        self.assertEqual(len(tree.children), 2)
        # 자식 노드의 라벨 검증 (구현 방식에 따라 다를 수 있으므로 포함 여부만 확인)
        self.assertIn("Planner", str(tree.children[0].label))

    def test_build_tree_empty(self):
        """빈 로그 처리 테스트"""
        tree = self.renderer.build_tree([])
        self.assertIsInstance(tree, Tree)
        # "No trace data" 메시지 노드가 하나 추가됨
        self.assertEqual(len(tree.children), 1)

    def test_build_hierarchical_tree(self):
        """(고급) parent_id가 있는 로그의 계층 구조 시각화 테스트"""
        # Note: 현재 Gortex 로그 구조가 단순 선형 리스트라도, 추후 trace_id/parent_id 지원을 염두
        logs = [
            {"id": "1", "agent": "Manager", "event": "Start"},
            {"id": "2", "parent_id": "1", "agent": "Worker", "event": "Task"}
        ]
        tree = self.renderer.build_tree(logs)
        # 단순히 렌더링 에러가 안 나는지 확인 (Phase 3 초기 스펙은 선형 표시도 허용)
        self.assertIsInstance(tree, Tree)

if __name__ == '__main__':
    unittest.main()
