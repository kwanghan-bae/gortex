import os
import shutil
import subprocess
import logging
import hashlib
import re
import json
import ast
import zipfile
from datetime import datetime
from typing import Dict, Tuple, List, Any

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
        
        # [DISTRIBUTED SYNC] 변경 사항 전파
        try:
            from gortex.core.mq import mq_bus
            if mq_bus.is_connected:
                file_hash = hashlib.md5(content.encode()).hexdigest()
                mq_bus.broadcast_file_change(path, content, file_hash)
                logger.debug(f"🌐 Broadcasted file change: {path}")
        except Exception as sync_e:
            logger.warning(f"Failed to broadcast file change: {sync_e}")
            
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file {path}: {str(e)}"

def list_files(directory: str = ".") -> str:
    """현재 작업 디렉토리 파일 목록 반환."""
    try:
        files = []
        ignore_dirs = {'.git', 'venv', '__pycache__', '.DS_Store', 'logs', 'site-packages'}
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in filenames:
                if f in ignore_dirs:
                    continue
                rel_path = os.path.relpath(os.path.join(root, f), directory)
                if '.git' in rel_path:
                    continue
                files.append(rel_path)
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
                parts = command.split()
                if len(parts) >= 3:
                    package_name = parts[-1]
                    req_path = "requirements.txt"
                    existing_reqs = []
                    if os.path.exists(req_path):
                        with open(req_path, "r") as f:
                            existing_reqs = [line.strip().split('==')[0].lower() for line in f if line.strip()]
                    
                    if package_name.lower() not in existing_reqs:
                        with open(req_path, "a") as f:
                            f.write(f"\n{package_name}")
                        logger.info(f"✅ Automatically added '{package_name}' to requirements.txt")
                        
                        # [INTEGRITY] 서명 갱신 트리거
                        try:
                            from gortex.utils.integrity import guard
                            guard.generate_master_signature()
                            logger.info("🛡️ Master system signature refreshed after environment change.")
                        except Exception: pass
            except Exception as e:
                logger.warning(f"Failed to update requirements.txt: {e}")

        def truncate(text: str, limit: int = 2000) -> str:
            if len(text) <= limit:
                return text
            return text[:1000] + "\n... <truncated> ...\n" + text[-1000:]

        output = f"Exit Code: {result.returncode}\nSTDOUT:\n{truncate(result.stdout)}"
        if result.stderr:
            output += f"\nSTDERR:\n{truncate(result.stderr)}"
        
        if fs_changed:
            output += "\n\n[SYSTEM HINT: File system has changed. Consider using 'list_files' or 'read_file' to update cache.]"
        return output
    except subprocess.TimeoutExpired:
        return "❌ Error: Command timed out."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def read_file(path: str, limit: int = None, offset: int = 0) -> str:
    """파일 내용 읽기 (페이지네이션 지원)."""
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        if offset > 0:
            lines = lines[offset:]
            
        truncated = False
        if limit is not None and len(lines) > limit:
            lines = lines[:limit]
            truncated = True
            
        content = "".join(lines)
        if truncated:
            content += f"\n... (truncated, total {total_lines} lines) ...\n(truncated)"
        return content
    except Exception as e:
        return f"Error: {str(e)}"

def deep_integrity_check(working_dir: str, current_cache: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
    """프로젝트 전체 파일의 무결성을 검사하고 업데이트된 캐시와 변경된 파일 목록을 반환합니다."""
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
    """파일의 특정 범위를 새로운 내용으로 교체합니다."""
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return f"Error: Invalid line range {start_line}-{end_line}"
        new_lines = lines[:start_line-1] + [new_content + "\n"] + lines[end_line:]
        write_file(path, "".join(new_lines))
        return f"Successfully applied patch to {path}."
    except Exception as e:
        return f"Error applying patch: {str(e)}"

def register_new_node(node_name: str, function_name: str, file_name: str) -> str:
    """core/graph.py를 정적으로 분석하여 새로운 에이전트 노드를 등록합니다."""
    graph_path = "core/graph.py"
    try:
        with open(graph_path, "r", encoding='utf-8') as f:
            content = f.read()
        import_stmt = f"from gortex.agents.{file_name} import {function_name}\n"
        if import_stmt not in content:
            content = import_stmt + content
        node_stmt = f'    workflow.add_node("{node_name}", {function_name})\n'
        if node_stmt not in content:
            content = content.replace("# 노드 추가", f"# 노드 추가\n{node_stmt}")
        write_file(graph_path, content)
        return f"✅ Registered node '{node_name}'. Reboot required."
    except Exception as e:
        return f"❌ Failed: {e}"

def scan_security_risks(code: str) -> List[Dict[str, str]]:
    """생성된 코드 내의 보안 취약점 패턴 스캔"""
    risks = []
    patterns = [
        (r'''(?i)(password|passwd|secret|api_key|token)\s*=\s*['"].*['"]''', "Hardcoded Secret"),
        (r"eval\(", "Dangerous function: eval()"),
        (r"exec\(", "Dangerous function: exec()"),
        (r"os\.system\(", "Dangerous function: os.system()"),
        (r"subprocess\.Popen\(.*shell=True", "Subprocess with shell=True"),
        (r'''cursor\.execute\(f?['"].*\{.*}''', "Potential SQL Injection")
    ]
    for pattern, risk_type in patterns:
        if re.search(pattern, code):
            risks.append({"type": risk_type, "pattern": pattern})
    return risks

def archive_project_artifacts(project_name: str, version: str, files: List[str]) -> str:
    """프로젝트 생성물들을 버전별로 구조화하여 아카이빙"""
    try:
        archive_root = os.path.join("logs", "archives", project_name, version)
        os.makedirs(archive_root, exist_ok=True)
        moved_count = 0
        for f_path in files:
            if os.path.exists(f_path):
                dest = os.path.join(archive_root, os.path.basename(f_path))
                shutil.move(f_path, dest)
                moved_count += 1
        return f"✅ Archived {moved_count} artifacts to {archive_root}"
    except Exception as e:
        return f"❌ Archive failed: {e}"

def backup_file_with_rotation(file_path: str, backup_dir: str = "logs/backups", max_versions: int = 5) -> str:
    """파일을 백업하고 오래된 버전을 회전(삭제)시킴."""
    if not os.path.exists(file_path):
        return f"Error: Source file {file_path} not found."
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{base_name}.{timestamp}.bak")
        
        # 백업 생성
        shutil.copy2(file_path, backup_path)
        
        # 회전(Rotation) 로직: 해당 파일의 백업 목록 조회
        backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith(base_name) and f.endswith(".bak")]
        backups.sort(key=os.path.getmtime, reverse=True) # 최신순 정렬
        
        # max_versions 개수 초과분 삭제
        if len(backups) > max_versions:
            for old_backup in backups[max_versions:]:
                os.remove(old_backup)
                logger.info(f"🗑️ Rotated old backup: {old_backup}")
                
        return f"Successfully backed up {file_path} to {backup_path}"
    except Exception as e:
        return f"Error during backup rotation: {e}"

def safe_bulk_delete(file_paths: List[str]) -> Dict[str, Any]:
    """대량의 파일을 안전하게 삭제하고 결과를 보고함. 핵심 파일 보호 기능 포함."""
    results = {"success": [], "failed": [], "protected": []}
    
    # 절대 삭제하면 안 되는 보호 패턴
    protected_patterns = ["experience", "shard", "trace_summary", "release_note", "MILESTONE"]
    
    for path in file_paths:
        if not os.path.exists(path):
            continue
            
        # 보호 로직
        if any(p in path for p in protected_patterns):
            results["protected"].append(path)
            logger.warning(f"🛡️ Protected file deletion blocked: {path}")
            continue
            
        try:
            os.remove(path)
            results["success"].append(path)
        except Exception as e:
            results["failed"].append({"path": path, "error": str(e)})
            logger.error(f"Failed to delete {path}: {e}")
            
    logger.info(f"🧹 Bulk cleanup: {len(results['success'])} deleted, {len(results['protected'])} protected.")
    return results

def repair_and_load_json(text: str) -> Dict[str, Any]:
    """
    로컬 LLM이 생성한 비정형 텍스트에서 JSON을 추출하고 흔한 오류를 복구합니다.
    """
    if not text:
        return {}
    
    # 1. Markdown 코드 블록 제거
    clean_text = re.sub(r"```json\n?|```\n?", "", text).strip()
    
    # 2. 추출 시도: 최대한 JSON처럼 보이는 구간을 찾음
    # { 또는 [ 로 시작하는 지점부터 끝까지 추출 (닫는 괄호가 없을 수도 있으므로)
    match = re.search(r"(\{.*\}|\[.*\])", clean_text, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        # 괄호가 쌍으로 안 맞아도 일단 시작점부터 끝까지 시도
        match_start = re.search(r"(\{|\[).*", clean_text, re.DOTALL)
        json_str = match_start.group(0) if match_start else clean_text

    # 3. 홑따옴표를 쌍따옴표로 먼저 변환 (흔한 오류)
    json_str = json_str.replace("'", '"')

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 4. 구조적 오류 복구 시도
        try:
            # 불완전한 종료 중괄호 보정
            open_braces = json_str.count("{")
            close_braces = json_str.count("}")
            if open_braces > close_braces:
                json_str += "}" * (open_braces - close_braces)
            
            # 불완전한 종료 대괄호 보정
            open_brackets = json_str.count("[")
            close_brackets = json_str.count("]")
            if open_brackets > close_brackets:
                json_str += "]" * (open_brackets - close_brackets)
                
            # 마지막 쉼표 제거 (Trailing comma)
            json_str = re.sub(r",\s*(\}|\])", r"\1", json_str)
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"JSON Recovery failed: {e}")
            return {}

def verify_patch_integrity(file_path: str) -> Dict[str, Any]:
    """
    적용된 패치가 시스템 무결성을 해치지 않는지 검증 (Syntax + Tests).
    """
    if not os.path.exists(file_path):
        return {"success": False, "reason": "File not found"}

    # 1. Syntax Check
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
    except SyntaxError as e:
        return {"success": False, "reason": f"Syntax Error: {e}"}
    except Exception as e:
        return {"success": False, "reason": str(e)}

    # 2. Selective Test Execution
    # 파일명 기반으로 대응하는 테스트 파일 추측 (예: core/auth.py -> tests/test_auth.py)
    base_name = os.path.basename(file_path).replace(".py", "")
    test_file = f"tests/test_{base_name}.py"
    
    if os.path.exists(test_file):
        res = execute_shell(f"python3 -m unittest {test_file}")
        if "OK" in res:
            return {"success": True, "details": "Syntax and Tests passed."}
        else:
            return {"success": False, "reason": "Tests failed after patch.", "output": res}
    
    return {"success": True, "details": "Syntax passed (No matching test found)."}

def package_release_candidate(version: str, output_dir: str = "logs/archives") -> str:
    """현재 안정적인 소스 코드를 배포 후보(RC)로 패키징함."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"Gortex_RC_{version}.zip")
    
    ignore_patterns = [
        ".git", "venv", "__pycache__", ".DS_Store", "site-packages", 
        "logs", ".idea", ".pytest_cache", "training_jobs", "gortex"
    ]
    
    return compress_directory(".", output_path, ignore_patterns=ignore_patterns)

def compress_directory(source_dir: str, output_path: str, ignore_patterns: List[str] = None) -> str:
    """디렉토리 전체를 ZIP 아카이브로 압축 (특정 패턴 제외)"""
    if ignore_patterns is None:
        ignore_patterns = [".git", "venv", "__pycache__", ".DS_Store", "site-packages", "logs/archives"]
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                dirs[:] = [d for d in dirs if d not in ignore_patterns]
                for file in files:
                    if any(p in file for p in ignore_patterns):
                        continue
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, source_dir)
                    zipf.write(full_path, rel_path)
        return f"✅ Directory compressed to {output_path}"
    except Exception as e:
        return f"❌ Compression failed: {e}"

def safe_json_extract(text: str) -> Dict[str, Any]:
    """텍스트에서 JSON 블록을 안전하게 추출하고 파싱합니다."""
    if not text:
        return {}
    import re
    import json
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return {}
    json_str = match.group(0)
    try:
        return json.loads(json_str)
    except Exception:
        try:
            return json.loads(json_str.replace("'", '"'))
        except Exception:
            return {}
