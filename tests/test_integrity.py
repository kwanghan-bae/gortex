import unittest
import os

class TestCodebaseIntegrity(unittest.TestCase):
    """
    코드베이스의 물리적 온전성을 검사함.
    에이전트의 실수로 메서드나 로직이 유실되는 상황을 방지.
    """
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def check_file_for_ellipses(self, rel_path):
        full_path = os.path.join(self.base_dir, rel_path)
        if not os.path.exists(full_path):
            return
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # AI가 흔히 넣는 생략 패턴 검사
            ellipses = ["# ...", "(중략)", "(생략)"]
            for p in ellipses:
                self.assertNotIn(p, content, f"Placeholder '{p}' found in {rel_path}!")

    def test_core_files_integrity(self):
        """핵심 파일들에 생략 기호가 없는지 검사"""
        core_files = [
            "main.py",
            "agents/manager.py",
            "agents/planner.py",
            "agents/coder.py",
            "agents/analyst.py",
            "utils/tools.py"
        ]
        for f in core_files:
            self.check_file_for_ellipses(f)

    def test_method_preservation(self):
        """핵심 메서드가 유실되지 않고 존재하는지 검사"""
        checks = [
            ("agents/researcher.py", "async def scrape_url"),
            ("ui/three_js_bridge.py", "def convert_causal_graph_to_3d"),
            ("utils/tools.py", "def archive_project_artifacts")
        ]
        for file_path, method_name in checks:
            full_path = os.path.join(self.base_dir, file_path)
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn(method_name, content, f"Critical method '{method_name}' is missing from {file_path}!")

if __name__ == '__main__':
    unittest.main()
