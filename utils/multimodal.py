import os
import subprocess
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("GortexMultimodal")

def capture_ui_screenshot(output_path: Optional[str] = None) -> str:
    """
    현재 시스템 화면을 캡처하여 저장합니다. 
    시각적 버그 진단 및 UI 상태 확인에 사용됩니다.
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"logs/screenshots/screen_{timestamp}.png"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # macOS용 캡처 명령어 (Darwin)
        # -x: 소리 무음
        subprocess.run(["screencapture", "-x", output_path], check=True)
        logger.info(f"📸 UI Screenshot captured: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return f"Error: {str(e)}"

def capture_web_screenshot(url: str, output_path: Optional[str] = None) -> str:
    """
    특정 URL의 웹 페이지를 캡처합니다. (Playwright 필요)
    """
    import asyncio
    try:
        from playwright.async_api import async_playwright
        
        async def _capture():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                path = output_path or f"logs/screenshots/web_{datetime.now().strftime('%H%M%S')}.png"
                os.makedirs(os.path.dirname(path), exist_ok=True)
                await page.screenshot(path=path)
                await browser.close()
                return path
        
        return asyncio.run(_capture())
    except Exception as e:
        logger.error(f"Web screenshot failed: {e}")
        return f"Error: {e}"
