
import unittest
import os
import shutil
import tempfile
from gortex.core.task import TaskManager, Task, TaskStatus

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

    def test_create_root_task(self):
        """루트 태스크 생성 테스트"""
        task_id = self.manager.create_task(name="Project Alpha", description="Main Goal")
        task = self.manager.get_task(task_id)
        
        self.assertIsNotNone(task)
        self.assertEqual(task.name, "Project Alpha")
        self.assertEqual(task.status, TaskStatus.PLANNED)

    def test_subtask_management(self):
        """서브태스크 추가 및 계층 구조 테스트"""
        root_id = self.manager.create_task("Root")
        sub_id = self.manager.create_task("Sub", parent_id=root_id)
        
        root = self.manager.get_task(root_id)
        sub = self.manager.get_task(sub_id)
        
        self.assertEqual(sub.parent_id, root_id)
        self.assertIn(sub_id, root.children_ids)

    def test_status_transition(self):
        """태스크 상태 변경 테스트"""
        tid = self.manager.create_task("Job")
        self.manager.update_status(tid, TaskStatus.IN_PROGRESS)
        
        task = self.manager.get_task(tid)
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)

    def test_context_storage(self):
        """태스크별 컨텍스트(메모장) 저장 테스트"""
        tid = self.manager.create_task("Memory Job")
        self.manager.update_context(tid, {"key": "value", "progress": 50})
        
        task = self.manager.get_task(tid)
        self.assertEqual(task.context["key"], "value")
        self.assertEqual(task.context["progress"], 50)

if __name__ == '__main__':
    unittest.main()
