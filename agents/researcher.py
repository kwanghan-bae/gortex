import logging
import asyncio
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from gortex.core.auth import GortexAuth
from gortex.core.state import GortexState
from gortex.utils.cache import GortexCache

logger = logging.getLogger("GortexResearcher")

class ResearcherAgent:
    """
    Playwright를 사용하여 웹에서 정보를 수집하고 요약하는 에이전트.
    성능을 위해 불필요한 리소스(이미지 등)를 차단하고 캐시를 사용합니다.
    """
    def __init__(self):
        self.cache = GortexCache()
        self.timeout = 8000  # 8 seconds (SPEC)

    async def scrape_url(self, url: str) -> str:
        """URL의 내용을 스크랩 (이미지 등 차단 및 DOM 정리)"""
        # 1. 캐시 확인
        cached = self.cache.get("web_scrape", url)
        if cached:
            logger.info(f"Cache hit for URL: {url}")
            return cached

        logger.info(f"Scraping URL: {url}")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # 최적화: 불필요한 리소스 차단
                await page.route("**/*", lambda route: 
                    route.abort() if route.request.resource_type in ["image", "font", "stylesheet", "media"]
                    else route.continue_()
                )

                # 페이지 이동 (Timeout 적용)
                await page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                
                # HTML 획득
                content = await page.content()
                await browser.close()

                # DOM 정리 (BeautifulSoup)
                soup = BeautifulSoup(content, 'html.parser')
                
                # 불필요한 태그 제거
                for tag in soup(["script", "style", "nav", "footer", "iframe", "header"]):
                    tag.decompose()

                # 텍스트 추출 (주요 본문 영역 우선)
                main_content = soup.find(["article", "main", "div", {"id": "content"}, {"class": "content"}])
                text = main_content.get_text(separator="\n") if main_content else soup.get_text(separator="\n")
                
                # 공백 정리
                text = re.sub(r'\n+', '\n', text).strip()
                
                # 캐시 저장
                self.cache.set("web_scrape", url, text[:10000]) # 너무 길면 잘라서 저장
                
                return text[:10000]

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return f"Error: {e}"

    async def search_and_summarize(self, query: str) -> str:
        """검색 쿼리를 기반으로 웹 조사 수행"""
        search_url = f"https://duckduckgo.com/html/?q={query}"
        
        # 비동기 제어권 양보 (UI 갱신 기회 부여)
        await asyncio.sleep(0)
        return await self.scrape_url(search_url)


def researcher_node(state: GortexState) -> Dict[str, Any]:
    """Researcher 노드 엔트리 포인트 (Sync wrapper for async)"""
    agent = ResearcherAgent()
    
    # 1. 쿼리 추출
    last_msg = state["messages"][-1].content
    auth = GortexAuth()
    prompt = f"다음 사용자 요청을 보고 정보를 찾기 위한 최적의 검색어(한국어/영어)를 추출해줘: {last_msg}"
    
    response = auth.generate("gemini-1.5-flash", [("user", prompt)], None)
    query = response.text.strip()
    
    # 2. 비동기 실행을 위한 이벤트 루프 처리
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # 이미 루프가 실행 중인 경우 (예: 다른 비동기 프레임워크 내부)
        # 새로운 스레드에서 실행하거나 nest_asyncio 등을 고려해야 함.
        # 여기서는 단순화를 위해 run_until_complete 시도 (단, 에러 가능성 있음)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(lambda: asyncio.run(agent.search_and_summarize(query)))
            research_result = future.result()
    else:
        research_result = loop.run_until_complete(agent.search_and_summarize(query))

    # 3. 결과 요약
    summary_prompt = f"다음은 '{query}'에 대한 검색 결과다. 사용자의 요청({last_msg})에 맞춰 핵심 내용을 요약해줘.\n\n[검색 결과]\n{research_result}"
    summary_res = auth.generate("gemini-3-flash-preview", [("user", summary_prompt)], None)

    return {
        "messages": [("ai", summary_res.text)],
        "next_node": "manager"
    }