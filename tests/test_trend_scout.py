import unittest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from gortex.agents.trend_scout import TrendScoutAgent, trend_scout_node

class TestGortexTrendScout(unittest.TestCase):
    @patch('gortex.agents.trend_scout.LLMFactory')
    @patch('gortex.agents.trend_scout.ResearcherAgent')
    @patch('gortex.agents.trend_scout.TrendScoutAgent.should_scan')
    def test_trend_scout_node_flow(self, mock_should_scan, mock_researcher_cls, mock_factory):
        """TrendScout 노드 실행 흐름 테스트"""
        mock_should_scan.return_value = True
        
        # 1. Mock Backend Setup
        mock_backend = MagicMock()
        mock_backend.supports_structured_output.return_value = False
        
        # 트렌드 분석 및 보안 분석 응답 모킹
        mock_backend.generate.side_effect = [
            json.dumps({"models": [{"name": "GPT-5", "status": "leaked", "note": "Huge"}], "patterns": []}),
            json.dumps({"vulnerabilities_found": False}),
            json.dumps({"candidates": []})
        ]
        mock_factory.get_default_backend.return_value = mock_backend

        # 2. Mock Researcher
        mock_researcher = mock_researcher_cls.return_value
        mock_researcher.search_and_summarize = AsyncMock(return_value="search result")

        # 3. State
        state = {
            "messages": [],
            "file_cache": {},
            "assigned_model": "test-model"
        }

        # 4. Execute
        result = trend_scout_node(state)

        # 5. Verify
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("GPT-5", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()