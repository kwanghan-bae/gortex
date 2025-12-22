import requests
import logging
import os
from typing import List, Dict, Any, Optional
from gortex.core.llm.base import LLMBackend

logger = logging.getLogger("GortexOllamaClient")

class OllamaBackend(LLMBackend):
    """
    로컬 Ollama 서버와 통신하는 백엔드 구현체.
    """
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = 120  # 2분 타임아웃

    def generate(self, model: str, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None) -> str:
        url = f"{self.base_url}/api/chat"
        
        # [Optimization] 로컬 모델을 위한 시스템 프롬프트 보강
        # JSON 출력이 필요한 경우를 감지하여 지침 강화
        is_json_requested = False
        if config and config.get("response_mime_type") == "application/json":
            is_json_requested = True
            # 시스템 메시지 끝에 강제 지침 삽입
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\nIMPORTANT: Return ONLY valid JSON. No conversational text."

        # config 처리
        options = {}
        if config:
            if "temperature" in config: options["temperature"] = config["temperature"]
            if "max_tokens" in config: options["num_predict"] = config["max_tokens"]
            if "top_p" in config: options["top_p"] = config["top_p"]
            
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options
        }
        
        # Ollama 자체 JSON 모드 지원 활용
        if is_json_requested:
            payload["format"] = "json"

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            
            # [Healing] JSON 요청 시 파싱 검증 및 복구
            if is_json_requested:
                from gortex.utils.tools import repair_and_load_json
                repaired = repair_and_load_json(content)
                if repaired:
                    return json.dumps(repaired, ensure_ascii=False)
            
            return content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            raise e

    def is_available(self) -> bool:
        """Ollama 서버 헬스 체크"""
        try:
            # /api/tags 엔드포인트 등을 찔러서 생존 확인
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def supports_structured_output(self) -> bool:
        # 최신 Ollama는 format='json' 지원하지만, Schema 강제는 모델 의존적임
        # 안전하게 False로 두고 프롬프트 엔지니어링으로 해결 유도
        return False
        
    def supports_function_calling(self) -> bool:
        # Ollama도 도구 지원이 추가되었으나, Gortex 표준과 맞추기 위해 아직은 False
        return False
