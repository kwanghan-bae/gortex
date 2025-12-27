import pytest
from unittest.mock import MagicMock
from gortex.core.cli.safety import execute_tool_safely, ToolRefusedError

def test_execute_tool_safely_approved():
    # Arrange
    mock_tool = MagicMock()
    mock_tool.name = "write_file"
    mock_tool.run.return_value = "File written"
    
    mock_confirmation = MagicMock(return_value=True)
    
    args = {"file_path": "test.txt", "content": "hello"}
    
    # Act
    result = execute_tool_safely(mock_tool, args, confirmation_callback=mock_confirmation)
    
    # Assert
    assert result == "File written"
    mock_tool.run.assert_called_once_with(args)
    mock_confirmation.assert_called_once()

def test_execute_tool_safely_rejected():
    # Arrange
    mock_tool = MagicMock()
    mock_tool.name = "run_shell_command"
    
    mock_confirmation = MagicMock(return_value=False)
    
    args = {"command": "rm -rf /"}
    
    # Act & Assert
    with pytest.raises(ToolRefusedError):
        execute_tool_safely(mock_tool, args, confirmation_callback=mock_confirmation)
    
    mock_tool.run.assert_not_called()
