import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.agents.researcher import ResearcherAgent

logger = logging.getLogger("GortexTrendScout")

class TrendScoutAgent:
    """
    인터넷 트렌드(신규 LLM, 에이전트 기법)를 검색하고 tech_radar.json을 업데이트하는 에이전트.
    """
    def __init__(self, radar_path: str = "tech_radar.json"):
        self.radar_path = radar_path
        self.auth = GortexAuth()
        self.researcher = ResearcherAgent()
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
                
                # 알림용 요약 메시지 생성
                notifications = []
                for m in extracted.get("models", []):
                    notifications.append(f"✨ 신규 모델 발견: {m['name']} ({m['status']})")
                return notifications
        except Exception as e:
            logger.error(f"Trend analysis parsing failed: {e}")
            
        return ["트렌드 분석 중 오류가 발생했으나, 스캔은 완료되었습니다."]

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

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(scout.scan_trends()))
                notifications = future.result()
        else:
            notifications = loop.run_until_complete(scout.scan_trends())
            
        return {
            "messages": [("ai", "\n".join(notifications))],
            "next_node": "manager"
        }
    
    return {
        "next_node": "manager"
    }
