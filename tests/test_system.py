import unittest
from unittest.mock import patch
from gortex.core.system import GortexSystem
# GortexState is now a TypedDict, so we can't assertIsInstance(obj, GortexState) easily if it's just a dict at runtime.
# We will check keys.

class TestGortexSystem(unittest.TestCase):
    @patch('gortex.core.system.Console')
    @patch('gortex.core.system.DashboardUI')
    @patch('gortex.core.system.GortexObserver')
    @patch('gortex.core.system.VocalBridge')
    @patch('gortex.core.system.GortexEngine')
    @patch('gortex.core.system.SessionManager')
    def test_initialization(self, mock_sm, mock_engine, mock_vocal, mock_obs, mock_ui, mock_console):
        """Test that the system initializes correctly."""
        mock_sm.return_value.get_session.return_value = {}

        system = GortexSystem()

        self.assertIsInstance(system.state, dict)
        self.assertIn("agent_energy", system.state)
        self.assertTrue(mock_ui.called)
        self.assertTrue(mock_engine.called)

    @patch('gortex.core.system.Console')
    @patch('gortex.core.system.DashboardUI')
    @patch('gortex.core.system.GortexObserver')
    @patch('gortex.core.system.VocalBridge')
    @patch('gortex.core.system.GortexEngine')
    @patch('gortex.core.system.SessionManager')
    def test_initial_energy(self, mock_sm, mock_engine, mock_vocal, mock_obs, mock_ui, mock_console):
        """Test the initial energy state."""
        mock_sm.return_value.get_session.return_value = {}
        system = GortexSystem()
        # Default energy should be 100
        self.assertEqual(system.state["agent_energy"], 100)

if __name__ == '__main__':
    unittest.main()
