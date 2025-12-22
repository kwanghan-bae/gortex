import os
import time
import random
import logging
from typing import List, Optional, Any, Dict
from google import genai
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from dotenv import load_dotenv

# 로깅 설정
logger = logging.getLogger("GortexAuth")

# .env 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class APIKeyInfo:
    key: str
    client: genai.Client
    status: str = "alive" # alive, cooldown, exhausted
    last_failure: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    failure_count: int = 0

class GortexAuth:
    """
    API 할당량 소진 시 다른 계정이나 서비스(OpenAI)로 폴백하는 멀티 LLM 인증 엔진.
    지능형 키 로테이션 및 쿨다운(Cooldown) 시스템 탑재.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexAuth, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def _reset(cls):
        """인스턴스 초기화 (테스트용)"""
        cls._instance = None

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Gemini 키 풀 초기화
        raw_keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4")
        ]
        self.key_pool: List[APIKeyInfo] = []
        for k in raw_keys:
            if k:
                self.key_pool.append(APIKeyInfo(key=k, client=genai.Client(api_key=k)))
        
        self.current_key_idx = 0
        
        # OpenAI 설정 (최종 폴백용)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_key) if (OpenAI and self.openai_key) else None
        
        self.model_mapping = {
            "gemini-1.5-flash": "gpt-4o-mini",
            "gemini-1.5-pro": "gpt-4o",
            "gemini-2.0-flash": "gpt-4o",
            "gemini-2.5-flash-lite": "gpt-4o-mini"
        }
        
        self.call_history: List[float] = []
        self._provider = "gemini"
        self._initialized = True

    def _track_call(self):
        now = time.time()
        self.call_history.append(now)
        self.call_history = [t for t in self.call_history if now - t < 60]

    def get_call_count(self) -> int:
        now = time.time()
        self.call_history = [t for t in self.call_history if now - t < 60]
        return len(self.call_history)

    def get_provider(self) -> str:
        return self._provider.upper()

    def _get_available_gemini_key(self) -> Optional[APIKeyInfo]:
        """현재 사용 가능한(Alive 또는 Cooldown 종료된) 키를 찾음"""
        now = datetime.now()
        
        # 1. 만료된 Cooldown 먼저 해제
        for key_info in self.key_pool:
            if key_info.status == "cooldown" and key_info.cooldown_until and now >= key_info.cooldown_until:
                logger.info(f"🔄 Key Cooldown expired for a key. Resetting to alive.")
                key_info.status = "alive"
                key_info.failure_count = 0
        
        # 2. 첫 번째 Alive 상태인 키 반환
        for key_info in self.key_pool:
            if key_info.status == "alive":
                return key_info
                
        return None

    def report_key_failure(self, key_info: APIKeyInfo, is_quota_error: bool):
        """키 실패 보고 및 쿨다운 설정"""
        key_info.last_failure = datetime.now()
        key_info.failure_count += 1
        
        if is_quota_error:
            # 할당량 초과는 긴 쿨다운 (최소 10분)
            cooldown_mins = 10 * key_info.failure_count
            key_info.status = "cooldown"
            key_info.cooldown_until = datetime.now() + timedelta(minutes=cooldown_mins)
            logger.warning(f"⚠️ Key Quota Exhausted. Cooldown for {cooldown_mins} mins.")
        else:
            # 단순 서버 오류 등은 짧은 대기 후 재시도 가능하도록 alive 유지하되 카운트만 증가
            if key_info.failure_count >= 3:
                key_info.status = "cooldown"
                key_info.cooldown_until = datetime.now() + timedelta(minutes=2)
                logger.warning(f"⚠️ Key repeated failures. 2 mins cooldown.")

    def generate(self, model_id: str, contents: Any, config: Optional[Any] = None) -> Any:
        self._track_call()
        
        # 1. Gemini 시도
        for _ in range(len(self.key_pool) * 2): # 모든 키를 최소 두 번은 돌아봄
            key_info = self._get_available_gemini_key()
            if not key_info:
                break
                
            try:
                self._provider = "gemini"
                return key_info.client.models.generate_content(model=model_id, contents=contents, config=config)
            except Exception as e:
                err = str(e)
                is_quota = any(x in err for x in ["429", "Quota", "Exhausted", "Resource"])
                is_server = any(x in err for x in ["500", "503", "Overloaded"])
                
                self.report_key_failure(key_info, is_quota)
                
                if is_server:
                    logger.warning(f"❗ Gemini server busy. Retrying with next key...")
                    time.sleep(2)
                    continue
                elif is_quota:
                    # 지터 대기 후 다음 키
                    time.sleep(random.uniform(1.0, 3.0))
                    continue
                else:
                    logger.error(f"❌ Gemini Critical Error: {e}")
                    raise e

        # 2. OpenAI 폴백
        if self.openai_client:
            self._provider = "openai"
            logger.warning("🚨 No Gemini keys available. Switching to OpenAI fallback.")
            return self._generate_openai(model_id, contents, config)
            
        raise Exception("🚫 모든 LLM 서비스 사용 불가능 (Gemini/OpenAI 소진)")

    def _generate_openai(self, model_id: str, contents: Any, config: Optional[Any]) -> Any:
        # (기존 OpenAI 변환 로직 유지)
        target_model = self.model_mapping.get(model_id, "gpt-4o-mini")
        messages = []
        if isinstance(contents, list):
            for c in contents:
                role = "user" if (isinstance(c, tuple) and c[0] == "user") or (hasattr(c, 'role') and c.role == "user") else "assistant"
                text = c[1] if isinstance(c, tuple) else (c.parts[0].text if hasattr(c, 'parts') else str(c))
                messages.append({"role": role, "content": text})
        else:
            messages.append({"role": "user", "content": str(contents)})

        if config and hasattr(config, 'system_instruction'):
            messages.insert(0, {"role": "system", "content": str(config.system_instruction)})

        response = self.openai_client.chat.completions.create(
            model=target_model,
            messages=messages,
            temperature=getattr(config, 'temperature', 0.0) if config else 0.0
        )
        
        class OpenAIResponseAdapter:
            def __init__(self, res):
                self.text = res.choices[0].message.content
        return OpenAIResponseAdapter(response)

