import subprocess
import logging
import os

logger = logging.getLogger("GortexGitTool")

class GitTool:
    """
    Git 명령어 실행 및 저장소 상태 관리를 위한 보조 도구.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def _run_git(self, args: list) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise Exception(f"Git error: {e.stderr}")

    def status(self) -> str:
        return self._run_git(["status", "--short"])

    def add_all(self):
        return self._run_git(["add", "."])

    def commit(self, message: str):
        return self._run_git(["commit", "-m", message])

    def push(self, remote: str = "origin", branch: str = "main"):
        return self._run_git(["push", remote, branch])

    def get_current_branch(self) -> str:
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def is_repo(self) -> bool:
        return os.path.exists(os.path.join(self.repo_path, ".git"))

if __name__ == "__main__":
    gt = GitTool()
    if gt.is_repo():
        print(f"Current Branch: {gt.get_current_branch()}")
        print(f"Status:\n{gt.status()}")
