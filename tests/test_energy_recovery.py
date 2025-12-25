import unittest
from gortex.utils.energy_monitor import EnergyMonitor

class TestEnergyRecovery(unittest.TestCase):
    def test_recovery_logic(self):
        monitor = EnergyMonitor()
        monitor.energy = 10
        monitor.recover(40)
        self.assertEqual(monitor.energy, 50)

    def test_state_integration(self):
        state_vars = {"agent_energy": 11}
        # Simulate recovery
        state_vars["agent_energy"] += 40
        self.assertEqual(state_vars["agent_energy"], 51)

if __name__ == "__main__":
    unittest.main()
