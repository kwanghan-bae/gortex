import unittest
import importlib
import importlib.metadata # [NEW] pkg_resources 대체
import os
import stat

class TestEnvironmentIntegrity(unittest.TestCase):
    """
    TDD의 사각지대를 보완하기 위한 환경 무결성 테스트.
    """

    def test_requirements_installed(self):
        """1. requirements.txt에 명시된 패키지가 실제로 설치되어 있는지 검증"""
        required_packages = []
        try:
            with open("requirements.txt", "r") as f:
                required_packages = [
                    line.strip().split("==")[0] 
                    for line in f 
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            self.skipTest("requirements.txt not found")

        # [FIX] importlib.metadata를 사용하여 설치된 패키지 목록 획득
        installed_packages = {dist.metadata['Name'].lower().replace("_", "-") for dist in importlib.metadata.distributions()}
        
        missing_packages = []
        for package in required_packages:
            normalized_name = package.lower().replace("_", "-")
            if normalized_name not in installed_packages:
                missing_packages.append(package)

        self.assertFalse(missing_packages, f"🚨 필수 패키지 누락됨: {missing_packages}. './setup.sh'를 다시 실행하세요.")

    def test_critical_imports(self):
        """2. 핵심 모듈들이 에러 없이 실제로 임포트 되는지 검증 (ModuleNotFoundError 방지)"""
        critical_modules = [
            "psutil",
            "rich",
            "dotenv",
            "langchain_core",
            "pandas",
            # gortex 내부 모듈
            "gortex.core.engine",
            "gortex.utils.cache",
            "gortex.main" # 진입점 문법 오류 체크
        ]

        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                self.fail(f"🚨 핵심 모듈 임포트 실패: {module_name} -> {e}")
            except Exception as e:
                self.fail(f"🚨 모듈 로딩 중 크리티컬 에러: {module_name} -> {e}")

    def test_script_permissions(self):
        """3. 실행 스크립트(.sh)들이 실행 권한을 가지고 있는지 검증"""
        scripts = ["run.sh", "setup.sh", "start.sh"]
        for script in scripts:
            if os.path.exists(script):
                st = os.stat(script)
                self.assertTrue(bool(st.st_mode & stat.S_IXUSR), f"🚨 {script}에 실행 권한(x)이 없습니다. 'chmod +x {script}'가 필요합니다.")

if __name__ == "__main__":
    unittest.main()
