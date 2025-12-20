import unittest
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock
from gortex.agents.trend_scout import TrendScoutAgent, trend_scout_node

class TestGortexTrendScout(unittest.TestCase):
    def setUp(self):
        self.radar_path = "test_radar.json"
        if os.path.exists(self.radar_path):
            os.remove(self.radar_path)

    def tearDown(self):
        if os.path.exists(self.radar_path):
            os.remove(self.radar_path)

    def test_should_scan(self):
        """스캔 주기 판정 테스트"""
        scout = TrendScoutAgent(radar_path=self.radar_path)
        # 데이터가 없으면 무조건 True
        self.assertTrue(scout.should_scan())
        
        # 최근 스캔 기록 추가 (1시간 전)
        from datetime import datetime, timedelta
        scout.radar_data["last_scan"] = (datetime.now() - timedelta(hours=1)).isoformat()
        self.assertFalse(scout.should_scan(interval_hours=24))
        
        # 25시간 전 스캔 기록
        scout.radar_data["last_scan"] = (datetime.now() - timedelta(hours=25)).isoformat()
        self.assertTrue(scout.should_scan(interval_hours=24))

    @patch('gortex.agents.trend_scout.ResearcherAgent')
    @patch('gortex.agents.trend_scout.GortexAuth')
    def test_trend_scout_node_flow(self, mock_auth_cls, mock_researcher_cls):
        """TrendScout 노드 실행 흐름 테스트"""
        mock_auth = mock_auth_cls.return_value
        mock_res = MagicMock()
        mock_res.text = json.dumps({
            "models": [{"name": "Gemini 2.0", "status": "new", "note": "Faster"}],
            "patterns": [{"topic": "Chain of Thought", "summary": "Improves reasoning"}]
        })
        mock_auth.generate.return_value = mock_res
        
        mock_researcher = mock_researcher_cls.return_value
        mock_researcher.search_and_summarize = AsyncMock(return_value="Scraped data")

        # Input State
        state = {"messages": []}
        
        # Execute
        with patch.dict(os.environ, {"TREND_SCAN_INTERVAL_HOURS": "0"}): # 무조건 스캔
            result = trend_scout_node(state)
            
        self.assertEqual(result["next_node"], "manager")
        self.assertIn("Gemini 2.0", result["messages"][0][1])

if __name__ == '__main__':
    unittest.main()
