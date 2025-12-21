import logging
import json
import os
import re
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
        self.ltm = LongTermMemory() # LTM 직접 소유 (복구)

    def calculate_efficiency_score(self, success: bool, tokens: int, latency_ms: int, energy_cost: int) -> float:
        """작업의 효율성을 수치화 (0~100) - 원본 정교한 공식 복구"""
        if not success: return 0.0
        
        # 비용 함수: 토큰 1개 = 0.01, 레이턴시 1ms = 0.01, 에너지 1 = 1.0 (가중치 적용)
        cost = (tokens * 0.01) + (latency_ms * 0.005) + (energy_cost * 2.0)
        # 효율성 = 기본 보상(100) / (비용 + 1)
        # 로그 스케일을 적용하여 비용 증가에 따른 점수 감소폭을 완화
        import math
        score = 100.0 / (1.0 + math.log1p(cost / 5.0))
        return round(min(100.0, score), 1)

    def scan_project_complexity(self, directory: str = ".") -> List[Dict[str, Any]]:
        """코드의 복잡도와 기술 부채 정밀 스캔 (원본 로직 복구)"""
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
                            
                            # 정밀 복잡도 추정 (Proxy for Cyclomatic Complexity)
                            score = len(re.findall(r"\b(if|elif|for|while|except|def|class|with|async)\b", content))
                            score += len(lines) // 20
                            
                            if score > 10:
                                debt_list.append({
                                    "file": path, 
                                    "score": score, 
                                    "reason": "High logical density" if score > 30 else "Moderate complexity",
                                    "issue": "파일의 논리적 밀도가 너무 높아 가독성이 저하됨",
                                    "refactor_strategy": "긴 메서드를 분리하고 관심사를 모듈로 격리하라"
                                })
                    except: pass
        return sorted(debt_list, key=lambda x: x["score"], reverse=True)

    def analyze_data(self, file_path: str) -> Dict[str, Any]:
        """데이터 파일(CSV, JSON 등) 정밀 분석 수행 (원본 로직 복구)"""
        try:
            import pandas as pd
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                summary = {
                    "rows": len(df), "columns": list(df.columns),
                    "stats": df.describe().to_dict()
                }
                return {"status": "success", "summary": summary, "file": file_path}
        except: pass
        return {"status": "failed", "reason": "Data analysis failed"}

    def identify_missing_tests(self) -> List[Dict[str, Any]]:
        """커버리지 리포트를 분석하여 테스트가 시급한 파일을 식별합니다."""
        try:
            # 실시간 커버리지 데이터 획득 시도 (명령어 실행)
            import subprocess
            subprocess.run(["python3", "-m", "coverage", "json", "-o", "logs/coverage.json"], capture_output=True)
            
            if os.path.exists("logs/coverage.json"):
                with open("logs/coverage.json", "r") as f:
                    data = json.load(f)
                
                results = []
                for file_path, info in data.get("files", {}).items():
                    summary = info.get("summary", {})
                    percent = summary.get("percent_covered", 100)
                    if percent < 80: # 80% 미만인 파일 대상
                        results.append({
                            "file": file_path,
                            "coverage": round(percent, 1),
                            "missing_lines": info.get("missing_lines", []),
                            "priority": "High" if percent < 50 else "Medium"
                        })
                return sorted(results, key=lambda x: x["coverage"])
        except Exception as e:
            logger.error(f"Failed to identify missing tests: {e}")
        return []