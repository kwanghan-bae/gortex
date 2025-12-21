import unittest
import json
from unittest.mock import MagicMock, patch
from gortex.agents.analyst import AnalystAgent

class TestAnalystReflection(unittest.TestCase):
    def setUp(self):
        self.agent = AnalystAgent()

    @patch('gortex.core.auth.GortexAuth.generate')
    def test_generate_anti_failure_rule_success(self, mock_generate):
        """실패 로그로부터 성공적으로 방어 규칙을 생성하는지 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "instruction": "Never use rm -rf in production code.",
            "trigger_patterns": ["rm", "delete"],
            "severity": 5,
            "reason": "Dangerous command detected in logs."
        })
        mock_generate.return_value = mock_response

        error_log = "Error: Permission denied when running 'rm -rf /'"
        context = "Attempting to cleanup workspace."
        
        result = self.agent.generate_anti_failure_rule(error_log, context)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["instruction"], "Never use rm -rf in production code.")
        self.assertIn("rm", result["trigger_patterns"])

    @patch('gortex.core.auth.GortexAuth.generate')
    def test_generate_anti_failure_rule_parsing_error(self, mock_generate):
        """LLM 응답이 잘못된 형식일 때 에러 처리가 정상적인지 테스트"""
        mock_response = MagicMock()
        mock_response.text = "This is not a JSON"
        mock_generate.return_value = mock_response

        result = self.agent.generate_anti_failure_rule("dummy error", "dummy context")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
