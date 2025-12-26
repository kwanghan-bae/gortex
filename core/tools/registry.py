import logging
import importlib.util
import inspect
import os
from typing import Dict, Callable, List, Optional

logger = logging.getLogger("GortexToolRegistry")

class ToolRegistry:
    """
    Gortex 에이전트들이 사용하는 도구(함수)들을 관리하는 중앙 레지스트리.
    런타임에 새로운 도구를 동적으로 로드하고 배포할 수 있습니다.
    """
    _instance = None
    _tools: Dict[str, Callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
        return cls._instance

    def register_tool(self, name: str, func: Callable):
        """도구를 레지스트리에 등록함"""
        self._tools[name] = func
        logger.info(f"🛠️ Tool '{name}' registered to ToolRegistry.")

    def get_tool(self, name: str) -> Optional[Callable]:
        """등록된 도구 함수를 반환함"""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """현재 사용 가능한 모든 도구 목록 반환"""
        return list(self._tools.keys())

    def load_tools_from_module(self, module_path: str):
        """특정 모듈 파일에서 모든 함수를 도구로 자동 로드함"""
        if not os.path.exists(module_path):
            return
            
        try:
            module_name = os.path.basename(module_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for name, obj in inspect.getmembers(module):
                if inspect.isfunction(obj) and not name.startswith("_"):
                    self.register_tool(name, obj)
        except Exception as e:
            logger.error(f"Failed to load tools from {module_path}: {e}")

# 글로벌 싱글톤 인스턴스
tool_registry = ToolRegistry()
