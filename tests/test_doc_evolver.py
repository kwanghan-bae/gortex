import unittest
import os
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import analyst_instance
from gortex.utils.tools import read_file, write_file

class TestDocEvolver(unittest.TestCase):
    def setUp(self):
        # 1. 테스트용 코드 파일 생성
        self.code_file = "gortex/core/state_test.py"
        os.makedirs(os.path.dirname(self.code_file), exist_ok=True)
        code_content = "class GortexState(TypedDict):\n    plan: List[str]\n    new_field: str"
        write_file(self.code_file, code_content)
        
        # 2. 테스트용 문서 파일 생성
        self.doc_file = "docs/TECHNICAL_SPEC_TEST.md"
        doc_content = "## Schema\n```python\nclass GortexState(TypedDict):\n    plan: List[str]\n```"
        write_file(self.doc_file, doc_content)

    def tearDown(self):
        if os.path.exists(self.code_file): os.remove(self.code_file)
        if os.path.exists(self.doc_file): os.remove(self.doc_file)

    @patch("gortex.core.llm.factory.LLMFactory.get_default_backend")
    def test_documentation_auto_heal(self, mock_factory):
        """Doc-Evolver가 코드 변경을 감지하고 문서를 자동 업데이트하는지 테스트"""
        mock_backend = MagicMock()
        mock_factory.return_value = mock_backend
        
        # LLM 응답 모킹
        mock_backend.generate.return_value = json.dumps({
            "drift_detected": True,
            "reason": "New field added.",
            "suggested_doc": "class GortexState(TypedDict):\n    plan: List[str]\n    new_field: str"
        })
        
        # 전역 인스턴스의 백엔드 교체
        original_backend = analyst_instance.backend
        analyst_instance.backend = mock_backend
        
        try:
            # 실행
            res = analyst_instance.check_documentation_drift(self.code_file, self.doc_file, "GortexState")
            
            # 검증
            self.assertEqual(res["status"], "healed")
            updated_doc = read_file(self.doc_file)
            self.assertIn("new_field: str", updated_doc)
            print("\n✅ Doc-Evolver success.")
        finally:
            analyst_instance.backend = original_backend

if __name__ == "__main__":
    unittest.main()