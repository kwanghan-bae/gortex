import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from gortex.core.graph import (
    compile_gortex_graph,
    route_after_summary,
    route_coder,
    route_manager,
)

class DummyState:
    def __init__(self, data):
        self._data = data

    def get(self, key, default=None):
        return self._data.get(key, default)

class TestGraphRouting(unittest.TestCase):
    @patch("gortex.core.graph.count_tokens", return_value=1)
    def test_route_manager_by_message_count(self, _):
        messages = [SimpleNamespace(content="a") for _ in range(12)]
        state = DummyState({"messages": messages, "next_node": "planner"})
        self.assertEqual(route_manager(state), "summarizer")

    @patch("gortex.core.graph.count_tokens", return_value=2500)
    def test_route_manager_by_token_volume(self, _):
        messages = [SimpleNamespace(content="a") for _ in range(3)]
        state = DummyState({"messages": messages, "next_node": "planner"})
        self.assertEqual(route_manager(state), "summarizer")

    @patch("gortex.core.graph.count_tokens", return_value=1)
    def test_route_manager_respects_next_node(self, _):
        messages = [SimpleNamespace(content="a")]
        state = DummyState({"messages": messages, "next_node": "researcher"})
        self.assertEqual(route_manager(state), "researcher")

    def test_route_after_summary_returns_target(self):
        state = DummyState({"next_node": "planner"})
        self.assertEqual(route_after_summary(state), "planner")

    def test_route_coder_handles_end_and_loop(self):
        self.assertEqual(route_coder(DummyState({"next_node": "__end__"})), "analyst")
        self.assertEqual(route_coder(DummyState({"next_node": "coder"})), "coder")

class DummyGraph:
    def __init__(self, state_cls):
        self.state_cls = state_cls
        self.nodes = []
        self.edges = []
        self.conditionals = []
        self.compiled = False
        self.checkpointer = None

    def add_node(self, name, func):
        self.nodes.append(name)

    def add_edge(self, src, dst):
        self.edges.append((src, dst))

    def add_conditional_edges(self, node, router, mapping):
        self.conditionals.append((node, mapping))

    def compile(self, checkpointer=None):
        self.compiled = True
        self.checkpointer = checkpointer
        return self

class TestGraphCompilation(unittest.TestCase):
    def test_compile_builds_workflow(self):
        dummy_checkpointer = MagicMock()
        with patch("gortex.core.graph.StateGraph", new=DummyGraph), \
             patch("langgraph.checkpoint.memory.MemorySaver", return_value=dummy_checkpointer):
            compiled = compile_gortex_graph()

        self.assertTrue(compiled.compiled)
        self.assertEqual(compiled.checkpointer, dummy_checkpointer)
        self.assertIn("manager", compiled.nodes)
        conditional_map = {node: mapping for node, mapping in compiled.conditionals}
        self.assertIn("manager", conditional_map)
        self.assertEqual(conditional_map["manager"]["summarizer"], "summarizer")
