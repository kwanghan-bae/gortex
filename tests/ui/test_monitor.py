
import unittest
from unittest.mock import MagicMock, patch
from rich.panel import Panel
from gortex.ui.components.monitor import SystemMonitor

class TestSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.console = MagicMock()
        self.monitor = SystemMonitor(self.console)

    @patch('gortex.ui.components.monitor.psutil')
    def test_collect_metrics(self, mock_psutil):
        """시스템 메트릭 수집 기능 테스트"""
        # Mock psutil
        mock_psutil.cpu_percent.return_value = 45.5
        mock_psutil.virtual_memory.return_value.percent = 60.2
        
        # 가상의 Gortex 상태
        state_vars = {
            "agent_energy": 80,
            "total_tokens": 1500,
            "total_cost": 0.05
        }
        
        metrics = self.monitor.collect_metrics(state_vars)
        
        self.assertEqual(metrics['cpu'], 45.5)
        self.assertEqual(metrics['memory'], 60.2)
        self.assertEqual(metrics['energy'], 80)
        self.assertEqual(metrics['tokens'], 1500)
        self.assertEqual(metrics['cost'], 0.05)

    def test_render_returns_panel(self):
        """render 메서드가 Panel 객체를 반환하는지 테스트"""
        # 가짜 데이터 주입
        self.monitor.latest_metrics = {
            'cpu': 10.0,
            'memory': 20.0,
            'energy': 90,
            'tokens': 100,
            'cost': 0.001
        }
        
        result = self.monitor.render()
        self.assertIsInstance(result, Panel)

if __name__ == '__main__':
    unittest.main()
