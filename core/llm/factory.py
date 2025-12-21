import os
import logging
from typing import Literal
from gortex.core.llm.base import LLMBackend
from gortex.core.llm.gemini_client import GeminiBackend
from gortex.core.llm.ollama_client import OllamaBackend

logger = logging.getLogger("GortexLLMFactory")

class LLMFactory:
    _instances = {}

    @staticmethod
    def get_backend(backend_type: Literal["gemini", "ollama"] = "gemini") -> LLMBackend:
        """
        요청된 타입에 맞는 싱글톤 백엔드 인스턴스를 반환한다.
        """
        if backend_type not in LLMFactory._instances:
            logger.info(f"Initializing LLM Backend: {backend_type}")
            if backend_type == "gemini":
                LLMFactory._instances[backend_type] = GeminiBackend()
            elif backend_type == "ollama":
                LLMFactory._instances[backend_type] = OllamaBackend()
            else:
                raise ValueError(f"Unknown backend type: {backend_type}")
        
        return LLMFactory._instances[backend_type]

    @staticmethod
    def get_default_backend() -> LLMBackend:
        """
        환경 변수 LLM_BACKEND에 따라 기본 백엔드를 반환한다. (기본값: gemini)
        """
        backend_name = os.getenv("LLM_BACKEND", "gemini").lower()
        # 지원하지 않는 이름이면 안전하게 gemini로 폴백
        if backend_name not in ["gemini", "ollama"]:
            logger.warning(f"Unsupported LLM_BACKEND '{backend_name}', falling back to Gemini.")
            backend_name = "gemini"
        
        return LLMFactory.get_backend(backend_name)  # type: ignore
