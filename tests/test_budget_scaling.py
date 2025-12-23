import unittest
from unittest.mock import MagicMock, patch
from gortex.core.engine import GortexEngine
from gortex.utils.resource_monitor import ResourceMonitor

class TestBudgetScaling(unittest.TestCase):
    def setUp(self):
        self.ui = MagicMock()
        self.engine = GortexEngine(ui=self.ui)
        # 실제 시스템 부하에 의존하지 않도록 모니터 가로채기
        self.engine.monitor = MagicMock(spec=ResourceMonitor)

    def test_concurrency_scaling_light_load(self):
        """저부하 상태에서 동시성 확장 테스트"""
        # 1. 'LIGHT' 부하 시뮬레이션
        self.engine.monitor.estimate_concurrency_limit.return_value = 4
        
        self.engine.update_scaling_policy()
        
        self.assertEqual(self.engine.max_concurrency, 4)
        self.ui.add_achievement.assert_called_with("Scaling to 4x")

    def test_concurrency_scaling_critical_load(self):
        """고부하 상태에서 동시성 축소 테스트"""
        # 1. 'CRITICAL' 부하 시뮬레이션
        self.engine.monitor.estimate_concurrency_limit.return_value = 1
        
        # 기본값 2에서 1로 변경 확인
        self.engine.update_scaling_policy()
        
        self.assertEqual(self.engine.max_concurrency, 1)
        self.ui.add_achievement.assert_called_with("Scaling to 1x")

    def test_no_change_no_ui_update(self):
        """정책 변화 없을 시 UI 업데이트 생략 테스트"""
        self.engine.max_concurrency = 2
        self.engine.monitor.estimate_concurrency_limit.return_value = 2
        
        self.engine.update_scaling_policy()
        
        self.ui.add_achievement.assert_not_called()

if __name__ == '__main__':
    unittest.main()