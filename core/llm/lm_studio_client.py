import requests
import logging
import os
import json
from typing import List, Dict, Any, Optional
from gortex.core.llm.base import LLMBackend

logger = logging.getLogger("GortexLMStudioClient")

class LMStudioBackend(LLMBackend):
    """
    LM Studio 서버와 통신하는 백엔드 구현체.
    OpenAI API 호환 인터페이스를 사용합니다.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.timeout = 120  # 2분 타임아웃

    def generate(self, model: str, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/chat/completions"

        # [Optimization] JSON 출력이 필요한 경우
        is_json_requested = False
        if config and config.get("response_mime_type") == "application/json":
            is_json_requested = True
            # 시스템 메시지 보강
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\nIMPORTANT: Return ONLY valid JSON. No conversational text."

        # config 처리
        temperature = 0.7
        max_tokens = -1
        top_p = 1.0

        if config:
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", -1)
            top_p = config.get("top_p", 1.0)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }

        if max_tokens > 0:
            payload["max_tokens"] = max_tokens

        if is_json_requested:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [])[0].get("message", {}).get("content", "")

            # [Healing] JSON 요청 시 파싱 검증 및 복구
            if is_json_requested:
                from gortex.utils.tools import repair_and_load_json
                repaired = repair_and_load_json(content)
                if repaired:
                    return json.dumps(repaired, ensure_ascii=False)

            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"LM Studio generation failed: {e}")
            raise e

    def is_available(self) -> bool:
        """LM Studio 서버 헬스 체크"""
        try:
            # /v1/models 엔드포인트를 찔러서 생존 확인
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def supports_structured_output(self) -> bool:
        # LM Studio 최신 버전은 JSON 모드 지원
        return True

    def supports_function_calling(self) -> bool:
        # 모델에 따라 다르지만 기본적으로는 False로 가정
        return False
