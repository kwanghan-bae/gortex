import unittest
from unittest.mock import MagicMock, patch
from gortex.core.state import GortexState
from gortex.utils.memory import ContextPruner, summarizer_node

class TestContextPruning(unittest.TestCase):
    def setUp(self):
        self.state: GortexState = {
            "messages": [
                ("system", "Project summary"), # Must keep (0)
                ("user", "Old unrelated talk"), # Low relevance
                ("ai", "I am a robot"), # Low relevance
                ("user", "Fix bug in engine.py"), # Related to plan
                ("ai", "Starting bug fix"), # Related to plan
                ("ai", "Last 1"), # Must keep (-4)
                ("ai", "Last 2"), # Must keep (-3)
                ("ai", "Last 3"), # Must keep (-2)
                ("ai", "Last 4")  # Must keep (-1)
            ],
            "plan": ["Fix critical bug in core/engine.py"],
            "pinned_messages": []
        }

    @patch('gortex.agents.analyst.base.AnalystAgent.rank_context_relevance')
    def test_semantic_pruning_logic(self, mock_rank):
        """시맨틱 점수에 따른 노이즈 메시지 제거 테스트"""
        # 1. 랭킹 점수 모킹: 1번, 2번 메시지는 낮은 점수, 3번, 4번은 높은 점수
        # eval_indices 는 [1, 2, 3, 4] 임.
        mock_rank.return_value = [0.1, 0.1, 0.9, 0.9]
        
        pruner = ContextPruner(self.state)
        # 9개 메시지 중 7개로 줄이기 시도 (2개 삭제)
        new_messages = pruner.prune(target_count=7)
        
        self.assertEqual(len(new_messages), 7)
        
        # 0번(Summary)과 최신 4개는 반드시 있어야 함
        self.assertEqual(new_messages[0][1], "Project summary")
        self.assertEqual(new_messages[-1][1], "Last 4")
        
        # 1번, 2번(노이즈)이 삭제되었는지 확인
        contents = [m[1] for m in new_messages]
        self.assertNotIn("Old unrelated talk", contents)
        self.assertNotIn("I am a robot", contents)
        
        # 3번, 4번(관련성 높음)은 보존되어야 함
        self.assertIn("Fix bug in engine.py", contents)

    def test_pruning_protection_rules(self):
        """최신 메시지 보존 규칙 테스트"""
        pruner = ContextPruner(self.state)
        # target_count를 극단적으로 낮게 잡아도 최소 보존 개수는 유지되어야 함
        with patch.object(pruner, 'get_semantic_scores', return_value=[0.1]*4):
            new_messages = pruner.prune(target_count=3)
            
            # 최소 보존: 0번 + 최신 4개 = 5개
            # (구현상 target_count보다 보존 메시지가 많으면 보존 메시지 위주로 남음)
            self.assertGreaterEqual(len(new_messages), 5)

if __name__ == '__main__':
    unittest.main()