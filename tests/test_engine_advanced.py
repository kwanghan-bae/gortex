import unittest
import asyncio
from unittest.mock import MagicMock
from gortex.core.engine import GortexEngine

class TestGortexEngineAdvanced(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        self.ui.web_manager = MagicMock()
        self.ui.web_manager.broadcast = unittest.mock.AsyncMock()
        self.observer = MagicMock()
        self.vocal = MagicMock()
        self.engine = GortexEngine(self.ui, self.observer, self.vocal)
        self.state_vars = {
            "last_event_id": "parent_123", 
            "session_cache": {},
            "agent_energy": 100,
            "last_efficiency": 100.0
        }

    def run_async(self, coro):
        return asyncio.run(coro)

    def test_causal_chain_integrity(self):
        """노드 실행 시 이전 이벤트 ID를 부모로 하여 새로운 이벤트가 기록되는지 테스트"""
        self.observer.log_event.return_value = "child_456"
        
        output = {"goal": "Test Goal"}
        self.run_async(self.engine.process_node_output("coder", output, self.state_vars))
        
        # log_event 호출 시 cause_id가 "parent_123"으로 전달되었는지 확인
        self.observer.log_event.assert_called()
        args, kwargs = self.observer.log_event.call_args
        self.assertEqual(kwargs["cause_id"], "parent_123")
        self.assertEqual(self.state_vars["last_event_id"], "child_456")

    def test_ui_mode_switching(self):
        """output에 ui_mode가 포함된 경우 UI 레이아웃이 전환되는지 테스트"""
        output = {"ui_mode": "debugging"}
        self.run_async(self.engine.process_node_output("analyst", output, self.state_vars))
        
        self.ui.set_layout_mode.assert_called_with("debugging")

    def test_impact_highlight_streaming(self):
        """영향 분석 데이터가 있을 때 3D 하이라이트가 포함된 데이터가 전송되는지 테스트"""
        output = {"impact_analysis": {"target": "main.py", "direct": [], "indirect": []}}
        # ThreeJsBridge의 apply_impact_highlight가 호출되는지 확인 (Mock 필요 시 추가)
        self.run_async(self.engine.process_node_output("planner", output, self.state_vars))
        
        # broadcast가 호출되었는지 확인
        self.assertTrue(self.ui.web_manager.broadcast.called)

if __name__ == '__main__':
    unittest.main()
