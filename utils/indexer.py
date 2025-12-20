import ast
import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger("GortexIndexer")

class SynapticIndexer:
    """
    프로젝트의 코드를 정적으로 분석하여 함수, 클래스, 변수 정의를 인덱싱하는 엔진.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.index_path = "logs/synaptic_index.json"
        self.index = {}

    def scan_project(self):
        """프로젝트 내의 모든 Python 파일을 스캔하여 인덱싱"""
        logger.info(f"🚀 Starting synaptic indexing for {self.root_dir}...")
        new_index = {}
        
        for root, dirs, files in os.walk(self.root_dir):
            # 무시할 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in {'.git', 'venv', '__pycache__', 'logs', 'build', 'dist'}]
            
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    try:
                        with open(full_path, "r", encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                            new_index[rel_path] = self._analyze_tree(tree)
                    except Exception as e:
                        logger.error(f"Failed to index {rel_path}: {e}")
        
        self.index = new_index
        self._save_index()
        logger.info(f"✅ Indexing complete. Indexed {len(new_index)} files.")

    def _analyze_tree(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """AST를 분석하여 클래스와 함수 정보 추출"""
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions.append({
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                definitions.append({
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
        return definitions

    def _save_index(self):
        """인덱스를 JSON 파일로 저장"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """인덱스 내에서 검색 쿼리와 일치하는 정의를 검색"""
        results = []
        query = query.lower()
        
        for file_path, defs in self.index.items():
            for d in defs:
                if query in d["name"].lower() or (d.get("docstring") and query in d["docstring"].lower()):
                    results.append({
                        "file": file_path,
                        **d
                    })
        return results

if __name__ == "__main__":
    # 독립 실행 테스트
    logging.basicConfig(level=logging.INFO)
    indexer = SynapticIndexer()
    indexer.scan_project()
    print(f"Search result for 'Gortex': {indexer.search('Gortex')}")
