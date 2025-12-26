
import asyncio
import logging
import os
import shutil
from gortex.core.task import TaskManager, TaskStatus
from gortex.core.artifacts.base import BaseArtifact
from gortex.core.artifacts.store import FileSystemArtifactStore
from gortex.core.middleware import HealingMiddleware
from gortex.core.tools import FindByNameTool, ReplaceFileContentTool

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GortexTestDrive")

async def test_drive():
    logger.info("🚗 Starting Gortex Phase 5 Test Drive...")
    
    # 1. Setup Environment
    test_workspace = "test_workspace"
    os.makedirs(test_workspace, exist_ok=True)
    brain_dir = os.path.join(test_workspace, "brain")
    
    # 2. Initialize Core Components
    task_manager = TaskManager()
    artifact_store = FileSystemArtifactStore(base_path=brain_dir)
    healer = HealingMiddleware(max_retries=1)
    
    # 3. Task Management Simulation
    logger.info("--- [1] Task Management ---")
    root_id = task_manager.create_task("Phase 5 Integration", "Verify core modules")
    sub_id = task_manager.create_task("Test Tools", parent_id=root_id)
    
    task_manager.update_status(root_id, TaskStatus.IN_PROGRESS)
    task_manager.update_context(sub_id, {"progress": 10})
    logger.info(f"Root Task Status: {task_manager.get_task(root_id).status}")
    logger.info(f"Sub Task Context: {task_manager.get_task(sub_id).context}")
    
    # 4. Artifact System Simulation
    logger.info("--- [2] Artifact System ---")
    artifact = BaseArtifact(
        id="test-plan-v1",
        type="plan",
        title="Test Drive Plan",
        content="# Plan\n1. Run Test",
        metadata={"author": "TestDriver"}
    )
    saved_path = artifact_store.save(artifact)
    logger.info(f"Artifact Saved to: {saved_path}")
    
    loaded = artifact_store.load("test-plan-v1")
    if loaded and loaded.title == artifact.title:
        logger.info("✅ Artifact Load Verified")
    else:
        logger.error("❌ Artifact Load Failed")

    # 5. Developer Tools Simulation
    logger.info("--- [3] Developer Tools ---")
    # Create dummy file
    dummy_file = os.path.join(test_workspace, "hello.py")
    with open(dummy_file, "w") as f:
        f.write("print('Hello Old World')")
        
    # Search
    finder = FindByNameTool()
    found = finder.execute("hello.py", path=test_workspace)
    logger.info(f"File Found: {found}")
    
    # Edit
    editor = ReplaceFileContentTool()
    res = editor.execute(dummy_file, "print('Hello Old World')", "print('Hello New World')")
    logger.info(f"Edit Result: {res}")
    
    with open(dummy_file, "r") as f:
        logger.info(f"File Content: {f.read().strip()}")

    # 6. Healing Loop Simulation
    logger.info("--- [4] Healing Loop ---")
    # Simulate a failed response
    failed_output = {"status": "failed", "error": "SimulatedError"}
    state = {"retry_count": 0}
    
    processed = healer.process_response(failed_output, state)
    
    if state.get("next_node") == "healer":
        logger.info("✅ Healing Triggered: Routed to Healer node")
    else:
        logger.error("❌ Healing Failed to Trigger")
        
    # Cleanup
    shutil.rmtree(test_workspace)
    logger.info("🏁 Test Drive Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(test_drive())
