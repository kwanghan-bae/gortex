import unittest
from rich.console import Console
from gortex.ui.dashboard import DashboardUI
import io

class TestUIAlignment(unittest.TestCase):
    """
    TUI 박스 선 어긋남을 수학적으로 검증하는 테스트.
    """
    def setUp(self):
        # 가상 터미널 환경 (너비 120 고정)
        self.console = Console(width=120, height=40, file=io.StringIO(), force_terminal=True)
        self.ui = DashboardUI(self.console)

    def test_vertical_border_alignment(self):
        """모든 패널의 우측 테두리(|) 위치가 일치하는지 검사"""
        # 데이터 주입
        self.ui.update_sidebar(agent="Manager", step="Thinking", tokens=1234, cost=0.5)
        self.ui.update_main([("user", "안녕"), ("ai", "반가워요 [bold]Gortex[/]입니다.")])
        
        # 렌더링
        with self.console.capture() as capture:
            self.console.print(self.ui.layout)
        
        output = capture.get()
        lines = output.splitlines()
        
        # 각 라인에서 마지막 '|' 또는 '┃' 등의 위치 확인
        # (Rich의 Box 스타일에 따라 문자열이 다를 수 있음)
        last_border_indices = []
        for line in lines:
            if "|" in line or "│" in line or "┃" in line:
                # 가장 오른쪽에 있는 테두리 문자 인덱스 기록
                idx = max(line.rfind("|"), line.rfind("│"), line.rfind("┃"))
                if idx > 10: # 유효한 테두리 라인만
                    last_border_indices.append(idx)
        
        # 모든 인덱스가 동일해야 함 (표준 편차가 0이어야 함)
        if last_border_indices:
            first_idx = last_border_indices[0]
            for i, idx in enumerate(last_border_indices):
                self.assertEqual(idx, first_idx, f"Line {i} border is misaligned! Index {idx} != {first_idx}")

if __name__ == "__main__":
    unittest.main()
