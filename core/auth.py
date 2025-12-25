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
from dataclasses import dataclass
from datetime import datetime, timedelta

# 로깅 설정
logger = logging.getLogger("GortexAuth")

# .env 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

@dataclass
class APIKeyInfo:
    key: str
    client: genai.Client
    status: str = "alive" # alive, cooldown, dead
    last_failure: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    failure_count: int = 0
    success_count: int = 0
    error_log: List[str] = None

    def __post_init__(self):
        if self.error_log is None: self.error_log = []

class GortexAuth:
    """
    지능형 API 키 로테이션 및 실시간 건강 체크를 지원하는 인증 엔진.
    에러 타입에 따라 쿨다운 전략을 동적으로 조절합니다.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexAuth, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def _reset(cls):
        cls._instance = None

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
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

    def get_current_client(self) -> Any:
        """현재 활성화된(가장 최근 성공한) 클라이언트를 반환합니다."""
        # 1. 살아있는 키 중 첫 번째 사용
        key_info = self._get_available_gemini_key()
        if key_info:
            return key_info.client

        # 2. 없으면 OpenAI 클라이언트
        if self.openai_client:
            return self.openai_client

        # 3. 그것도 없으면 풀의 첫 번째 (에러 발생 가능성 있음)
        if self.key_pool:
            return self.key_pool[0].client

        raise Exception("No available LLM client found.")

    def get_pool_status(self) -> List[Dict[str, Any]]:
        """전체 키 풀의 건강 상태 요약 반환 (UI 연동용)"""
        status_list = []
        now = datetime.now()
        for idx, info in enumerate(self.key_pool):
            rem_cooldown = 0
            if info.status == "cooldown" and info.cooldown_until:
                rem_cooldown = max(0, int((info.cooldown_until - now).total_seconds()))
            
            status_list.append({
                "idx": idx + 1,
                "status": info.status,
                "success": info.success_count,
                "failure": info.failure_count,
                "cooldown": rem_cooldown,
                "key_hint": info.key[:8] + "..."
            })
        return status_list

    def _get_available_gemini_key(self) -> Optional[APIKeyInfo]:
        now = datetime.now()
        for key_info in self.key_pool:
            if key_info.status == "cooldown" and key_info.cooldown_until and now >= key_info.cooldown_until:
                logger.info(f"🔄 Cooldown expired for key {key_info.key[:8]}... Resetting.")
                key_info.status = "alive"
                key_info.failure_count = 0
        
        for key_info in self.key_pool:
            if key_info.status == "alive":
                return key_info
        return None

    def report_key_success(self, key_info: APIKeyInfo):
        key_info.success_count += 1
        key_info.failure_count = 0
        if key_info.status == "cooldown":
            key_info.status = "alive"

    def report_key_failure(self, key_info: APIKeyInfo, error_msg: str):
        key_info.failure_count += 1
        key_info.last_failure = datetime.now()
        key_info.error_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg[:100]}")
        
        is_quota = any(x in error_msg for x in ["429", "Quota", "Exhausted", "Resource"])
        is_server = any(x in error_msg for x in ["500", "503", "Overloaded", "Deadline"])
        is_auth = any(x in error_msg for x in ["401", "403", "API_KEY_INVALID"])

        if is_auth:
            key_info.status = "dead"
            logger.critical(f"💀 API Key {key_info.key[:8]}... is DEAD.")
        elif is_quota:
            wait_mins = 2 ** min(key_info.failure_count, 6)
            key_info.status = "cooldown"
            key_info.cooldown_until = datetime.now() + timedelta(minutes=wait_mins)
            logger.warning(f"⚠️ Quota Hit. {key_info.key[:8]}... cooldown for {wait_mins}m.")
        elif is_server:
            key_info.status = "cooldown"
            key_info.cooldown_until = datetime.now() + timedelta(seconds=30 * key_info.failure_count)
            logger.warning(f"❗ Server Overloaded. {key_info.key[:8]}... brief isolation.")
        else:
            if key_info.failure_count >= 3:
                key_info.status = "cooldown"
                key_info.cooldown_until = datetime.now() + timedelta(minutes=1)

    def generate(self, model_id: str, contents: Any, config: Optional[Any] = None) -> Any:
        self._track_call()
        for _ in range(len(self.key_pool) * 2):
            key_info = self._get_available_gemini_key()
            if not key_info: break
            try:
                self._provider = "gemini"
                res = key_info.client.models.generate_content(model=model_id, contents=contents, config=config)
                self.report_key_success(key_info)
                return res
            except Exception as e:
                err = str(e)
                self.report_key_failure(key_info, err)
                time.sleep(random.uniform(0.5, 1.5))
                continue

        if self.openai_client:
            self._provider = "openai"
            logger.warning("🚨 Gemini Exhausted. Using OpenAI.")
            return self._generate_openai(model_id, contents, config)
        raise Exception("🚫 All LLM services exhausted.")

    def _generate_openai(self, model_id: str, contents: Any, config: Optional[Any]) -> Any:
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
            model=target_model, messages=messages,
            temperature=getattr(config, 'temperature', 0.0) if config else 0.0
        )
        class OpenAIResponseAdapter:
            def __init__(self, res): self.text = res.choices[0].message.content
        return OpenAIResponseAdapter(response)