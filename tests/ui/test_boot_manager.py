import unittest
import asyncio
from rich.console import Console
from gortex.ui.components.boot import BootManager

class TestBootManager(unittest.TestCase):
    def setUp(self):
        self.console = Console(quiet=True)
        self.boot = BootManager(self.console)

    def test_boot_sequence_calls(self):
        """부팅 시퀀스가 예외 없이 실행되는지 확인"""
        try:
            asyncio.run(self.boot.run_sequence())
        except Exception as e:
            self.fail(f"Boot sequence failed with error: {e}")

if __name__ == "__main__":
    unittest.main()
