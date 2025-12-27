from typing import Any, Callable, Dict, Protocol

class ToolRefusedError(Exception):
    """Raised when a tool execution is refused by the user."""
    pass

class ToolProtocol(Protocol):
    name: str
    def run(self, args: Dict[str, Any]) -> Any:
        ...

UNSAFE_TOOLS = {"write_file", "replace", "run_shell_command", "delete_file"}

def execute_tool_safely(
    tool: ToolProtocol, 
    args: Dict[str, Any], 
    confirmation_callback: Callable[[str, Dict[str, Any]], bool]
) -> Any:
    """
    Executes a tool with a safety check for side-effects.
    
    Args:
        tool: The tool object (must have .name and .run method)
        args: Arguments for the tool
        confirmation_callback: Function that returns True if user approves
        
    Returns:
        The result of tool.run(args)
        
    Raises:
        ToolRefusedError: If user denies execution
    """
    if tool.name in UNSAFE_TOOLS:
        approved = confirmation_callback(tool.name, args)
        if not approved:
            raise ToolRefusedError(f"User refused execution of tool: {tool.name}")
            
    return tool.run(args)
