import unittest
import json
from unittest.mock import MagicMock, patch
from rich.console import Console
from gortex.ui.dashboard import DashboardUI
from gortex.core.commands import handle_command
from gortex.agents.analyst.base import AnalystAgent

class TestKnowledgeLineage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.console = Console()
        self.ui = DashboardUI(self.console)

    @patch("gortex.core.evolutionary_memory.EvolutionaryMemory")
    async def test_inspect_command_lineage(self, MockEvoMem):
        """/inspect 명령어가 지식 계보를 정확히 출력하는지 테스트"""
        # 1. 가상의 규칙 데이터 준비 (계보 포함)
        parent_id = "RULE_OLD_001"
        child_id = "RULE_EVOLVED_002"
        mock_rule = {
            "id": child_id,
            "learned_instruction": "Evolved instruction",
            "trigger_patterns": ["pattern"],
            "parent_rules": [parent_id],
            "usage_count": 5,
            "success_count": 4,
            "category": "coding"
        }
        
        # 2. 메모리 모킹
        mock_inst = MockEvoMem.return_value
        mock_inst.shards = {"coding": [mock_rule]}
        
        # 3. 명령어 실행
        observer = MagicMock()
        await handle_command(f"/inspect {child_id}", self.ui, observer, {}, "thread_1", MagicMock())
        
        # 4. 결과 검증
        # 채팅 히스토리에 Panel(상세정보)과 Tree(계보)가 추가되었어야 함
        panel = self.ui.chat_history[-2][1]
        self.assertIn(child_id, panel.title)
        
        tree = self.ui.chat_history[-1][1]
        self.assertIn(child_id, str(tree.label))
        self.assertTrue(any(parent_id in str(node.label) for node in tree.children))

    @patch("gortex.agents.analyst.base.LLMFactory.get_default_backend")
    def test_analyst_records_parents_during_optimization(self, mock_factory):
        """지식 최적화 시 부모 규칙 ID가 기록되는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # 병합 결과 모킹
        mock_backend.generate.return_value = json.dumps([
            {"instruction": "New Evolved Rule", "trigger_patterns": ["p"], "severity": 3}
        ])
        
        analyst = AnalystAgent()
        # 최소 5개의 규칙이 필요함 (임계치 충족)
        rules = [
            {"id": f"P{i}", "learned_instruction": f"Old {i}", "usage_count": 10, "success_count": 8, "category": "general"}
            for i in range(5)
        ]
        analyst.memory.shards["general"] = rules
        analyst.memory.memory = rules
        
        analyst.optimize_knowledge_base()
        
        # 생성된 규칙에 부모 ID들이 있는지 확인 (general 샤드 확인)
        new_rule = analyst.memory.shards["general"][0]
        self.assertIn("parent_rules", new_rule)
        self.assertEqual(len(new_rule["parent_rules"]), 5)
        self.assertIn("P0", new_rule["parent_rules"])

if __name__ == '__main__':
    unittest.main()