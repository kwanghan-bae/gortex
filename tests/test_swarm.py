import unittest
from unittest.mock import MagicMock, patch
from gortex.agents.swarm import swarm_node_async
import asyncio

class TestGortexSwarm(unittest.TestCase):
    
    @patch('gortex.agents.swarm.execute_parallel_task')
    @patch('gortex.agents.swarm.AnalystAgent')
    @patch('gortex.agents.swarm.GortexMessageQueue')
    def test_swarm_node_logic(self, mock_mq, mock_analyst_cls, mock_execute):
        """Swarm 노드의 비동기 로직 테스트"""
        # Setup Mocks
        mock_analyst = mock_analyst_cls.return_value
        mock_analyst.calculate_efficiency_score.return_value = 85.0
        
        # 가상의 병렬 작업 결과 반환
        mock_execute.side_effect = [
            {"task": "Task A", "success": True, "certainty": 0.8, "risk": 0.1, "report": "Report A", "persona": "Innovation"},
            {"task": "Task B", "success": True, "certainty": 0.7, "risk": 0.0, "report": "Report B", "persona": "Stability"}
        ]
        
        state = {
            "plan": ["Task A", "Task B"], # 토론 주제
            "active_constraints": []
        }
        
        # Run Async Function
        result = asyncio.run(swarm_node_async(state))
        
        # Assertions
        self.assertEqual(len(result["debate_context"]), 2)
        # 토론 키워드가 없으므로 기본 manager로 복귀
        self.assertEqual(result["next_node"], "manager") 
        self.assertIn("Swarm", result["messages"][0][1])
        
    @patch('gortex.agents.swarm.execute_parallel_task')
    @patch('gortex.agents.swarm.AnalystAgent')
    @patch('gortex.agents.swarm.GortexMessageQueue')
    def test_swarm_debate_routing(self, mock_mq, mock_analyst_cls, mock_execute):
        """'토론' 키워드가 있을 때 Analyst로 라우팅되는지 테스트"""
        mock_analyst = mock_analyst_cls.return_value
        mock_analyst.calculate_efficiency_score.return_value = 85.0
        
        mock_execute.side_effect = [
            {"task": "Topic 1", "success": True, "certainty": 0.8, "risk": 0.1, "report": "A", "persona": "Innovation"},
            {"task": "Topic 1", "success": True, "certainty": 0.7, "risk": 0.0, "report": "B", "persona": "Stability"}
        ]
        
        state = {
            "plan": ["토론 주제 1", "토론 주제 2"], # '토론' 키워드 포함
            "active_constraints": []
        }
        
        result = asyncio.run(swarm_node_async(state))
        self.assertEqual(result["next_node"], "analyst")

if __name__ == '__main__':
    unittest.main()