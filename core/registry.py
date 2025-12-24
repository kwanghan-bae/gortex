import logging
import importlib.util
import inspect
import os
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

    def load_agent_from_file(self, file_path: str) -> bool:
        """소스 파일로부터 에이전트 클래스를 동적으로 로드하고 등록함"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False

        try:
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # BaseAgent를 상속받은 클래스 탐색
            from gortex.agents.base import BaseAgent
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    # 인스턴스 생성하여 메타데이터 확인
                    instance = obj()
                    self.register(instance.metadata.name, obj, instance.metadata)
                    return True
            
            logger.warning(f"No valid BaseAgent subclass found in {file_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load agent from {file_path}: {e}")
            return False

    def is_tool_permitted(self, agent_name: str, tool_name: str, agent_economy: Dict[str, Any]) -> bool:
        """에이전트의 숙련도에 따라 특정 도구의 사용 가능 여부를 판별함."""
        # 1. 고급 도구별 필요 스킬 포인트 정의
        advanced_tools = {
            "apply_patch": {"cat": "Coding", "pts": 500},
            "audit_architecture": {"cat": "Analysis", "pts": 1000},
            "spawn_new_agent": {"cat": "Analysis", "pts": 2000},
            "execute_shell": {"cat": "General", "pts": 300}
        }
        
        if tool_name not in advanced_tools:
            return True # 일반 도구는 무조건 허용
            
        # 2. 에이전트의 현재 스킬 점수 확인
        required = advanced_tools[tool_name]
        agent_skills = agent_economy.get(agent_name.lower(), {}).get("skill_points", {})
        current_pts = agent_skills.get(required["cat"], 0)
        
        if current_pts >= required["pts"]:
            return True
            
        logger.warning(f"🚫 Tool '{tool_name}' is locked for {agent_name}. Requires {required['pts']} pts in {required['cat']}.")
        return False

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
