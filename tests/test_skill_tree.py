import unittest
from gortex.utils.economy import get_economy_manager
from gortex.core.registry import registry
from gortex.core.state import GortexState

class TestSkillTree(unittest.TestCase):
    def setUp(self):
        self.economy = get_economy_manager()
        self.state: GortexState = {"agent_economy": {}, "achievements": []}

    def test_skill_gain_and_rank_up(self):
        """작업 성공에 따른 스킬 누적 및 칭호 승급 테스트"""
        agent = "Coder"
        category = "Coding"
        
        # 1. 초기 포인트 0
        self.economy.initialize_agent(self.state["agent_economy"], agent)
        self.assertEqual(self.state["agent_economy"][agent.lower()]["skill_points"].get(category), 0)
        
        # 2. 고품질 고난도 작업 10회 성공 (회당 60점 가정: 10 * 2.0 * 3.0)
        for _ in range(10):
            self.economy.update_skill_points(self.state, agent, category, quality_score=2.0, difficulty=3.0)
            
        # 3. 600점 도달 및 Journeyman 승급 확인
        final_pts = self.state["agent_economy"][agent.lower()]["skill_points"][category]
        self.assertEqual(final_pts, 600)
        
        # 업적 기록 확인
        achievements = [a["text"] for a in self.state.get("achievements", [])]
        self.assertTrue(any("Journeyman" in a for a in achievements))

    def test_tool_unlocking_by_skill(self):
        """스킬 레벨에 따른 고급 도구 잠금 해제 테스트"""
        agent = "Analyst"
        tool = "apply_patch" # Requires 500 pts in Coding
        
        # 1. 포인트 부족 시 거부
        economy_data = {
            "analyst": {
                "skill_points": {"Coding": 100}
            }
        }
        self.assertFalse(registry.is_tool_permitted(agent, tool, economy_data))
        
        # 2. 500점 이상 시 허용
        economy_data["analyst"]["skill_points"]["Coding"] = 550
        self.assertTrue(registry.is_tool_permitted(agent, tool, economy_data))

    def test_general_tools_always_permitted(self):
        """일반 도구는 무조건 허용되는지 확인"""
        self.assertTrue(registry.is_tool_permitted("Any", "read_file", {}))

if __name__ == '__main__':
    unittest.main()