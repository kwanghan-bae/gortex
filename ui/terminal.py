import json
import logging
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from gortex.ui.dashboard import DashboardUI

logger = logging.getLogger("GortexTerminal")

class TerminalHandler:
    """터미널 UI 렌더링 및 사용자 입력 인터랙션 관리"""
    def __init__(self, ui: DashboardUI):
        self.ui = ui
        self.console = Console()

    def update_status(self, agent: str, step: str, **kwargs):
        """사이드바 상태 업데이트 래퍼"""
        self.ui.update_sidebar(agent, step, **kwargs)

    def display_message(self, role: str, content: Any):
        """채팅 이력에 메시지 추가 및 메인 화면 갱신"""
        self.ui.chat_history.append((role, content))
        self.ui.update_main(self.ui.chat_history)

    async def get_input(self) -> str:
        """터미널 및 웹 큐로부터 입력을 대기 (main.py의 로직 이관)"""
        # 실제 구현은 main.py의 루프와 결합 필요
        pass
