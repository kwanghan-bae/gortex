import os
import shutil
import subprocess
import logging
import hashlib
import re
from datetime import datetime
from typing import Dict, Union, Tuple, Optional, List

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
    """안전한 원자적 파일 쓰기 및 자동 버전 아카이빙."""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        if os.path.exists(path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 1. 일반 백업
            backup_dir = "logs/backups"
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"{os.path.basename(path)}.{timestamp}.bak")
            shutil.copy2(path, backup_path)
            
            # 2. 타임머신 버전 아카이빙
            version_dir = os.path.join("logs/versions", path.replace("/", "_"))
            os.makedirs(version_dir, exist_ok=True)
            ext = os.path.splitext(path)[1]
            version_path = os.path.join(version_dir, f"v_{timestamp}{ext}")
            shutil.copy2(path, version_path)
            logger.info(f"🕰️ File version archived: {version_path}")
        
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

def deep_integrity_check(working_dir: str, current_cache: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
    """
    프로젝트 전체 파일의 무결성을 검사하고 업데이트된 캐시와 변경된 파일 목록을 반환합니다.
    """
    updated_cache = current_cache.copy()
    changed_files = []
    
    ignore_dirs = {'.git', 'venv', '__pycache__', '.DS_Store', 'logs', 'site-packages'}
    
    for root, dirs, filenames in os.walk(working_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in filenames:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, working_dir)
            
            actual_hash = get_file_hash(file_path)
            cached_hash = updated_cache.get(rel_path)
            
            if actual_hash != cached_hash:
                updated_cache[rel_path] = actual_hash
                changed_files.append(rel_path)
                
    # 삭제된 파일 처리
    deleted_files = []
    for path in list(updated_cache.keys()):
        if not os.path.exists(os.path.join(working_dir, path)):
            del updated_cache[path]
            deleted_files.append(path)
            
    return updated_cache, changed_files + [f"(deleted) {p}" for p in deleted_files]

def get_changed_files(working_dir: str, current_cache: Dict[str, str]) -> List[str]:
    """현재 캐시와 대조하여 변경된 파일 목록만 추출"""
    changed = []
    ignore_dirs = {'.git', 'venv', '__pycache__', 'logs', 'site-packages'}
    
    for root, dirs, filenames in os.walk(working_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in filenames:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, working_dir)
            
            actual_hash = get_file_hash(file_path)
            if actual_hash != current_cache.get(rel_path):
                changed.append(rel_path)
    return list(set(changed))

def apply_patch(path: str, start_line: int, end_line: int, new_content: str) -> str:
    """
    파일의 특정 범위(start_line~end_line)를 새로운 내용으로 교체합니다. (1-based index)
    """
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 범위 유효성 검사
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return f"Error: Invalid line range {start_line}-{end_line} (Total lines: {len(lines)})"
            
        # 패치 적용 (0-based 인덱스로 변환)
        new_lines = lines[:start_line-1] + [new_content + "\n"] + lines[end_line:]
        
        write_file(path, "".join(new_lines))
        return f"Successfully applied patch to {path} at lines {start_line}-{end_line}."
    except Exception as e:
        return f"Error applying patch: {str(e)}"

def register_new_node(node_name: str, function_name: str, file_name: str) -> str:
    """
    core/graph.py를 정적으로 분석하여 새로운 에이전트 노드를 등록합니다.
    """
    graph_path = "core/graph.py"
    try:
        with open(graph_path, "r", encoding='utf-8') as f:
            content = f.read()
            
        # 1. Import 추가
        import_stmt = f"from gortex.agents.{file_name} import {function_name}\n"
        if import_stmt not in content:
            content = import_stmt + content
            
        # 2. workflow.add_node 추가
        node_stmt = f'    workflow.add_node("{node_name}", {function_name})\n'
        if node_stmt not in content:
            # compile_gortex_graph 함수 내부 찾기
            content = content.replace("# 노드 추가", f"# 노드 추가\n{node_stmt}")
            
        write_file(graph_path, content)
        return f"✅ Successfully registered node '{node_name}' in core/graph.py. System reboot required."
    except Exception as e:
        return f"❌ Failed to register node: {e}"

def scan_security_risks(code: str) -> List[Dict[str, str]]:
    """생성된 코드 내의 보안 취약점 패턴 스캔"""
    risks = []
    patterns = [
        (r"(?i)(password|passwd|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded Secret"),
        (r"eval\(", "Dangerous function: eval()"),
        (r"exec\(", "Dangerous function: exec()"),
        (r"os\.system\(", "Dangerous function: os.system()"),
        (r"subprocess\.Popen\(.*shell=True", "Subprocess with shell=True"),
        (r"cursor\.execute\(f?['\"].*\{.*\}", "Potential SQL Injection")
    ]
    
    for pattern, risk_type in patterns:
        if re.search(pattern, code):
            risks.append({"type": risk_type, "pattern": pattern})
            
    return risks