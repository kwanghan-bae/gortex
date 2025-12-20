import os
import time
import random
import logging
from typing import List, Optional, Any
from google import genai
from dotenv import load_dotenv

# 로깅 설정
logger = logging.getLogger("GortexAuth")

# .env 로드 (프로젝트 루트 기준으로 검색)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback to default

class GortexAuth:
    """
    Gemini API 할당량 제한(Quota Limit)을 극복하기 위한 듀얼 키 로테이션 클래스.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexAuth, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.api_keys: List[str] = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2")
        ]
        self.api_keys = [k for k in self.api_keys if k]
        
        self.current_index = 0
        self.clients: List[genai.Client] = []
        self.call_history: List[float] = []
        
        for key in self.api_keys:
            self.clients.append(genai.Client(api_key=key))
        
        self._initialized = True

    @classmethod
    def _reset(cls):
        """인스턴스 초기화 (테스트용)"""
        cls._instance = None


    def _track_call(self):
        """호출 횟수 기록 및 1분 경과 기록 정리"""
        now = time.time()
        self.call_history.append(now)
        self.call_history = [t for t in self.call_history if now - t < 60]
        
        if len(self.call_history) > 10:
            logger.warning(f"🚀 API call frequency is high: {len(self.call_history)} calls/min")

    def get_call_count(self) -> int:
        """최근 1분간의 API 호출 횟수 반환"""
        now = time.time()
        self.call_history = [t for t in self.call_history if now - t < 60]
        return len(self.call_history)

    def get_client(self) -> genai.Client:


        """현재 활성화된 계정의 클라이언트 반환"""
        if not self.clients:
            raise ValueError("사용 가능한 Gemini API 클라이언트가 없습니다.")
        return self.clients[self.current_index]

    def switch_account(self, error_message: str):
        """429(Resource Exhausted) 에러 발생 시 계정을 전환하고 지터를 수행"""
        old_idx = self.current_index
        self.current_index = (self.current_index + 1) % len(self.clients)
        
        # 구글의 탐지를 피하기 위한 지능적 대기 (Anti-bot Jitter)
        # 5.5초 ~ 12.0초 사이의 랜덤 대기 시간
        wait_time = random.uniform(5.5, 12.0)
        
        logger.warning(f"\n[⚠️ QUOTA EXHAUSTED] Account {old_idx + 1} 한도 초과: {error_message}")
        logger.info(f"🔄 Switching to Account {self.current_index + 1}...")
        logger.info(f"⏳ Anti-bot Jitter: {wait_time:.1f}초 동안 대기합니다...")
        
        time.sleep(wait_time)

    def generate(self, model_id: str, contents: Any, config: Optional[Any] = None) -> Any:
        """안정적인 API 호출을 위한 재시도 및 로테이션 래퍼"""
        if not self.clients:
             raise ValueError("API 클라이언트가 초기화되지 않았습니다. .env를 확인하세요.")

        self._track_call()
        max_retries = len(self.clients) * 2

        
        for attempt in range(max_retries):
            try:
                client = self.get_client()
                # google-genai 라이브러리의 generate_content 호출
                return client.models.generate_content(
                    model=model_id,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                error_str = str(e)
                # 429 Resource Exhausted 체크
                if "429" in error_str or "QuotaExhausted" in error_str or "ResourceExhausted" in error_str:
                    self.switch_account(error_str)
                    continue
                # 5xx 서버 에러 체크
                elif "500" in error_str or "503" in error_str:
                    logger.warning(f"❗ 서버 일시 오류 (5xx). 3초 후 재시도... ({attempt+1}/{max_retries})")
                    time.sleep(3)
                    continue
                else:
                    logger.error(f"❌ 치명적 API 에러: {e}")
                    raise e
        
        raise Exception("🚫 모든 API 계정의 할당량이 소진되었습니다.")
