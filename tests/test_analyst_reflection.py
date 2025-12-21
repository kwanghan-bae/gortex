import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import AnalystAgent

class TestAnalystReflection(unittest.TestCase):
    def setUp(self):
        # AnalystAgent.__init__ 에서 LLMFactory를 호출하므로 패치 필요
        with patch('gortex.agents.analyst.base.LLMFactory') as mock_factory:
            self.mock_backend = MagicMock()
            mock_factory.get_default_backend.return_value = self.mock_backend
            self.agent = AnalystAgent()

    def test_generate_anti_failure_rule_success(self):
        """실패 로그로부터 성공적으로 방어 규칙을 생성하는지 테스트"""
        # Mock 응답 설정
        self.mock_backend.generate.return_value = json.dumps({
            "instruction": "Never use rm -rf in production code.",
            "trigger_patterns": ["rm", "delete"],
            "severity": 5,
            "reason": "Dangerous command detected in logs."
        })

        error_log = "Error: Permission denied when running 'rm -rf /'"
        context = "Attempting to cleanup workspace."
        
        result = self.agent.generate_anti_failure_rule(error_log, context)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["instruction"], "Never use rm -rf in production code.")
        self.assertIn("rm", result["trigger_patterns"])

    def test_generate_anti_failure_rule_parsing_error(self):
        """LLM 응답이 잘못된 형식일 때 에러 처리가 정상적인지 테스트"""
        self.mock_backend.generate.return_value = "This is not a JSON"

        result = self.agent.generate_anti_failure_rule("dummy error", "dummy context")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()