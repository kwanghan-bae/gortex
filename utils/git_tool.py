import subprocess
import logging
import os
import json
import urllib.request

logger = logging.getLogger("GortexGitTool")

class GitTool:
    """
    Git 명령어 실행 및 GitHub API 연동을 위한 보조 도구.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.github_token = os.getenv("GITHUB_TOKEN")

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

    # GitHub API 연동 추가
    def fetch_github_issues(self, repo_owner: str, repo_name: str) -> List[Dict[str, Any]]:
        """GitHub 저장소의 오픈된 이슈 목록 조회"""
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=open"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            logger.error(f"Failed to fetch GitHub issues: {e}")
            return []

    def create_github_pr(self, repo_owner: str, repo_name: str, title: str, body: str, head: str, base: str = "main"):
        """Pull Request 생성"""
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
        data = json.dumps({
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }).encode('utf-8')
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            raise e

if __name__ == "__main__":
    gt = GitTool()
    if gt.is_repo():
        print(f"Current Branch: {gt.get_current_branch()}")
        print(f"Status:\n{gt.status()}")
