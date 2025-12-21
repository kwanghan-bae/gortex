import logging
import asyncio
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.cache import GortexCache
from gortex.utils.vector_store import LongTermMemory

logger = logging.getLogger("GortexResearcher")

class ResearcherAgent:
    """
    Playwright를 사용하여 웹에서 정보를 수집하고 요약하는 에이전트.
    성능을 위해 불필요한 리소스(이미지 등)를 차단하고 캐시를 사용합니다.
    """
    def __init__(self):
        self.cache = GortexCache()
        self.ltm = LongTermMemory()
        self.timeout = 8000  # 8 seconds (SPEC)

# ... (중략) ...

    async def fetch_api_docs(self, library_name: str) -> str:
        """라이브러리의 최신 API 문서를 정밀하게 검색 및 추출"""
        query = f"official documentation {library_name} python api reference example"
        logger.info(f"🔍 Fetching API documentation for: {library_name}")
        
        # 1. 검색 수행
        search_results = await self.search_and_summarize(query)
        
        # 2. LLM을 통한 정밀 필터링 및 시그니처 추출
        auth = GortexAuth()
        prompt = f"""다음 검색 결과에서 라이브러리 '{library_name}'의 
        핵심 클래스, 함수 시그니처, 그리고 간단한 예제 코드를 추출하라. 
        불필요한 설명은 배제하고 개발자가 즉시 참조할 수 있는 기술 정보 위주로 요약하라.
        
        [Search Results]
        {search_results}
        """
        response = auth.generate("gemini-1.5-flash", [("user", prompt)], None)
        
        # 3. [Knowledge Integration] 실시간 문서를 장기 기억에 임시 저장
        self.ltm.memorize(
            f"Live API Docs ({library_name}): {response.text[:1000]}...",
            {"source": "LiveDocs", "library": library_name, "type": "api_reference"}
        )
        
        return response.text

    async def search_and_summarize(self, query: str) -> str:
        """검색 쿼리를 기반으로 웹 조사 수행"""
        # DuckDuckGo HTML 검색 활용
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        # 비동기 제어권 양보
        await asyncio.sleep(0)
        return await self.scrape_url(search_url)


def researcher_node(state: GortexState) -> Dict[str, Any]:
    """Researcher 노드 엔트리 포인트"""
    agent = ResearcherAgent()
    auth = GortexAuth()
    
    # 최근 API 호출 빈도에 따라 모델 선택
    call_count = state.get("api_call_count", 0)
    gemini_model = "gemini-2.5-flash-lite" if call_count > 10 else "gemini-1.5-flash"
    
    # 1. 의도 및 쿼리 추출
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    
    prompt = f"""다음 사용자 요청을 분석하여:
    1. 라이브러리나 API 문서 검색이 필요한지 판단하라. (is_docs_needed: true/false)
    2. 검색이 필요하다면 최적의 검색어(영어 권장)를 생성하라. (query: string)
    
    [User Request]
    {last_msg}
    
    결과는 반드시 JSON 형식을 따라라:
    {{ "is_docs_needed": true, "query": "..." }}
    """
    
    try:
        response = auth.generate(gemini_model, [("user", prompt)], None)
        import json
        req_info = json.loads(response.text)
        query = req_info.get("query", last_msg)
    except:
        req_info = {"is_docs_needed": False, "query": last_msg}
        query = last_msg

    # 2. 비동기 실행 (Playwright)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if req_info.get("is_docs_needed"):
                future = executor.submit(lambda: asyncio.run(agent.fetch_api_docs(query)))
            else:
                future = executor.submit(lambda: asyncio.run(agent.search_and_summarize(query)))
            research_result = future.result()
    else:
        if req_info.get("is_docs_needed"):
            research_result = loop.run_until_complete(agent.fetch_api_docs(query))
        else:
            research_result = loop.run_until_complete(agent.search_and_summarize(query))

    # 3. 결과 요약
    summary_prompt = f"""다음은 '{query}'에 대한 웹 조사 결과다. 
    사용자의 원래 요청({last_msg})에 답하기 위해 가장 중요한 핵심 정보를 요약하라.
    특히 API 문서라면 클래스/함수명과 사용법 예시를 반드시 포함하라.
    
    [Research Findings]
    {research_result}
    """
    summary_res = auth.generate("gemini-3-flash-preview", [("user", summary_prompt)], None)

    return {
        "messages": [("ai", summary_res.text)],
        "next_node": "manager"
    }