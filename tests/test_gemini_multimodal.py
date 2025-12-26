import unittest
from unittest.mock import patch
import os
from gortex.core.llm.gemini_client import GeminiBackend

class TestGeminiMultimodal(unittest.TestCase):
    def setUp(self):
        self.backend = GeminiBackend()
        # 테스트용 가짜 이미지 생성
        self.test_img = "test_screen.png"
        with open(self.test_img, "wb") as f:
            f.write(b"fake image data")

    def tearDown(self):
        if os.path.exists(self.test_img):
            os.remove(self.test_img)

    @patch("gortex.core.auth.GortexAuth.generate")
    def test_image_part_conversion(self, mock_auth_generate):
        """'image:path' 문자열이 Gemini의 Part 객체로 올바르게 변환되는지 테스트"""
        messages = [
            {"role": "user", "content": f"Check this out image:{self.test_img}"}
        ]
        
        self.backend.generate("gemini-2.0-flash", messages)
        
        # GortexAuth.generate에 전달된 contents 확인
        self.assertTrue(mock_auth_generate.called)
        contents = mock_auth_generate.call_args[0][1]
        
        # Content 객체 및 Part 검증
        from google.genai import types
        self.assertIsInstance(contents[0], types.Content)
        parts = contents[0].parts
        
        # 텍스트 파트와 이미지 파트가 분리되어야 함
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0].text, "Check this out")
        self.assertIsNotNone(parts[1].inline_data)
        self.assertEqual(parts[1].inline_data.mime_type, "image/png")

if __name__ == "__main__":
    unittest.main()
