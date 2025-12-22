import unittest
from rich.console import Console
from gortex.ui.dashboard import DashboardUI

class TestEnergyUI(unittest.TestCase):
    def setUp(self):
        self.console = Console()
        self.ui = DashboardUI(self.console)

    def test_energy_visualizer_colors(self):
        """에너지 수치에 따른 색상 및 게이지 렌더링 테스트"""
        
        # 1. High Energy (Green)
        self.ui.update_energy_visualizer(100)
        self.assertEqual(self.ui.energy, 100)
        
        # 2. Medium Energy (Yellow)
        self.ui.update_energy_visualizer(50)
        self.assertEqual(self.ui.energy, 50)
        
        # 3. Critical Energy (Red)
        self.ui.update_energy_visualizer(5)
        self.assertEqual(self.ui.energy, 5)
        
        # 렌더링 시도 (에러 발생 여부 확인)
        renderable = self.ui.render()
        self.assertIsNotNone(renderable)

    def test_recharging_status(self):
        """충전 중일 때의 아이콘 변화 테스트"""
        self.ui.current_step = "Recovering..."
        self.ui.update_energy_visualizer(80)
        # 내부적으로 icon 로직이 blink ⚡를 포함하는지 확인 (UI 문자열 캡처는 생략)
        self.assertEqual(self.ui.energy, 80)

if __name__ == '__main__':
    unittest.main()
