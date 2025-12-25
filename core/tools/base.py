
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("GortexTools")

class BaseTool(ABC):
    """모든 Gortex 도구의 기본 클래스"""
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """도구 실행 로직을 구현해야 합니다."""
        pass
        
    def validate_args(self, **kwargs) -> bool:
        """인자 유효성 검사 (Optional)"""
        return True
