import unittest
from rich.console import Console
from gortex.ui.dashboard import DashboardUI
import io

class TestUIIntegrity(unittest.TestCase):
    """
    다양한 화면 크기에서 UI 렌더링 및 정렬 무결성 검증.
    """
    def _check_alignment(self, console, ui):
        with console.capture() as capture:
            console.print(ui.layout)
        
        # [FIX] ANSI 이스케이프 코드 제거 (정확한 인덱스 계산을 위해)
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', capture.get())
        lines = output.splitlines()
        
        last_border_indices = []
        for line in lines:
            # 테두리 문자가 포함된 행에서 가장 오른쪽 인덱스 추출
            indices = [line.rfind(c) for c in ["|", "│", "┃", "┤", "┨", "┐", "┓"] if c in line]
            if indices:
                idx = max(indices)
                # 너무 짧은 행이나 내용이 없는 행은 제외
                if idx > 20: 
                    last_border_indices.append(idx)
        
        if not last_border_indices:
            self.fail("No border characters detected in output!")
            
        # 모든 테두리의 끝점이 일치해야 함 (정렬 무결성)
        first_idx = last_border_indices[0]
        for i, idx in enumerate(last_border_indices):
            self.assertEqual(idx, first_idx, f"Misalignment detected! Line {i} ends at {idx}, expected {first_idx}")

    def test_standard_screen_alignment(self):
        """표준 화면 (120x40) 정렬 테스트"""
        console = Console(width=120, height=40, file=io.StringIO(), force_terminal=True)
        ui = DashboardUI(console)
        self._check_alignment(console, ui)

    def test_small_screen_responsiveness(self):
        """작은 화면 (80x20)에서도 크래시 없이 렌더링되는지 테스트"""
        console = Console(width=80, height=20, file=io.StringIO(), force_terminal=True)
        ui = DashboardUI(console)
        try:
            with console.capture() as capture:
                console.print(ui.layout)
        except Exception as e:
            self.fail(f"UI crashed on small screen: {e}")

    def test_markup_rendering(self):
        """마크업 태그가 노출되지 않고 렌더링되는지 검증"""
        console = Console(width=100, height=30, file=io.StringIO(), force_terminal=True)
        ui = DashboardUI(console)
        ui.update_main([("system", "[bold red]CRITICAL[/]")])
        
        with console.capture() as capture:
            console.print(ui.layout)
        
        output = capture.get()
        self.assertNotIn("[bold red]", output, "Markup tags are exposed in the output!")
        self.assertIn("CRITICAL", output)

if __name__ == "__main__":
    unittest.main()
