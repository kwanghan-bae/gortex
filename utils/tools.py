import os
import shutil
import subprocess
import logging
from datetime import datetime
from typing import Dict, Union

logger = logging.getLogger("GortexTools")

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
