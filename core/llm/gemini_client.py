import logging
from typing import List, Dict, Any, Optional
from gortex.core.llm.base import LLMBackend
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexGeminiClient")

class GeminiBackend(LLMBackend):
    """
    GortexAuth(기존 Gemini 연동 모듈)를 감싸는 어댑터 클래스.
    """
    def __init__(self):
        self.auth = GortexAuth()

    def generate(self, model: str, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None) -> str:
        try:
            # GortexAuth.generate는 google.genai.types.GenerateContentConfig를 기대함
            # 여기서는 편의상 딕셔너리 config를 변환하거나 기본값을 사용해야 함
            # 기존 auth.py는 types 객체를 직접 받았으므로, 호환성을 위해 config가 types 객체인지 확인
            
            from google.genai import types
            
            gen_config = None
            if config:
                if isinstance(config, dict):
                    # 딕셔너리를 GenerateContentConfig로 변환 (필요한 필드만 매핑)
                    gen_config = types.GenerateContentConfig(
                        temperature=config.get("temperature", 0.7),
                        max_output_tokens=config.get("max_tokens", None),
                        top_p=config.get("top_p", None)
                    )
                else:
                    gen_config = config
            
            # 메시지 형식 변환: List[Dict] -> List[Tuple] or similar supported format
            # GortexAuth.generate는 [(role, content), ...] 튜플 리스트를 선호할 수 있음
            # 또는 리스트 그대로 전달 시도 (auth.py 구현에 따라 다름)
            # auth.py 분석 결과 generate(self, model_name, contents, config=None)
            
            # contents 포맷팅
            formatted_contents = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Gemini role mapping
                if role == "system":
                    # 시스템 메시지는 별도 처리가 필요할 수 있으나, 여기서는 user/model 흐름에 맞김
                    # 최신 Gemini API는 system_instruction을 config에 넣는 것을 권장하나
                    # auth.py가 이를 처리하는지 불확실하므로 일단 content로 포함
                    role = "user" 
                    content = f"[System Instruction]\n{content}"
                elif role == "assistant":
                    role = "model"
                
                formatted_contents.append((role, content))
                
            response = self.auth.generate(model, formatted_contents, gen_config)
            return response.text if response else ""
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise e

    def is_available(self) -> bool:
        # GortexAuth가 초기화되었고 키가 있다면 사용 가능으로 간주
        # 실제 API 호출 테스트는 비용 문제로 생략
        return bool(self.auth.api_keys)
