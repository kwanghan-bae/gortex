import unittest
from unittest.mock import patch, MagicMock
from gortex.core.llm.lm_studio_client import LMStudioBackend

class TestLMStudioBackend(unittest.TestCase):
    def setUp(self):
        self.backend = LMStudioBackend(base_url="http://test-server/v1")

    @patch("requests.post")
    def test_generate(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello from LM Studio"}}]
        }
        mock_post.return_value = mock_response

        response = self.backend.generate("local-model", [{"role": "user", "content": "Hi"}])
        self.assertEqual(response, "Hello from LM Studio")

        # Verify payload
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["model"], "local-model")
        self.assertEqual(kwargs["json"]["messages"][0]["content"], "Hi")

    @patch("requests.get")
    def test_is_available(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.assertTrue(self.backend.is_available())

    @patch("requests.get")
    def test_is_not_available(self, mock_get):
        mock_get.side_effect = Exception("Connection refused")

        self.assertFalse(self.backend.is_available())

if __name__ == "__main__":
    unittest.main()
