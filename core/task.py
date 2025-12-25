
import uuid
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

logger = logging.getLogger("GortexTaskManager")

class TaskStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class Task:
    id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PLANNED
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "context": self.context
        }

class TaskManager:
    """계층적 태스크 관리자 (In-Memory)"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, name: str, description: str = "", parent_id: Optional[str] = None) -> str:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, name=name, description=description, parent_id=parent_id)
        
        self.tasks[task_id] = task
        
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].children_ids.append(task_id)
            
        logger.info(f"📋 Task Created: {name} ({task_id}) [Parent: {parent_id}]")
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_status(self, task_id: str, status: TaskStatus):
        if task_id in self.tasks:
            old_status = self.tasks[task_id].status
            self.tasks[task_id].status = status
            logger.info(f"🔄 Task {self.tasks[task_id].name} Status: {old_status} -> {status}")

    def update_context(self, task_id: str, updates: Dict[str, Any]):
        if task_id in self.tasks:
            self.tasks[task_id].context.update(updates)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
