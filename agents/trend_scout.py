import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.agents.researcher import ResearcherAgent
from gortex.utils.vector_store import LongTermMemory

logger = logging.getLogger("GortexTrendScout")

class TrendScoutAgent:
    """
    인터넷 트렌드(신규 LLM, 에이전트 기법)를 검색하고 tech_radar.json을 업데이트하는 에이전트.
    """
    def __init__(self, radar_path: str = "tech_radar.json"):
        self.radar_path = radar_path
        self.auth = GortexAuth()
        self.researcher = ResearcherAgent()
        self.ltm = LongTermMemory()
        self.radar_data = self._load_radar()

    def _load_radar(self) -> Dict[str, Any]:
        if os.path.exists(self.radar_path):
            try:
                with open(self.radar_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load tech radar: {e}")
                return {}
        return {}

    def _save_radar(self):
        try:
            with open(self.radar_path, 'w', encoding='utf-8') as f:
                json.dump(self.radar_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tech radar: {e}")

    async def check_vulnerabilities(self) -> List[str]:
        """requirements.txt를 분석하여 알려진 보안 취약점 점검"""
        req_path = "requirements.txt"
        if not os.path.exists(req_path):
            return ["requirements.txt 파일을 찾을 수 없어 보안 점검을 건너뜁니다."]

        logger.info("🔍 Scanning for security vulnerabilities in dependencies...")
        try:
            with open(req_path, "r", encoding='utf-8') as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            if not packages:
                return ["점검할 패키지가 없습니다."]

            findings = []
            for pkg in packages[:10]: # 토큰 및 시간 절약을 위해 상위 10개 패키지 우선 점검
                query = f"security vulnerability {pkg} python cve 2024 2025"
                result = await self.researcher.search_and_summarize(query)
                findings.append(f"Package: {pkg}\n{result}")

            analysis_prompt = f"""
            다음은 프로젝트 의존성 패키지들에 대한 보안 검색 결과이다.
            심각한 취약점(Critical/High)이 발견되었는지 분석하고, 업데이트가 필요한 패키지 목록을 제안하라.
            
            [Search Results]
            {""}
            
            결과는 반드시 다음 JSON 형식을 따라라:
            {{
                "vulnerabilities_found": true/false,
                "risky_packages": [{{ "name": "패키지명", "cve": "CVE ID", "severity": "High/Medium", "recommendation": "최신 버전으로 업데이트 등" }}]
            }}
            """
            
            response = self.auth.generate("gemini-1.5-flash", [("user", analysis_prompt)], None)
            res_data = json.loads(response.text)
            
            notifications = []
            if res_data.get("vulnerabilities_found"):
                for p in res_data.get("risky_packages", []):
                    msg = f"⚠️ [보안 위험] {p['name']}: {p['recommendation']} ({p['severity']})"
                    notifications.append(msg)
                    # tech_radar에 보안 정보 기록
                    if "security_alerts" not in self.radar_data:
                        self.radar_data["security_alerts"] = []
                    self.radar_data["security_alerts"].append({
                        "package": p["name"],
                        "detected_at": datetime.now().isoformat(),
                        "details": p
                    })
                self._save_radar()
                return notifications
            return ["✅ 주요 패키지 보안 점검 결과, 알려진 심각한 취약점이 발견되지 않았습니다."]
            
        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            return [f"보안 점검 중 오류 발생: {e}"]

    def should_scan(self, interval_hours: int = 24) -> bool:
        """마지막 스캔으로부터 지정된 시간이 지났는지 확인"""
        last_scan_str = self.radar_data.get("last_scan")
        if not last_scan_str:
            return True
        
        try:
            last_scan = datetime.fromisoformat(last_scan_str)
            return datetime.now() > last_scan + timedelta(hours=interval_hours)
        except ValueError:
            return True

    async def scan_trends(self) -> List[str]:
        """웹 검색을 통해 트렌드 정보를 수집하고 분석"""
        logger.info("🚀 Scouting for new tech trends and LLM models...")
        
        # 1. 검색 쿼리 설정
        queries = [
            "latest free LLM API 2025",
            "Gemini API updates and new models",
            "new autonomous agent patterns and best practices python"
        ]
        
        findings = []
        for q in queries:
            result = await self.researcher.search_and_summarize(q)
            findings.append(result)

        # 2. 결과 분석 및 요약 (LLM)
        analysis_prompt = f"""
        다음은 최신 AI 트렌드 및 모델에 대한 검색 결과들이다.
        Gortex 시스템을 강화할 수 있는 신규 모델 소식이나 에이전트 설계 기법이 있는지 분석하라.
        
        [Search Results]
        {"".join(findings)}
        
        분석 결과를 바탕으로 'models'와 'patterns' 정보를 JSON 형식으로 추출하라.
        {{
            "models": [{{ "name": "모델명", "status": "new/updated", "note": "설명" }}],
            "patterns": [{{ "topic": "주제", "summary": "설명" }}]
        }}
        """
        
        response = self.auth.generate("gemini-1.5-flash", [("user", analysis_prompt)], None)
        
        try:
            # 응답 텍스트에서 JSON 추출 (정규식 또는 간단한 파싱)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                
                # 3. tech_radar.json 업데이트
                self.radar_data["last_scan"] = datetime.now().isoformat()
                self.radar_data["models"] = extracted.get("models", [])
                self.radar_data["patterns"] = extracted.get("patterns", [])
                self._save_radar()
                
                # [Knowledge Base Integration] 최신 트렌드를 장기 기억 저장소에 통합
                for m in extracted.get("models", []):
                    knowledge_text = f"최신 모델 정보: {m['name']}는 {m['status']} 상태이며, 특징은 다음과 같다: {m.get('note')}"
                    self.ltm.memorize(knowledge_text, {"source": "TrendScout", "type": "model", "topic": m['name']})
                
                for p in extracted.get("patterns", []):
                    knowledge_text = f"신규 에이전트 패턴: {p['topic']} - {p.get('summary')}"
                    self.ltm.memorize(knowledge_text, {"source": "TrendScout", "type": "pattern", "topic": p['topic']})

                # 알림용 요약 메시지 생성
                notifications = []
                for m in extracted.get("models", []):
                    notifications.append(f"✨ 신규 모델 발견: {m['name']} ({m['status']})")
                return notifications
        except Exception as e:
            logger.error(f"Trend analysis parsing failed: {e}")
            
        return ["트렌드 분석 중 오류가 발생했으나, 스캔은 완료되었습니다."]

    async def analyze_adoption_opportunity(self, file_list: List[str]) -> List[str]:
        """신기술 도입 기회 분석"""
        if not self.radar_data.get("models") and not self.radar_data.get("patterns"):
            return []
            
        logger.info("🕵️ Analyzing code adoption opportunities...")
        
        # 프로젝트 파일 구조 요약 (토큰 절약)
        file_summary = "\n".join(file_list[:50]) # 최대 50개 파일명만
        
        radar_summary = json.dumps({
            "models": self.radar_data.get("models", []),
            "patterns": self.radar_data.get("patterns", [])
        }, ensure_ascii=False)
        
        prompt = f"""
        다음은 현재 프로젝트의 파일 구조와 Tech Radar에서 발견된 신기술 목록이다.
        프로젝트에 도입할 만한 기술이나 패턴이 있는지 분석하고, 적용 대상 파일과 이유를 제안하라.
        
        [Project Files]
        {file_summary}
        
        [Tech Radar]
        {radar_summary}
        
        결과는 JSON으로:
        {{
            "candidates": [
                {{ "tech": "이름", "target_file": "경로", "reason": "이유", "effort": "High/Medium/Low" }}
            ]
        }}
        """
        try:
            response = self.auth.generate("gemini-1.5-flash", [("user", prompt)], {"response_mime_type": "application/json"})
            res_data = json.loads(response.text)
            candidates = res_data.get("candidates", [])
            
            if candidates:
                self.radar_data["adoption_candidates"] = candidates
                self._save_radar()
                return [f"💡 기술 도입 제안: {c['tech']} -> {c['target_file']} ({c['reason']})" for c in candidates]
        except Exception as e:
            logger.error(f"Adoption analysis failed: {e}")
            
        return []

import asyncio
import re

def trend_scout_node(state: GortexState) -> Dict[str, Any]:
    """TrendScout 노드 엔트리 포인트"""
    scout = TrendScoutAgent()
    
    interval = int(os.getenv("TREND_SCAN_INTERVAL_HOURS", "24"))
    
    if scout.should_scan(interval):
        # 비동기 실행 (Researcher와 동일한 패턴)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        file_list = list(state.get("file_cache", {}).keys())

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 트렌드 스캔과 보안 점검 병렬 실행
                f1 = executor.submit(lambda: asyncio.run(scout.scan_trends()))
                f2 = executor.submit(lambda: asyncio.run(scout.check_vulnerabilities()))
                notifications = f1.result() + f2.result()
                
                # 도입 기회 분석은 위 결과 반영 후 순차 실행
                f3 = executor.submit(lambda: asyncio.run(scout.analyze_adoption_opportunity(file_list)))
                notifications += f3.result()
        else:
            n1 = loop.run_until_complete(scout.scan_trends())
            n2 = loop.run_until_complete(scout.check_vulnerabilities())
            n3 = loop.run_until_complete(scout.analyze_adoption_opportunity(file_list))
            notifications = n1 + n2 + n3
            
        return {
            "messages": [("ai", "\n".join(notifications))],
            "next_node": "manager"
        }
    
    return {
        "next_node": "manager"
    }
