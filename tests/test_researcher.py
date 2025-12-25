import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.researcher import researcher_node

class TestGortexResearcher(unittest.TestCase):
    
    @unittest.skip("Async mocking issue in researcher_node")
    @patch('gortex.agents.researcher.LLMFactory')
    @patch('gortex.agents.researcher.ResearcherAgent')
    def test_researcher_node_flow(self, mock_factory, mock_agent_cls):
        """Researcher 노드의 전체 흐름(쿼리 추출 -> 검색 -> 요약) 테스트"""
        
        # 1. Mock Backend Setup
        mock_backend = MagicMock()
        mock_backend.supports_structured_output.return_value = False
        
        # 첫 번째 호출 (쿼리 추출)
        mock_query_res = json.dumps({"query": "test query", "is_docs_needed": False})
        # 두 번째 호출 (요약)
        mock_summary_res = "test summary"
        
        mock_backend.generate.side_effect = [mock_query_res, mock_summary_res]
        mock_factory.get_default_backend.return_value = mock_backend

        # 2. Mock ResearcherAgent Setup
        mock_agent = mock_agent_cls.return_value
        
        # asyncio.run()이나 loop.run_until_complete()에서 작동하도록 코루틴 함수 모킹
        async def mock_search(q): return "raw search result"
        mock_agent.search_and_summarize = mock_search

        # 3. Input State
        state = {
            "messages": [("user", "오늘 날씨 알려줘")],
            "active_constraints": []
        }

        # 4. Execute
        result = researcher_node(state)

        # 5. Verify
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("test summary", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()
