import logging
from typing import Dict, Any, Optional
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexTranslator")

class SynapticTranslator:
    """
    다국어 입력을 처리하고 자연스러운 응답 언어를 선택하는 지능형 번역 엔진.
    """
    def __init__(self):
        self.auth = GortexAuth()

    def detect_and_translate(self, text: str, target_lang: str = "Korean") -> Dict[str, str]:
        """언어를 감지하고 목표 언어로 번역"""
        prompt = f"""다음 텍스트의 언어를 감지하고, '{target_lang}'으로 번역하라.
        
        [Text]
        {text}
        
        결과는 반드시 다음 JSON 형식을 따라라:
        {{
            "detected_lang": "ISO 639-1 code (e.g. ko, en, ja)",
            "is_korean": true/false,
            "translated_text": "번역된 내용",
            "confidence": 0.0~1.0
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            import json
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {"detected_lang": "unknown", "is_korean": True, "translated_text": text, "confidence": 0.0}

    def translate_response(self, text: str, target_lang_code: str) -> str:
        """응답을 사용자의 언어로 번역"""
        if target_lang_code == "ko":
            return text
            
        prompt = f"""다음 한국어 텍스트를 언어 코드 '{target_lang_code}'에 해당하는 언어로 자연스럽게 번역하라.
        기술적인 용어는 보존하라.
        
        [Text]
        {text}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], None)
            return response.text
        except Exception as e:
            logger.error(f"Response translation failed: {e}")
            return text
