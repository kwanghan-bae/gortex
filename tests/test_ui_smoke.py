import unittest
from rich.console import Console
from gortex.ui.dashboard import DashboardUI

class TestUISmoke(unittest.TestCase):
    """
    UI 렌더링 무결성을 검증하는 스모크 테스트.
    존재하지 않는 스피너나 잘못된 마크업 태그가 있으면 여기서 즉시 발견됩니다.
    """
    def setUp(self):
        self.console = Console(width=120, height=40)
        self.ui = DashboardUI(self.console)

    def test_all_agent_rendering(self):
        """모든 등록된 에이전트의 사이드바 및 사고 패널 렌더링 테스트"""
        agents = ["manager", "planner", "coder", "researcher", "analyst", "trend_scout", "summarizer", "optimizer"]
        
        for agent in agents:
            with self.subTest(agent=agent):
                # 1. 사이드바 업데이트 테스트 (스피너 이름 검증)
                self.ui.update_sidebar(agent, "Active", tokens=100, cost=0.01)
                
                # 2. 사고 패널 업데이트 테스트 (마크업 태그 검증)
                self.ui.update_thought(f"Test thought for {agent}", agent_name=agent)
                self.ui.update_thought("", agent_name=agent) # 빈 상태(Thinking) 테스트
                
                # 3. 실제 렌더링 시도 (Rich 예외 발생 여부 확인)
                try:
                    list(self.console.render(self.ui.layout, self.console.options))
                except Exception as e:
                    self.fail(f"Rendering failed for agent '{agent}': {e}")

    def test_stats_and_logs_rendering(self):
        """통계 및 로그 패널의 극한 상황 렌더링 테스트"""
        self.ui.update_sidebar(tokens=9999999, cost=123.456)
        self.ui.update_logs({"agent": "system", "event": "Test [bracket] markup safety"})
        
        try:
            # layout 프로퍼티에 접근하여 전체 렌더링 트리 생성 검증
            renderable = self.ui.layout
            list(self.console.render(renderable, self.console.options))
        except Exception as e:
            self.fail(f"Stats/Logs rendering failed: {e}")

if __name__ == "__main__":
    unittest.main()
