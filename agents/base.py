import abc
from typing import Dict, Any
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.core.registry import AgentMetadata

class BaseAgent(abc.ABC):
    """
    모든 Gortex 에이전트의 공통 추상 베이스 클래스 (v3.0 표준).
    """
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()

    @property
    @abc.abstractmethod
    def metadata(self) -> AgentMetadata:
        """에이전트의 메타데이터를 정의해야 함"""
        pass

    @abc.abstractmethod
    def run(self, state: GortexState) -> Dict[str, Any]:
        """에이전트의 핵심 실행 로직"""
        pass

    def __call__(self, state: GortexState) -> Dict[str, Any]:
        """LangGraph 노드 호환성을 위한 호출 인터페이스"""
        return self.run(state)
