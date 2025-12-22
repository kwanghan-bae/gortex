import unittest
from unittest.mock import MagicMock, patch
from ui.dashboard import DashboardUI

# We'll test the sparkline logic by importing it after we add it, 
# or we can define the expected behavior here.
# Since I haven't added render_sparkline to the file yet, I can't import it.
# I will proceed to modify the file first, then run this test.

class TestDashboardHealth(unittest.TestCase):
    def test_sparkline_logic(self):
        # This will be tested via the method I add to DashboardUI or standalone
        from ui.dashboard import render_sparkline
        data = [0, 50, 100]
        line = render_sparkline(data)
        self.assertEqual(len(line), 3)
        self.assertEqual(line[0], " ")
        self.assertEqual(line[2], "█")

    def test_update_sidebar_with_health(self):
        # We need to ensure EfficiencyMonitor is mocked correctly where it is IMPORTED.
        # Inside update_sidebar: `from gortex.utils.efficiency_monitor import EfficiencyMonitor`
        # Patching local imports is tricky. 
        # Better to mock sys.modules or use patch.dict
        
        # However, for this test, I'll rely on the fact that unit tests usually run in an environment 
        # where we can patch 'gortex.utils.efficiency_monitor.EfficiencyMonitor'.
        
        with patch('gortex.utils.efficiency_monitor.EfficiencyMonitor') as MockMonitor:
            mock_inst = MockMonitor.return_value
            mock_inst.get_health_history.return_value = [
                {"score": 90.0, "timestamp": "t2"},
                {"score": 80.0, "timestamp": "t1"}
            ]
            
            console = MagicMock()
            ui = DashboardUI(console)
            ui.update_sidebar()
            
            # Verify call
            mock_inst.get_health_history.assert_called()
