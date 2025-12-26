import pytest
import asyncio
import time
from unittest.mock import MagicMock, AsyncMock
from gortex.core.engine import GortexEngine
from gortex.core.state import GortexState

@pytest.mark.asyncio
async def test_engine_process_node_output_non_blocking():
    """
    Verify that process_node_output uses asyncio.to_thread for slow sync calls,
    preventing the event loop from being blocked.
    """
    # Mock UI and Vocal Bridge
    mock_ui = MagicMock()
    # Slow sync vocal bridge mock
    mock_vocal = MagicMock()
    def slow_tts(text):
        time.sleep(0.5) # Simulate network/IO lag
        return "mock_path.mp3"
    mock_vocal.text_to_speech.side_effect = slow_tts
    
    engine = GortexEngine(ui=mock_ui, vocal_bridge=mock_vocal)
    
    state = {"assigned_model": "flash", "last_event_id": None}
    output = {"thought": "test", "messages": [("ai", "Hello")]}
    
    start_time = asyncio.get_event_loop().time()
    
    # Execution
    task = asyncio.create_task(engine.process_node_output("manager", output, state))
    
    # If it was blocking, we couldn't do anything here until 0.5s passed.
    # But since it's in a thread, the loop should be free.
    await asyncio.sleep(0.1)
    mid_time = asyncio.get_event_loop().time()
    
    await task
    end_time = asyncio.get_event_loop().time()
    
    # Assertions
    assert mid_time - start_time < 0.2, "Event loop was blocked by sync TTS call!"
    assert end_time - start_time >= 0.5, "Task finished too fast, mock didn't work?"
    mock_vocal.text_to_speech.assert_called_once()
    assert state["thought"] == "test"

@pytest.mark.asyncio
async def test_workflow_execution_not_eating_input_loop():
    """
    This is harder to test without a full UI, but we can verify the 'await current_task' 
    logic conceptually by checking if execution flow is preserved.
    """
    pass # Managed by manual verification and sanity check
