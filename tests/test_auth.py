import unittest
from unittest.mock import patch, MagicMock
from gortex.core.auth import GortexAuth

class TestGortexAuth(unittest.TestCase):
    def setUp(self):
        # Reset singleton instance
        GortexAuth._instance = None
        
    @patch("gortex.core.auth.genai.Client")
    def test_init(self, mock_client):
        auth = GortexAuth()
        self.assertTrue(hasattr(auth, "key_pool"))
        self.assertTrue(hasattr(auth, "openai_client"))

    @patch("gortex.core.auth.genai.Client")
    def test_get_current_client(self, mock_client):
        # Mock env vars or rely on mock client injection if feasible
        # Since we can't easily set env vars here without affecting other tests,
        # we'll mock the internal key_pool
        auth = GortexAuth()
        mock_key_info = MagicMock()
        mock_key_info.status = "alive"
        mock_key_info.client = "gemini_client"
        auth.key_pool = [mock_key_info]
        
        client = auth.get_current_client()
        self.assertEqual(client, "gemini_client")

    def test_get_pool_status(self):
        auth = GortexAuth()
        status = auth.get_pool_status()
        self.assertIsInstance(status, list)

if __name__ == "__main__":
    unittest.main()
