from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMBackend(ABC):
    """
    모든 LLM(Large Language Model) 백엔드가 구현해야 할 추상 인터페이스.
    Gortex 시스템은 이 인터페이스를 통해 모델과 통신하며, 구체적인 구현(Gemini, Ollama 등)에 의존하지 않는다.
    """

    @abstractmethod
    def generate(self, model: str, messages: List[Dict[str, str]], config: Optional[Dict[str, Any]] = None) -> str:
        """
        주어진 메시지 컨텍스트를 바탕으로 응답 텍스트를 생성한다.
        
        Args:
            model (str): 사용할 모델 식별자 (예: 'gemini-1.5-flash', 'qwen2.5-coder:7b')
            messages (List[Dict[str, str]]): 대화 내역 [{'role': 'user', 'content': '...'}, ...]
            config (Optional[Dict[str, Any]]): 생성 설정 (temperature, max_tokens 등)
            
        Returns:
            str: 생성된 텍스트 응답
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        현재 백엔드가 사용 가능한 상태인지 확인한다.
        (예: API 키 유효성, 로컬 서버 연결 상태 등)
        """
        pass
        
    def supports_structured_output(self) -> bool:
        """JSON Schema 강제 등 구조화된 출력 지원 여부"""
        return False
        
    def supports_function_calling(self) -> bool:
        """Native Function Calling 지원 여부"""
        return False