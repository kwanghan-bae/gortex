import unittest
import asyncio
from gortex.main import energy_recovery_loop

class TestEnergyRecovery(unittest.IsolatedAsyncioTestCase):
    async def test_energy_recovery_loop(self):
        """에너지 회복 루프가 정상적으로 에너지를 올리는지 테스트"""
        state_vars = {"agent_energy": 50, "total_tokens": 0, "total_cost": 0.0, "last_efficiency": 100.0}
        ui = MagicMock()
        ui.current_agent = "Idle"
        
        # 2초마다 1씩 회복하므로, 비동기 작업을 잠깐 실행
        # 루프가 무한히 돌지 않도록 timeout 처리
        try:
            # 2.1초만 실행 (첫 번째 sleep 2초 이후 1회 증가 기대)
            await asyncio.wait_for(energy_recovery_loop(state_vars, ui), timeout=2.1)
        except asyncio.TimeoutError:
            pass
            
        self.assertGreater(state_vars["agent_energy"], 50)
        self.assertEqual(state_vars["agent_energy"], 51)

from unittest.mock import MagicMock

if __name__ == '__main__':
    unittest.main()
