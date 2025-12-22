import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst.reflection import ReflectionAnalyst

class TestSelfHealingDocs(unittest.TestCase):
    def setUp(self):
        self.agent = ReflectionAnalyst()
        self.agent.backend = MagicMock()
        
        # 임시 코드 파일 및 문서 생성
        self.code_path = "dummy_state.py"
        self.doc_path = "dummy_spec.md"
        
        with open(self.code_path, "w", encoding="utf-8") as f:
            f.write("class DummyState(TypedDict):\n    field1: int\n    field2: str\n    new_field: bool")
            
        with open(self.doc_path, "w", encoding="utf-8") as f:
            f.write("# Spec\n\n```python\nclass DummyState(TypedDict):\n    field1: int\n    field2: str\n```")

    def tearDown(self):
        if os.path.exists(self.code_path): os.remove(self.code_path)
        if os.path.exists(self.doc_path): os.remove(self.doc_path)

    def test_drift_detection_and_healing(self):
        # LLM 응답 시뮬레이션: 드리프트 감지됨
        self.agent.backend.generate.return_value = json.dumps({
            "drift_detected": True,
            "reason": "Missing new_field",
            "suggested_doc": "class DummyState(TypedDict):\n    field1: int\n    field2: str\n    new_field: bool"
        })
        
        result = self.agent.check_documentation_drift(self.code_path, self.doc_path, "DummyState")
        
        self.assertEqual(result["status"], "healed")
        
        # 문서가 실제로 업데이트되었는지 확인
        with open(self.doc_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("new_field: bool", content)

if __name__ == '__main__':
    unittest.main()