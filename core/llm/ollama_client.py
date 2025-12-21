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

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
            
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
