import logging
import asyncio
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from gortex.core.llm.factory import LLMFactory
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

    async def scrape_url(self, url: str) -> str:
        """Playwright를 사용하여 URL의 텍스트 콘텐츠를 추출 (이미지 제외)"""
        logger.info(f"🌐 Scraping: {url}")
        
        # 캐시 확인
        cached = self.cache.get(url)
        if cached:
            logger.info("♻️  Using cached research data.")
            return cached

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # 성능을 위해 이미지 및 CSS 차단 시도
                context = await browser.new_context(user_agent="Mozilla/5.0")
                page = await context.new_page()
                
                # 리소스 차단 로직
                async def block_aggressively(route):
                    if route.request.resource_type in ["image", "media", "font"]:
                        await route.abort()
                    else:
                        await route.continue_()
                await page.route("**/*", block_aggressively)

                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                content = await page.content()
                await browser.close()

                # HTML 정제 (BeautifulSoup)
                soup = BeautifulSoup(content, 'html.parser')
                # 광고, 스크립트 등 제거
                for s in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    s.decompose()
                
                text = soup.get_text(separator=' ', strip=True)
                # 다중 공백 제거
                text = re.sub(r'\s+', ' ', text)
                
                # 결과 캐싱
                self.cache.set(url, text[:10000]) # 상위 1만자만 저장
                return text[:5000] # 분석용으로 5천자 반환
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return f"Error: {e}"

    async def fetch_api_docs(self, library_name: str) -> str:
        """라이브러리의 최신 API 문서를 정밀하게 검색 및 추출"""
        query = f"official documentation {library_name} python api reference example"
        logger.info(f"🔍 Fetching API documentation for: {library_name}")
        
        # 1. 검색 수행
        search_results = await self.search_and_summarize(query)
        
        # 2. LLM을 통한 정밀 필터링 및 시그니처 추출 (LLMFactory 적용)
        from gortex.core.llm.factory import LLMFactory
        backend = LLMFactory.get_default_backend()
        prompt = f"""다음 검색 결과에서 라이브러리 '{library_name}'의 
        핵심 클래스, 함수 시그니처, 그리고 간단한 예제 코드를 추출하라. 
        불필요한 설명은 배제하고 개발자가 즉시 참조할 수 있는 기술 정보 위주로 요약하라.
        
        [Search Results]
        {search_results}
        """
        response_text = backend.generate("gemini-1.5-flash", [{"role": "user", "content": prompt}])
        
        # 3. [Knowledge Integration] 실시간 문서를 장기 기억에 임시 저장
        self.ltm.memorize(
            f"Live API Docs ({library_name}): {response_text[:1000]}...",
            {"source": "LiveDocs", "library": library_name, "type": "api_reference"}
        )
        
        return response_text

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
    from gortex.core.llm.factory import LLMFactory
    backend = LLMFactory.get_default_backend()
    from gortex.utils.prompt_loader import loader
    
    # 1. 의도 및 쿼리 추출 (외부 템플릿 사용)
    last_msg_obj = state["messages"][-1]
    last_msg = last_msg_obj[1] if isinstance(last_msg_obj, tuple) else last_msg_obj.content
    
    # 지침 로드
    base_instruction = loader.get_prompt("researcher")
    intent_prompt = f"{base_instruction}\n\n사용자 요청: {last_msg}\n\n위 요청을 분석하여 검색 필요 여부와 쿼리를 JSON으로 반환하라."
    
    assigned_model = state.get("assigned_model", "gemini-1.5-flash")
    config = {"temperature": 0.0}
    if backend.supports_structured_output():
        from google.genai import types
        config = types.GenerateContentConfig(response_mime_type="application/json")

    try:
        response_text = backend.generate(assigned_model, [{"role": "user", "content": intent_prompt}], config)
        import json
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        req_info = json.loads(json_match.group(0)) if json_match else json.loads(response_text)
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
    summary_instruction = loader.get_prompt("researcher_summary")
    summary_prompt = f"{summary_instruction}\n\n사용자 요청: {last_msg}\n검색 결과: {research_result}"
    
    summary_text = backend.generate(assigned_model, [{"role": "user", "content": summary_prompt}])

    return {
        "messages": [("ai", summary_text)],
        "next_node": "manager"
    }