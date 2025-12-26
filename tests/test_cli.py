import unittest
from typer.testing import CliRunner
from cli import app
from unittest.mock import patch

runner = CliRunner()

class TestCLI(unittest.TestCase):
    def test_config_command(self):
        result = runner.invoke(app, ["config"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("GEMINI_API_KEY_1", result.stdout)

    @patch('cli.Prompt.ask')
    def test_init_command(self, mock_ask):
        mock_ask.side_effect = ["key1", "key2"]
        with runner.isolated_filesystem():
            result = runner.invoke(app, ["init"])
            self.assertEqual(result.exit_code, 0)
            with open(".env", "r") as f:
                content = f.read()
                self.assertIn("GEMINI_API_KEY_1=key1", content)

if __name__ == '__main__':
    unittest.main()
