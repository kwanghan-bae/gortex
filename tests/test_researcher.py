import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from gortex.agents.researcher import researcher_node

class TestGortexResearcher(unittest.TestCase):
    
    @patch('gortex.agents.researcher.GortexAuth')
    @patch('gortex.agents.researcher.ResearcherAgent')
    def test_researcher_node_flow(self, mock_agent_cls, mock_auth_cls):
        """Researcher 노드의 전체 흐름(쿼리 추출 -> 검색 -> 요약) 테스트"""
        
        # 1. Mock Auth Setup
        mock_auth = mock_auth_cls.return_value
        # 첫 번째 호출 (쿼리 추출)
        mock_query_res = MagicMock()
        mock_query_res.text = "test query"
        # 두 번째 호출 (요약)
        mock_summary_res = MagicMock()
        mock_summary_res.text = "test summary"
        
        mock_auth.generate.side_effect = [mock_query_res, mock_summary_res]

        # 2. Mock ResearcherAgent Setup
        mock_agent = mock_agent_cls.return_value
        mock_agent.search_and_summarize = AsyncMock(return_value="raw search result")

        # 3. Input State
        state = {
            "messages": [MagicMock(content="오늘 날씨 알려줘")],
            "active_constraints": []
        }

        # 4. Execute
        result = researcher_node(state)

        # 5. Verify
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("test summary", result["messages"][0][1])
        mock_agent.search_and_summarize.assert_called_once()
        self.assertEqual(mock_auth.generate.call_count, 2)

if __name__ == '__main__':
    unittest.main()
