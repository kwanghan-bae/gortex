import json
import os
import logging
from typing import Dict, Any, List
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexSystemTranslator")

class SystemTranslator:
    """시스템 표준 메시지 다국어 지원 엔진 (i18n)"""
    def __init__(self, default_lang: str = "ko"):
        self.current_lang = default_lang
        self.dictionaries: Dict[str, Dict[str, str]] = {}
        self._load_all_dicts()

    def _load_all_dicts(self):
        # 파일의 위치를 기준으로 상대 경로 설정
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        i18n_dir = os.path.join(base_dir, "docs/i18n")
        if not os.path.exists(i18n_dir): 
            # Fallback for different execution contexts
            i18n_dir = "gortex/docs/i18n"
            if not os.path.exists(i18n_dir):
                return
        
        for file in os.listdir(i18n_dir):
            if file.endswith(".json"):
                lang = file.split(".")[0]
                try:
                    with open(os.path.join(i18n_dir, file), 'r', encoding='utf-8') as f:
                        self.dictionaries[lang] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load dictionary {file}: {e}")

    def t(self, key: str, lang: str = None, **kwargs) -> str:
        """키값에 해당하는 메시지 반환 및 변수 치환"""
        target_lang = lang or self.current_lang
        dictionary = self.dictionaries.get(target_lang, self.dictionaries.get("ko", {}))
        
        template = dictionary.get(key, key) 
        try:
            return template.format(**kwargs)
        except Exception:
            return template

# 전역 싱글톤 인스턴스
i18n = SystemTranslator()

class SynapticTranslator:
    """
    다국어 입력을 처리하고 자연스러운 응답 언어를 선택하는 지능형 번역 엔진.
    """
    def __init__(self):
        self.auth = GortexAuth()

    def detect_and_translate(self, text: str, target_lang: str = "Korean") -> Dict[str, str]:
        """언어를 감지하고 목표 언어로 번역"""
        # [OPTIMIZATION] 한글이 포함되어 있으면 한국어로 간주하고 번역 스킵
        import re
        if re.search("[ㄱ-ㅎㅏ-ㅣ가-힣]", text):
            return {
                "detected_lang": "ko",
                "is_korean": True,
                "translated_text": text,
                "confidence": 1.0
            }

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

    def translate_knowledge_shard(self, rule: Dict[str, Any], target_langs: List[str] = ["en", "ja", "zh"]) -> Dict[str, str]:
        """하나의 지식(Rule)을 여러 언어로 일괄 번역함"""
        translations = {"ko": rule["learned_instruction"]}
        
        prompt = f"""You are the Galactic Knowledge Translator. 
        Translate the following Gortex Super Rule into these languages: {target_langs}.
        Maintain technical integrity and don't translate placeholders or technical IDs.
        
        [Rule]: {rule['learned_instruction']}
        
        Return JSON ONLY:
        {{ "en": "...", "ja": "...", "zh": "..." }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response.text)
            translations.update(res_data)
            return translations
        except Exception as e:
            logger.error(f"Knowledge translation failed: {e}")
            return translations

    def translate_batch(self, texts: Dict[str, str], target_lang_code: str) -> Dict[str, str]:
        """여러 텍스트 항목을 한 번에 번역"""
        if target_lang_code == "ko" or not texts:
            return texts
            
        prompt = f"""다음 JSON 데이터 내의 텍스트들을 언어 코드 '{target_lang_code}'로 번역하라.
        JSON 키는 유지하고 값만 번역된 내용으로 교체하라. 기술 용어는 보존하라.
        
        [Data]
        {json.dumps(texts, ensure_ascii=False)}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            return texts
