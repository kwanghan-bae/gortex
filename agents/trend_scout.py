import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from gortex.core.llm.factory import LLMFactory
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
        self.backend = LLMFactory.get_default_backend()
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

    async def check_vulnerabilities(self, model_id: str = "gemini-1.5-flash") -> List[str]:
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
            {"".join(findings)}
            
            결과는 반드시 다음 JSON 형식을 따라라:
            {{
                "vulnerabilities_found": true/false,
                "risky_packages": [{{ "name": "패키지명", "cve": "CVE ID", "severity": "High/Medium", "recommendation": "최신 버전으로 업데이트 등" }}]
            }}
            """
            
            config = {"temperature": 0.0}
            if self.backend.supports_structured_output():
                from google.genai import types
                config = types.GenerateContentConfig(response_mime_type="application/json")

            response_text = self.backend.generate(model_id, [{"role": "user", "content": analysis_prompt}], config)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
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

    async def scan_trends(self, model_id: str = "gemini-1.5-flash") -> List[str]:
        """웹 검색을 통해 트렌드 정보를 수집하고 분석"""
        logger.info("🚀 Scouting for new tech trends and LLM models...")
        
        # [OPTIMIZATION] 쿼리 개수 축소 (지연 방지)
        queries = [
            "latest LLM agent trends 2025"
        ]
        
        findings = []
        for q in queries:
            try:
                # Researcher 타임아웃 활용
                result = await self.researcher.search_and_summarize(q)
                findings.append(result)
            except Exception as e:
                logger.warning(f"Trend search failed for '{q}': {e}")

        # 분석할 데이터가 없으면 즉시 종료
        if not findings or not "".join(findings).strip():
            return ["새로운 트렌드 정보를 찾지 못했습니다."]

        # 2. 결과 분석 및 요약 (LLM)
        analysis_prompt = f"""
        다음은 AI 트렌드 검색 결과이다. Gortex 시스템을 강화할 수 있는 신규 모델이나 에이전트 기법을 JSON으로 추출하라.
        
        [Search Results]
        {"".join(findings)[:4000]}
        
        {{
            "models": [{{ "name": "모델명", "status": "new/updated", "note": "설명" }}],
            "patterns": [{{ "topic": "주제", "summary": "설명" }}]
        }}
        """
        
        config = {"temperature": 0.0}
        if self.backend.supports_structured_output():
            from google.genai import types
            config = types.GenerateContentConfig(response_mime_type="application/json")

        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": analysis_prompt}], config)
            
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                
                # 3. tech_radar.json 업데이트
                self.radar_data["last_scan"] = datetime.now().isoformat()
                
                # 테스트 환경의 Mock 객체 방어 로직 (JSON 직렬화 가능 여부 체크)
                if not isinstance(extracted, dict):
                    extracted = {}
                
                models = extracted.get("models", [])
                patterns = extracted.get("patterns", [])
                
                # 리스트 타입이 아니면 (Mock 등) 빈 리스트로 초기화
                if not isinstance(models, list): models = []
                if not isinstance(patterns, list): patterns = []
                
                self.radar_data["models"] = models
                self.radar_data["patterns"] = patterns
                self._save_radar()
                
                # [Knowledge Base Integration] 최신 트렌드를 장기 기억 저장소에 통합
                for m in models:
                    if isinstance(m, dict) and "name" in m:
                        knowledge_text = f"최신 모델 정보: {m.get('name')}는 {m.get('status')} 상태이며, 특징은 다음과 같다: {m.get('note')}"
                        self.ltm.memorize(knowledge_text, {"source": "TrendScout", "type": "model", "topic": m.get('name')})
                
                for p in patterns:
                    if isinstance(p, dict) and "topic" in p:
                        knowledge_text = f"신규 에이전트 패턴: {p.get('topic')} - {p.get('summary')}"
                        self.ltm.memorize(knowledge_text, {"source": "TrendScout", "type": "pattern", "topic": p.get('topic')})

                # 알림용 요약 메시지 생성
                notifications = []
                for m in models:
                    if isinstance(m, dict):
                        notifications.append(f"✨ 신규 모델 발견: {m.get('name')} ({m.get('status')})")
                return notifications
        except Exception as e:
            logger.error(f"Trend analysis parsing failed: {e}")
            # 파싱 실패 시 원문을 요약하여 반환 (가짜 데이터 생성 금지)
            return [f"트렌드 스캔 완료 (구조화 실패): {response_text[:200]}..."]
            
        return ["트렌드 분석 스캔은 완료되었으나 새로운 항목이 발견되지 않았습니다."]

    async def analyze_adoption_opportunity(self, file_list: List[str], model_id: str = "gemini-1.5-flash") -> List[str]:
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
        config = {"temperature": 0.0}
        if self.backend.supports_structured_output():
            from google.genai import types
            config = types.GenerateContentConfig(response_mime_type="application/json")

        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}], config)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            candidates = res_data.get("candidates", [])
            
            if candidates:
                self.radar_data["adoption_candidates"] = candidates
                self._save_radar()
                return [f"💡 기술 도입 제안: {c['tech']} -> {c['target_file']} ({c['reason']})" for c in candidates]
        except Exception as e:
            logger.error(f"Adoption analysis failed: {e}")
            
        return []

    async def propose_new_agents(self, model_id: str = "gemini-1.5-flash") -> List[Dict[str, Any]]:
        """Tech Radar 정보를 바탕으로 시스템에 필요한 신규 전문가 에이전트 영입 제안"""
        if not self.radar_data.get("patterns") and not self.radar_data.get("models"):
            return []

        logger.info("🔭 Designing proactive agent expansion strategies...")
        
        radar_summary = json.dumps({
            "models": self.radar_data.get("models", []),
            "patterns": self.radar_data.get("patterns", [])
        }, ensure_ascii=False)

        prompt = f"""
        당신은 Gortex 시스템의 지능 확장 전략가입니다. 
        아래의 테크 레이더 정보를 분석하여, Gortex v3.0의 성능을 획기적으로 높일 수 있는 '새로운 전문가 에이전트'를 1개 설계하십시오.
        
        [Tech Radar]
        {radar_summary}
        
        에이전트 설계 조건:
        1. 기존의 Manager, Coder, Planner, Analyst와 역할이 겹치지 않아야 합니다.
        2. 구체적인 도구(Tools)와 실행 전략을 포함해야 합니다.
        
        결과는 JSON으로만 반환하십시오:
        {{
            "proposed_agent": {{
                "agent_name": "UniqueNameAgent",
                "role": "역할명",
                "description": "상세 설명",
                "required_tools": ["tool1", "tool2"],
                "logic_strategy": "핵심 알고리즘/동작 방식",
                "strategic_value": "이 에이전트를 도입했을 때의 이득"
            }}
        }}
        """
        
        config = {"temperature": 0.0}
        if self.backend.supports_structured_output():
            from google.genai import types
            config = types.GenerateContentConfig(response_mime_type="application/json")

        try:
            response_text = self.backend.generate(model_id, [{"role": "user", "content": prompt}], config)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            res_data = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
            
            proposal = res_data.get("proposed_agent")
            if proposal:
                # tech_radar에 제안 기록
                if "agent_proposals" not in self.radar_data:
                    self.radar_data["agent_proposals"] = []
                self.radar_data["agent_proposals"].append({
                    "timestamp": datetime.now().isoformat(),
                    "proposal": proposal
                })
                self._save_radar()
                return [proposal]
        except Exception as e:
            logger.error(f"Agent expansion proposal failed: {e}")
            
        return []

import asyncio
import re

def trend_scout_node(state: GortexState) -> Dict[str, Any]:
    """TrendScout 노드 엔트리 포인트"""
    scout = TrendScoutAgent()
    
    interval = int(os.getenv("TREND_SCAN_INTERVAL_HOURS", "24"))
    assigned_model = state.get("assigned_model", "gemini-1.5-flash")
    
    if scout.should_scan(interval):
        file_list = list(state.get("file_cache", {}).keys())
        # 비동기 실행 (Researcher와 동일한 패턴)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 트렌드 스캔과 보안 점검 병렬 실행
                f1 = executor.submit(lambda: asyncio.run(scout.scan_trends(assigned_model)))
                f2 = executor.submit(lambda: asyncio.run(scout.check_vulnerabilities(assigned_model)))
                notifications = f1.result() + f2.result()
                
                # 도입 기회 및 에이전트 확장 제안 분석
                f3 = executor.submit(lambda: asyncio.run(scout.analyze_adoption_opportunity(file_list, assigned_model)))
                f4 = executor.submit(lambda: asyncio.run(scout.propose_new_agents(assigned_model)))
                
                notifications += f3.result()
                agent_proposals = f4.result()
                
                for p in agent_proposals:
                    notifications.append(f"🌟 [선제적 확장 제안] '{p['agent_name']}' 영입 검토 필요 ({p['strategic_value']})")
        else:
            n1 = loop.run_until_complete(scout.scan_trends(assigned_model))
            n2 = loop.run_until_complete(scout.check_vulnerabilities(assigned_model))
            n3 = loop.run_until_complete(scout.analyze_adoption_opportunity(file_list, assigned_model))
            n4 = loop.run_until_complete(scout.propose_new_agents(assigned_model))
            notifications = n1 + n2 + n3 + [f"🌟 [선제적 확장 제안] '{p['agent_name']}' 영입 검토 필요" for p in n4]
            agent_proposals = n4
            
        return {
            "messages": [("ai", "\n".join(notifications))],
            "next_node": "manager",
            "agent_proposals": agent_proposals # 매니저에게 제안 데이터 전달
        }
    
    return {
        "next_node": "manager"
    }
