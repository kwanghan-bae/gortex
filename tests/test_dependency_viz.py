import unittest
import os
from unittest.mock import MagicMock
from gortex.utils.indexer import SynapticIndexer
from gortex.agents.analyst.base import AnalystAgent
from gortex.ui.dashboard import DashboardUI
from rich.console import Console

class TestDependencyViz(unittest.TestCase):
    def setUp(self):
        self.indexer = SynapticIndexer()
        self.analyst = AnalystAgent()
        self.console = Console()
        self.ui = DashboardUI(self.console)

    def test_find_reverse_dependencies(self):
        """특정 심볼의 역방향 의존성 추적 테스트"""
        # 실제 프로젝트 인덱스 스캔 실행
        self.indexer.scan_project()
        
        # 핵심 유틸리티 'count_tokens' 추적
        # utils/token_counter.py 정의를 core/engine.py 등에서 호출함
        deps = self.indexer.find_reverse_dependencies("count_tokens")
        
        self.assertTrue(len(deps) > 0, "Should find at least one caller for count_tokens")
        
        # 호출자 중 하나가 engine.py 인지 확인
        callers = [d["file"] for d in deps]
        self.assertTrue(any("engine.py" in c for c in callers))

    def test_generate_impact_map_mermaid(self):
        """Mermaid 형식의 영향력 지도 생성 테스트"""
        # 의존성이 확실한 'count_tokens' 심볼에 대해 다이어그램 생성
        mermaid = self.analyst.generate_impact_map("count_tokens")
        
        # 'graph' 가 포함되어 있는지 확인 (TD 또는 RL)
        self.assertIn("graph", mermaid)
        self.assertIn("count_tokens", mermaid)
        
        if "Safe" not in mermaid:
            # 의존성이 발견되었을 때의 구조 검증
            self.assertIn("Target", mermaid)
            self.assertIn("classDef target", mermaid)

    def test_impact_panel_risk_coloring(self):
        """의존성 수에 따른 UI 위험 색상 적용 테스트"""
        # 1. 고위험 시나리오 (의존성 6개)
        deps_high = [{"file": f"file_{i}.py", "caller": "func", "type": "call"} for i in range(6)]
        self.ui.update_impact_panel("CriticalFunc", deps_high)
        
        # Panel의 title 및 border_style에 'red'가 포함되어야 함
        panel = self.ui.layout["impact"].renderable
        self.assertEqual(panel.border_style, "red")

        # 2. 저위험 시나리오 (의존성 1개)
        deps_low = [{"file": "util.py", "caller": "main", "type": "call"}]
        self.ui.update_impact_panel("SmallFunc", deps_low)
        
        panel_low = self.ui.layout["impact"].renderable
        self.assertEqual(panel_low.border_style, "green")

if __name__ == '__main__':
    unittest.main()
