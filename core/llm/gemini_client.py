import logging
import re
import os
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
            
            from google.genai import types
            
            formatted_contents = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Gemini role mapping
                if role == "system":
                    role = "user" 
                    content = f"[System Instruction]\n{content}"
                elif role == "assistant":
                    role = "model"
                
                # [MULTIMODAL] Detect image paths
                parts = []
                # content가 리스트 형태인 경우와 문자열 형태인 경우 모두 대응
                text_content = content if isinstance(content, str) else str(content)
                
                # 이미지 경로 패턴 찾기 (e.g., image:logs/screen.png)
                image_matches = re.findall(r'image:([^\s,]+\.(?:png|jpg|jpeg|webp))', text_content)
                
                if image_matches:
                    # 텍스트에서 이미지 태그 제거
                    remaining_text = re.sub(r'image:[^\s,]+\.(?:png|jpg|jpeg|webp)', '', text_content).strip()
                    if remaining_text:
                        parts.append(types.Part.from_text(text=remaining_text))
                    
                    for img_path in image_matches:
                        if os.path.exists(img_path):
                            with open(img_path, "rb") as f:
                                img_data = f.read()
                            ext = img_path.split('.')[-1].lower()
                            mime = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
                            parts.append(types.Part.from_bytes(data=img_data, mime_type=mime))
                            logger.info(f"📸 Attached image to Gemini prompt: {img_path}")
                else:
                    parts.append(types.Part.from_text(text=text_content))
                
                # google-genai 라이브러리의 Content 객체 생성
                formatted_contents.append(types.Content(role=role, parts=parts))
                
            # auth.py의 generate가 types.Content 리스트를 처리할 수 있도록 전달
            response = self.auth.generate(model, formatted_contents, gen_config)
            return response.text if response else ""
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise e

    def is_available(self) -> bool:
        # GortexAuth가 초기화되었고 키가 있다면 사용 가능으로 간주
        # 실제 API 호출 테스트는 비용 문제로 생략
        return bool(self.auth.api_keys)

    def supports_structured_output(self) -> bool:
        return True
        
    def supports_function_calling(self) -> bool:
        return True
