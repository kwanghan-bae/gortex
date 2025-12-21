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
        """AST를 분석하여 클래스, 함수, 임포트, 호출 정보 추출"""
        definitions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions.append({
                    "type": "class",
                    "name": node.name,
                    "bases": [ast.unparse(b) for b in node.bases],
                    "line": node.lineno,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                # 함수 내부의 다른 함수 호출 수집
                calls = []
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        try:
                            call_name = ast.unparse(subnode.func)
                            calls.append(call_name)
                        except: pass
                
                definitions.append({
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "calls": list(set(calls)), # 중복 제거
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    definitions.append({"type": "import", "name": alias.name, "line": node.lineno})
            elif isinstance(node, ast.ImportFrom):
                definitions.append({"type": "import_from", "module": node.module, "names": [alias.name for alias in node.names], "line": node.lineno})
        return definitions

    def generate_call_graph(self) -> Dict[str, Any]:
        """함수 간 호출 관계 그래프 생성"""
        nodes = {}
        edges = []
        for file_path, defs in self.index.items():
            for d in defs:
                if d["type"] == "function":
                    func_id = f"{file_path}:{d['name']}"
                    nodes[func_id] = {"name": d["name"], "file": file_path}
                    for called in d.get("calls", []):
                        # 프로젝트 내의 다른 함수를 호출하는지 매칭 (단순화된 이름 기반 매칭)
                        edges.append({"from": func_id, "to_name": called})
        return {"nodes": nodes, "edges": edges}

    def generate_map(self) -> Dict[str, Any]:
        """프로젝트의 모듈간 관계 및 클래스 계층 구조 맵 생성"""
        proj_map = {"nodes": {}, "edges": []}
        for file_path, defs in self.index.items():
            module_name = file_path.replace("/", ".").replace(".py", "")
            proj_map["nodes"][module_name] = {
                "file": file_path,
                "classes": [d["name"] for d in defs if d["type"] == "class"],
                "functions": [d["name"] for d in defs if d["type"] == "function"]
            }
            # 임포트 관계 추출
            for d in defs:
                if d["type"] == "import":
                    proj_map["edges"].append({"from": module_name, "to": d["name"], "type": "dependency"})
                elif d["type"] == "import_from" and d["module"]:
                    proj_map["edges"].append({"from": module_name, "to": d["module"], "type": "dependency"})
                elif d["type"] == "class" and d.get("bases"):
                    for base in d["bases"]:
                        proj_map["edges"].append({"from": d["name"], "to": base, "type": "inheritance"})
        return proj_map

    def generate_knowledge_graph(self) -> Dict[str, Any]:
        """코드 구조와 진화적 메모리를 결합한 통합 지식 그래프 생성"""
        from gortex.core.evolutionary_memory import EvolutionaryMemory
        evo_mem = EvolutionaryMemory()
        rules = evo_mem.rules
        
        # 1. 기존 프로젝트 맵(코드 구조) 생성
        kg = self.generate_map()
        
        # 2. 규칙 노드 추가
        for rule in rules:
            rule_id = rule.get("id", "UNKNOWN_RULE")
            kg["nodes"][rule_id] = {
                "type": "rule",
                "instruction": rule.get("instruction"),
                "severity": rule.get("severity"),
                "triggers": rule.get("trigger_patterns", [])
            }
            
            # 3. 규칙과 관련 코드 노드 연결 (트리거 패턴 기반 단순 매칭)
            for pattern in rule.get("trigger_patterns", []):
                for node_id, node_info in kg["nodes"].items():
                    if pattern.lower() in node_id.lower():
                        kg["edges"].append({
                            "from": rule_id, 
                            "to": node_id, 
                            "type": "constrains"
                        })
        return kg

    def _save_index(self):
        """인덱스를 JSON 파일로 저장"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def search(self, query: str, normalize: bool = False) -> List[Dict[str, Any]]:
        """인덱스 내에서 검색 (지능형 쿼리 정규화 및 점수화 지원)"""
        search_query = query.lower()
        
        if normalize:
            from gortex.core.auth import GortexAuth
            auth = GortexAuth()
            prompt = f"다음 자연어 질문을 코드 검색을 위한 핵심 기술 키워드(함수명, 클래스명 등)로 변환하라: {query}"
            try:
                response = auth.generate("gemini-1.5-flash", [("user", prompt)], None)
                search_query = response.text.strip().lower()
                logger.info(f"🔍 Normalized query: '{query}' -> '{search_query}'")
            except:
                pass

        results = []
        for file_path, defs in self.index.items():
            for d in defs:
                symbol_name = d.get("name", "").lower()
                # 1. 심볼명 매칭 (가중치 100)
                name_match = search_query in symbol_name
                # 2. 독스트링 매칭 (가중치 50)
                doc_match = d.get("docstring") and search_query in d["docstring"].lower()
                
                if name_match or doc_match:
                    results.append({
                        "file": file_path,
                        "score": 100 if name_match else 50,
                        **d
                    })
        
        # 점수 순 정렬
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_impact_radius(self, target_file: str) -> Dict[str, List[str]]:
        """특정 파일 수정 시 영향을 받는 직접/간접 모듈 분석"""
        if not self.index:
            self.scan_project()
            
        target_module = target_file.replace("/", ".").replace(".py", "")
        direct_impact = []
        indirect_impact = []
        
        # 1단계: 직접 임포트 또는 호출하는 모듈 찾기
        for file_path, defs in self.index.items():
            if file_path == target_file: continue
            
            is_direct = False
            for d in defs:
                # 임포트 확인
                if d["type"] == "import" and target_module in d["name"]:
                    is_direct = True
                elif d["type"] == "import_from" and d["module"] and target_module.endswith(d["module"]):
                    is_direct = True
                # 함수 호출 확인 (단순 이름 기반)
                target_funcs = [def_item["name"] for def_item in self.index.get(target_file, []) if def_item["type"] == "function"]
                if d["type"] == "function" and any(tf in d.get("calls", []) for tf in target_funcs):
                    is_direct = True
                    
            if is_direct:
                direct_impact.append(file_path)

        # 2단계: 간접 영향(직접 영향 받는 모듈을 다시 참조하는 모듈)
        for file_path, defs in self.index.items():
            if file_path == target_file or file_path in direct_impact: continue
            
            for direct in direct_impact:
                direct_mod = direct.replace("/", ".").replace(".py", "")
                if any(d["type"] in ["import", "import_from"] and (direct_mod in str(d.get("name", "")) or direct_mod in str(d.get("module", ""))) for d in defs):
                    indirect_impact.append(file_path)
                    break
                    
        return {
            "target": target_file,
            "direct": list(set(direct_impact)),
            "indirect": list(set(indirect_impact))
        }

if __name__ == "__main__":
    # 독립 실행 테스트
    logging.basicConfig(level=logging.INFO)
    indexer = SynapticIndexer()
    indexer.scan_project()
    print(f"Search result for 'Gortex': {indexer.search('Gortex')}")
