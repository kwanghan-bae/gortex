import os
import logging
from typing import Literal
from gortex.core.llm.base import LLMBackend
from gortex.core.llm.gemini_client import GeminiBackend
from gortex.core.llm.ollama_client import OllamaBackend

logger = logging.getLogger("GortexLLMFactory")

class HybridBackend(LLMBackend):
    """
    클라우드(Gemini)와 로컬(Ollama) 모델을 결합한 하이브리드 백엔드.
    Gemini 실패 시 Ollama로 자동 폴백합니다.
    """
    def __init__(self):
        self.gemini = GeminiBackend()
        self.ollama = OllamaBackend()

    def generate(self, model: str, messages: List[dict], config: Optional[Dict[str, Any]] = None) -> str:
        try:
            # 1. 우선 Gemini 시도
            return self.gemini.generate(model, messages, config)
        except Exception as e:
            # 429(Quota), 500 등 장애 발생 시 Ollama로 전환
            logger.warning(f"Gemini failed, falling back to Ollama: {e}")
            if self.ollama.is_available():
                # 로컬 모델명 매핑 (기본값: llama3)
                local_model = os.getenv("OLLAMA_MODEL", "llama3")
                return self.ollama.generate(local_model, messages, config)
            else:
                logger.error("Ollama is also unavailable.")
                raise e

    def is_available(self) -> bool:
        return self.gemini.is_available() or self.ollama.is_available()

    def supports_structured_output(self) -> bool:
        return self.gemini.supports_structured_output()

    def supports_function_calling(self) -> bool:
        return self.gemini.supports_function_calling()

class LLMFactory:
    _instances = {}

    @staticmethod
    def get_backend(backend_type: Literal["gemini", "ollama", "hybrid"] = "hybrid") -> LLMBackend:
        """
        요청된 타입에 맞는 싱글톤 백엔드 인스턴스를 반환한다.
        """
        if backend_type not in LLMFactory._instances:
            logger.info(f"Initializing LLM Backend: {backend_type}")
            if backend_type == "gemini":
                LLMFactory._instances[backend_type] = GeminiBackend()
            elif backend_type == "ollama":
                LLMFactory._instances[backend_type] = OllamaBackend()
            elif backend_type == "hybrid":
                LLMFactory._instances[backend_type] = HybridBackend()
            else:
                raise ValueError(f"Unknown backend type: {backend_type}")
        
        return LLMFactory._instances[backend_type]

    @staticmethod
    def get_default_backend() -> LLMBackend:
        """
        환경 변수 LLM_BACKEND에 따라 기본 백엔드를 반환한다. (기본값: hybrid)
        """
        backend_name = os.getenv("LLM_BACKEND", "hybrid").lower()
        if backend_name not in ["gemini", "ollama", "hybrid"]:
            logger.warning(f"Unsupported LLM_BACKEND '{backend_name}', falling back to Hybrid.")
            backend_name = "hybrid"
        
        return LLMFactory.get_backend(backend_name)  # type: ignore
