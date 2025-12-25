
import os
import re
import fnmatch
from typing import List, Dict, Any
from .base import BaseTool

class FindByNameTool(BaseTool):
    """파일 이름 패턴으로 파일 검색 (gitignore 스타일 무시 규칙 적용)"""

    def execute(self, pattern: str, path: str = ".") -> List[str]:
        found_files = []
        # 기본 무시 목록
        ignore_dirs = {'.git', 'venv', '__pycache__', '.DS_Store', 'site-packages', 'node_modules', '.idea'}
        
        for root, dirs, files in os.walk(path):
            # 디렉토리 필터링 (In-place modification for pruning)
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # 패턴 매칭
            for filename in fnmatch.filter(files, pattern):
                full_path = os.path.join(root, filename)
                # 상대 경로 변환
                rel_path = os.path.relpath(full_path, start=path)
                found_files.append(rel_path)
            
        return sorted(found_files)

class GrepSearchTool(BaseTool):
    """파일 내용 검색 (grep 유사)"""

    def execute(self, query: str, path: str = ".") -> List[Dict[str, Any]]:
        results = []
        ignore_dirs = {'.git', 'venv', '__pycache__', '.DS_Store', 'site-packages', 'node_modules', '.idea'}
        
        # 정규식 컴파일
        try:
            regex = re.compile(query)
        except re.error:
            regex = re.compile(re.escape(query))
            
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                # 파일명 자체 필터링 가능 (확장자 등)
                if file.startswith('.'): continue 
                
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": os.path.relpath(file_path, path),
                                    "line": i,
                                    "content": line.strip()
                                })
                except Exception:
                    continue
                    
        return results
