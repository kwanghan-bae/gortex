import unittest
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from gortex.core.graph import route_manager, route_after_summary, route_coder, compile_gortex_graph

class DummyState(dict):
    def __getattr__(self, name):
        return self.get(name)

class DummyGraph:
    def __init__(self, state_schema):
        self.nodes = {}
        self.edges = []
        self.checkpointer = None
    def add_node(self, name, func): self.nodes[name] = func
    def add_edge(self, start, end): self.edges.append((start, end))
    def add_conditional_edges(self, start, func, mapping): pass
    def compile(self, checkpointer=None):
        self.checkpointer = checkpointer
        return self
    @property
    def compiled(self): return True

class TestGraphRouting(unittest.TestCase):
    @patch("gortex.core.graph.count_tokens", return_value=1)
    def test_route_manager_by_message_count(self, _):
        # Set LLM_BACKEND to ollama to have lower threshold (8)
        with patch.dict(os.environ, {"LLM_BACKEND": "ollama"}):
            messages = [SimpleNamespace(content="a") for _ in range(10)]
            state = DummyState({"messages": messages, "next_node": "planner"})
            self.assertEqual(route_manager(state), "summarizer")

    @patch("gortex.core.graph.count_tokens", return_value=4000)
    def test_route_manager_by_token_volume(self, _):
        with patch.dict(os.environ, {"LLM_BACKEND": "ollama"}):
            messages = [SimpleNamespace(content="a")]
            state = DummyState({"messages": messages, "next_node": "planner"})
            self.assertEqual(route_manager(state), "summarizer")

    def test_route_after_summary_returns_to_target(self):
        state = DummyState({"next_node": "researcher"})
        self.assertEqual(route_after_summary(state), "researcher")

    def test_route_coder_handles_end_and_loop(self):
        # Trigger analyst via error message
        state = DummyState({
            "messages": [("ai", "❌ Error occurred")],
            "next_node": "coder",
            "coder_iteration": 0
        })
        self.assertEqual(route_coder(state), "analyst")
        
        # Trigger swarm via repeated failure
        state["messages"] = [("ai", "Success")]
        state["coder_iteration"] = 5
        self.assertEqual(route_coder(state), "swarm")

class TestGraphCompilation(unittest.TestCase):
    def test_compile_builds_workflow(self):
        dummy_checkpointer = MagicMock()
        with patch("gortex.core.graph.StateGraph", new=DummyGraph):
            # Pass checkpointer explicitly
            compiled = compile_gortex_graph(checkpointer=dummy_checkpointer)
    
        self.assertTrue(compiled.compiled)
        self.assertEqual(compiled.checkpointer, dummy_checkpointer)

if __name__ == "__main__":
    unittest.main()