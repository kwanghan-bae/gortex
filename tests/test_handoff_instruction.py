import unittest
from unittest.mock import MagicMock, patch
from gortex.agents.planner import planner_node
from gortex.agents.coder import coder_node
from gortex.utils.prompt_loader import loader

class TestHandoffInstruction(unittest.TestCase):
    @patch("gortex.agents.planner.LLMFactory.get_default_backend")
    @patch("gortex.agents.planner.SynapticIndexer")
    @patch("gortex.agents.planner.EfficiencyMonitor")
    def test_planner_generates_handoff(self, mock_monitor, mock_indexer, mock_factory):
        """Planner가 핸드오프 지침을 생성하는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        plan_res = {
            "thought_process": "...", "impact_analysis": {"target": "t.py", "direct": [], "indirect": [], "risk_level": "low"},
            "internal_critique": "...", "thought_tree": [], "goal": "Goal",
            "steps": [{"id": 1, "action": "list_files", "target": ".", "reason": "R", "priority": 5, "is_essential": True}],
            "handoff_instruction": "Remember to check the config file."
        }
        mock_backend.generate.return_value = json.dumps(plan_res)
        mock_backend.supports_structured_output.return_value = False
        
        state = {"messages": [("user", "plan it")], "agent_energy": 100, "working_dir": "."}
        result = planner_node(state)
        
        self.assertEqual(result["handoff_instruction"], "Remember to check the config file.")

    @patch("gortex.agents.coder.LLMFactory.get_default_backend")
    @patch("gortex.agents.coder.SelfHealingMemory")
    @patch("gortex.agents.coder.EfficiencyMonitor")
    def test_coder_receives_handoff(self, mock_monitor, mock_healing, mock_factory):
        """Coder가 핸드오프 지침을 프롬프트에 포함하는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        mock_backend.generate.return_value = '{"thought": "ok", "status": "success"}'
        mock_backend.supports_structured_output.return_value = False
        
        state = {
            "messages": [("user", "code it")],
            "plan": [json.dumps({"action": "list_files", "target": "."})],
            "current_step": 0,
            "handoff_instruction": "USE_STRICT_MODE",
            "agent_energy": 100
        }
        
        with patch.object(loader, 'get_prompt', wraps=loader.get_prompt) as mock_get_prompt:
            coder_node(state)
            # handoff_instruction이 인자로 전달되었는지 확인
            args, kwargs = mock_get_prompt.call_args
            self.assertEqual(kwargs["handoff_instruction"], "USE_STRICT_MODE")

import json
if __name__ == '__main__':
    unittest.main()
