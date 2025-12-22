import logging
import json
import os
import re
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.utils.vector_store import LongTermMemory

logger = logging.getLogger("GortexAnalystBase")

class AnalystAgent:
    """Gortex 시스템의 분석 및 진화 담당 에이전트 (Base Class)"""
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()
        self.memory = EvolutionaryMemory()
        self.ltm = LongTermMemory()

    def calculate_efficiency_score(self, success: bool, tokens: int, latency_ms: int, energy_cost: int) -> float:
        if not success: return 0.0
        cost = (tokens * 0.01) + (latency_ms * 0.005) + (energy_cost * 2.0)
        score = 100.0 / (1.0 + math.log1p(cost / 5.0))
        return round(min(100.0, score), 1)

    def scan_project_complexity(self, directory: str = ".") -> List[Dict[str, Any]]:
        debt_list = []
        ignore_dirs = {'.git', 'venv', '__pycache__', 'logs', 'site-packages'}
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for f in files:
                if f.endswith(".py"):
                    path = os.path.join(root, f)
                    try:
                        with open(path, 'r', encoding='utf-8') as file:
                            content = file.read()
                            lines = content.splitlines()
                            score = len(re.findall(r"\b(if|elif|for|while|except|def|class|with|async)\b", content))
                            score += len(lines) // 20
                            if score > 10:
                                debt_list.append({
                                    "file": path, "score": score, 
                                    "reason": "High logical density" if score > 30 else "Moderate complexity",
                                    "issue": "파일의 논리적 밀도가 너무 높아 가독성이 저하됨",
                                    "refactor_strategy": "긴 메서드를 분리하고 관심사를 모듈로 격리하라"
                                })
                    except: pass
        return sorted(debt_list, key=lambda x: x["score"], reverse=True)

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        try:
            import pandas as pd
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                return {"status": "success", "summary": df.describe().to_dict(), "file": file_path}
        except: pass
        return {"status": "failed", "reason": "Data analysis failed"}

    def identify_missing_tests(self) -> List[Dict[str, Any]]:
        try:
            import subprocess
            subprocess.run(["python3", "-m", "coverage", "json", "-o", "logs/coverage.json"], capture_output=True)
            if os.path.exists("logs/coverage.json"):
                with open("logs/coverage.json", "r") as f:
                    data = json.load(f)
                results = []
                for file_path, info in data.get("files", {}).items():
                    p = info.get("summary", {}).get("percent_covered", 100)
                    if p < 80:
                        results.append({"file": file_path, "coverage": round(p, 1), "missing_lines": info.get("missing_lines", [])})
                return sorted(results, key=lambda x: x["coverage"])
        except: pass
        return []

    def audit_architecture(self) -> List[Dict[str, Any]]:
        from gortex.utils.indexer import SynapticIndexer
        deps = SynapticIndexer().generate_dependency_graph()
        violations = []
        layers = {"utils": 0, "core": 1, "ui": 2, "agents": 3, "tests": 4}
        for dep in deps:
            s, t = dep["source"], dep["target"]
            sl = next((l for l in layers if f"gortex.{l}" in s or s.startswith(l)), None)
            tl = next((l for l in layers if f"gortex.{l}" in t or t.startswith(l)), None)
            if sl and tl and layers[sl] < layers[tl]:
                violations.append({"type": "Layer Violation", "source": s, "target": t, "reason": f"하위 레이어 '{sl}'가 상위 레이어 '{tl}'를 참조함"})
        return violations

    def synthesize_global_rules(self, model_id: str = "gemini-1.5-pro") -> str:
        rules = self.memory.memory
        if not rules: return "정리할 규칙이 없습니다."
        ctx = "".join([f"- [{r['severity']}] {r['learned_instruction']}\n" for r in rules])
        try:
            summary = self.backend.generate(model_id, [{"role": "user", "content": f"다음 규칙을 5가지 원칙으로 요약하라:\n{ctx}"}])
            rules_md_path = "docs/RULES.md"
            original = ""
            if os.path.exists(rules_md_path):
                with open(rules_md_path, 'r', encoding='utf-8') as f: original = f.read()
            section = "## 🤖 Auto-Evolved Coding Standards"
            new_c = f"{original.split(section)[0]}{section}\n\n> 갱신: {datetime.now()}\n\n{summary}" if section in original else f"{original}\n\n{section}\n\n{summary}"
            with open(rules_md_path, 'w', encoding='utf-8') as f: f.write(new_c)
            return "✅ 전역 규칙 종합 완료."
        except: return "❌ 실패"

    def generate_release_note(self, model_id: str = "gemini-1.5-pro") -> str:
        try:
            import subprocess
            git_log = subprocess.run(["git", "log", "-n", "10", "--pretty=format:%s"], capture_output=True, text=True).stdout
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            evo = "\n".join([f"- {h['metadata'].get('tech')} applied to {h['metadata'].get('file')}" for h in EfficiencyMonitor().get_evolution_history(limit=5)])
            prompt = f"다음 로그로 릴리즈 노트를 작성하라:\n\n[Git]\n{git_log}\n\n[Evo]\n{evo}"
            summary = self.backend.generate(model_id, [{"role": "user", "content": prompt}])
            with open("docs/release_note.md", "w", encoding="utf-8") as f:
                f.write(f"# 🚀 Gortex Release Note\n\n> Generated at: {datetime.now()}\n\n{summary}")
            return "✅ release_note.md 갱신 완료."
        except: return "❌ 실패"

    def bump_version(self) -> str:
        v_path = "VERSION"
        try:
            cur_v = "1.0.0"
            if os.path.exists(v_path):
                with open(v_path, "r") as f: cur_v = f.read().strip()
            parts = [int(p) for p in cur_v.split(".")] if "." in cur_v else [1, 0, 0]
            from gortex.utils.efficiency_monitor import EfficiencyMonitor
            if len(EfficiencyMonitor().get_evolution_history(limit=5)) >= 5:
                parts[1] += 1
                parts[2] = 0
            else:
                parts[2] += 1
            new_v = ".".join(map(str, parts))
            with open(v_path, "w") as f: f.write(new_v)
            return new_v
        except: return "Error"

    def generate_evolution_roadmap(self) -> List[Dict[str, Any]]:
        """지능 지수가 낮은 모듈을 식별하여 진화 우선순위 로드맵 생성"""
        from gortex.utils.indexer import SynapticIndexer
        intel_map = SynapticIndexer().calculate_intelligence_index()
        
        # 지능 지수가 낮은 순으로 정렬 (보완이 필요한 모듈)
        weak_modules = sorted(intel_map.items(), key=lambda x: x[1])
        
        # Tech Radar 후보군 획득
        adoption_candidates = []
        if os.path.exists("tech_radar.json"):
            try:
                with open("tech_radar.json", "r") as f:
                    radar_data = json.load(f)
                    adoption_candidates = radar_data.get("adoption_candidates", [])
            except: pass

        roadmap = []
        for file_path, score in weak_modules[:5]: # 가장 취약한 5개 모듈 대상
            # 해당 파일에 적용 가능한 신기술 제안 매칭
            suggested_tech = next((c["tech"] for c in adoption_candidates if c["target_file"] == file_path), "Refactoring Required")
            
            roadmap.append({
                "target": file_path,
                "current_maturity": score,
                "suggested_tech": suggested_tech,
                "priority": "High" if score < 10 else "Medium"
            })
            
        return roadmap
