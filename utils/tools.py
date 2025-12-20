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

def write_file(path: str, content: str) -> str:
    """
    안전한 원자적(Atomic) 파일 쓰기를 수행합니다.
    1. 원본 파일이 존재하면 백업 생성 (logs/backups/)
    2. .tmp 파일에 작성
    3. os.replace로 원본 교체
    """
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 백업 생성
        if os.path.exists(path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "logs/backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{os.path.basename(path)}.{timestamp}.bak")
            shutil.copy2(path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Atomic Write
        tmp_path = path + ".tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.replace(tmp_path, path)
        return f"Successfully wrote to {path}"
        
    except Exception as e:
        error_msg = f"Error writing file {path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

def execute_shell(command: str, timeout: int = 300) -> str:
    """
    셸 명령어를 안전하게 실행합니다.
    파괴적인 명령어는 차단되며, 출력 길이는 제한됩니다.
    """
    # 1. 보안 검사 (Blacklist)
    forbidden_commands = ["rm -rf", "mkfs", "dd if=", ":(){ :|:& };:"]
    for cmd in forbidden_commands:
        if cmd in command:
            return f"❌ Security Alert: Forbidden command detected ('{cmd}'). Execution blocked."
    
    try:
        logger.info(f"Executing: {command}")
        
        # 2. 실행
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # 3. 출력 처리 (Truncate)
        def truncate(text: str, limit: int = 2000) -> str:
            if len(text) <= limit:
                return text
            half = limit // 2
            return text[:half] + f"\n... <truncated {len(text) - limit} chars> ...\n" + text[-half:]

        stdout = truncate(result.stdout)
        stderr = truncate(result.stderr)
        
        exit_code = result.returncode
        output = f"Exit Code: {exit_code}\nSTDOUT:\n{stdout}"
        if stderr:
            output += f"\nSTDERR:\n{stderr}"
            
        return output

    except subprocess.TimeoutExpired:
        return f"❌ Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"❌ Error executing command: {str(e)}"

def list_files(directory: str = ".") -> str:
    """
    현재 작업 디렉토리의 파일 목록을 반환합니다.
    .git, venv, __pycache__ 등 불필요한 디렉토리는 제외합니다.
    """
    try:
        files = []
        ignore_dirs = {{'.git', 'venv', '__pycache__', '.DS_Store', 'logs', 'site-packages'}}
        
        for root, dirs, filenames in os.walk(directory):
            # 무시할 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for f in filenames:
                if f in ignore_dirs:
                    continue
                rel_path = os.path.relpath(os.path.join(root, f), directory)
                files.append(rel_path)
        
        return "\n".join(sorted(files))
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file(path: str) -> str:
    """
    파일의 내용을 읽어 반환합니다.
    """
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"