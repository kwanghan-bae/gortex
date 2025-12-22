import logging
from typing import Dict, Any, List, Type, Optional

logger = logging.getLogger("GortexRegistry")

class AgentMetadata:
    """에이전트의 정체성과 능력을 기술하는 메타데이터"""
    def __init__(self, name: str, role: str, description: str, tools: List[str], version: str = "1.0.0"):
        self.name = name
        self.role = role
        self.description = description
        self.tools = tools
        self.version = version

class AgentRegistry:
    """
    Gortex 에이전트들을 중앙에서 관리하는 레지스트리.
    플러그인 아키텍처(v3.0)의 핵심 구성 요소.
    """
    _instance = None
    _agents: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, agent_name: str, agent_class: Type, metadata: AgentMetadata):
        """에이전트를 레지스트리에 등록함"""
        self._agents[agent_name.lower()] = {
            "class": agent_class,
            "metadata": metadata
        }
        logger.info(f"🆕 Agent '{agent_name}' (v{metadata.version}) registered to registry.")

    def get_agent(self, agent_name: str) -> Optional[Type]:
        """등록된 에이전트 클래스 반환"""
        return self._agents.get(agent_name.lower(), {}).get("class")

    def get_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """에이전트 메타데이터 조회"""
        return self._agents.get(agent_name.lower(), {}).get("metadata")

    def get_agents_by_role(self, role: str) -> List[str]:
        """특정 역할을 수행할 수 있는 모든 에이전트 목록 반환"""
        return [name for name, info in self._agents.items() if info["metadata"].role.lower() == role.lower()]

    def get_agents_by_tool(self, tool_name: str) -> List[str]:
        """특정 도구를 사용할 수 있는 모든 에이전트 목록 반환 (discover_capability 별칭)"""
        return self.discover_capability(tool_name)

    def list_agents(self) -> List[str]:
        """등록된 모든 에이전트 목록 반환"""
        return list(self._agents.keys())

    def discover_capability(self, tool_name: str) -> List[str]:
        """특정 도구를 사용할 수 있는 에이전트 탐색"""
        capable_agents = []
        for name, info in self._agents.items():
            if tool_name in info["metadata"].tools:
                capable_agents.append(name)
        return capable_agents

# 글로벌 싱글톤 인스턴스
registry = AgentRegistry()
