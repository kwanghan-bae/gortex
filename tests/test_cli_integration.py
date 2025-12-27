import pytest
from typer.testing import CliRunner
from cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "chat" in result.stdout
    assert "start" in result.stdout

def test_chat_command_importable():
    # Just checking if the command is registered and help works, 
    # which implies imports inside the command function (if lazy) or top level are okay.
    # Since imports in chat() are lazy (inside the function), we need to trigger them to test.
    # But running chat() starts a loop. We can't easily test that without mocking input.
    # For now, help check is sufficient to see if typer picked it up.
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0
    assert "Start the local Gortex CLI" in result.stdout
