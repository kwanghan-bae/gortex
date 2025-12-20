import os
import shutil
import subprocess
import logging
import hashlib
from datetime import datetime
from typing import Dict, Union, Tuple, Optional

logger = logging.getLogger("GortexTools")

def get_file_hash(path: str) -> str:
    """파일 내용의 MD5 해시를 계산합니다."""
    try:
        if not os.path.exists(path):
            return ""
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""

def write_file_with_hash(path: str, content: str) -> Tuple[str, str]:
    """파일을 작성하고 새로운 해시를 반환하는 통합 함수."""
    write_result = write_file(path, content)
    new_hash = get_file_hash(path)
    return write_result, new_hash

def write_file(path: str, content: str) -> str:
    """안전한 원자적 파일 쓰기."""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        if os.path.exists(path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "logs/backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{os.path.basename(path)}.{timestamp}.bak")
            shutil.copy2(path, backup_path)
        
        tmp_path = path + ".tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp_path, path)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file {path}: {str(e)}"

def list_files(directory: str = ".") -> str:
    """현재 작업 디렉토리 파일 목록 반환."""
    try:
        files = []
        ignore_dirs = {{'.git', 'venv', '__pycache__', '.DS_Store', 'logs', 'site-packages'}}
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in filenames:
                if f in ignore_dirs: continue
                files.append(os.path.relpath(os.path.join(root, f), directory))
        return "\n".join(sorted(files))
    except Exception as e:
        return f"Error: {str(e)}"

def execute_shell(command: str, timeout: int = 300) -> str:
    """셸 명령어 안전 실행 및 파일 시스템 변경 감지, 의존성 자동 업데이트."""
    forbidden_commands = ["rm -rf", "mkfs", "dd if=", ":(){ :|:& };:"]
    for cmd in forbidden_commands:
        if cmd in command:
            return f"❌ Security Alert: Forbidden command detected ('{cmd}'). Execution blocked."

    try:
        # 실행 전 스냅샷
        files_before = set(os.listdir("."))
        
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        
        # 실행 후 스냅샷
        files_after = set(os.listdir("."))
        fs_changed = files_before != files_after

        # [AUTO-DEPENDENCY] pip install 감지 시 requirements.txt 업데이트
        if "pip install" in command and result.returncode == 0:
            try:
                # 패키지명 추출 (단순 로직: 마지막 인자)
                parts = command.split()
                if len(parts) >= 3:
                    package_name = parts[-1]
                    # 이미 requirements.txt에 있는지 확인
                    req_path = "requirements.txt"
                    existing_reqs = []
                    if os.path.exists(req_path):
                        with open(req_path, "r") as f:
                            existing_reqs = [line.strip().split('==')[0].lower() for line in f if line.strip()]
                    
                    if package_name.lower() not in existing_reqs:
                        with open(req_path, "a") as f:
                            f.write(f"\n{package_name}")
                        logger.info(f"✅ Automatically added '{package_name}' to requirements.txt")
            except Exception as e:
                logger.warning(f"Failed to update requirements.txt: {e}")

        def truncate(text: str, limit: int = 2000) -> str:
            if len(text) <= limit: return text
            return text[:1000] + "\n... <truncated> ...\n" + text[-1000:]

        output = f"Exit Code: {result.returncode}\nSTDOUT:\n{truncate(result.stdout)}"
        if result.stderr:
            output += f"\nSTDERR:\n{truncate(result.stderr)}"
        
        if fs_changed:
            output += f"\n\n[SYSTEM HINT: File system has changed. Consider using 'list_files' or 'read_file' to update cache.]"
        return output
    except subprocess.TimeoutExpired:
        return "❌ Error: Command timed out."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def read_file(path: str) -> str:
    """파일 내용 읽기."""
    try:
        if not os.path.exists(path): return f"Error: File not found at {path}"
        with open(path, 'r', encoding='utf-8') as f: return f.read()
    except Exception as e:
        return f"Error: {str(e)}"