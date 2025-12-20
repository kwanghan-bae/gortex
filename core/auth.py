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

class GortexAuth:
    """
    API 할당량 소진 시 다른 계정이나 서비스(OpenAI)로 폴백하는 멀티 LLM 인증 엔진.
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
            
        # Gemini 설정
        self.api_keys: List[str] = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2")
        ]
        self.api_keys = [k for k in self.api_keys if k]
        self.clients: List[genai.Client] = [genai.Client(api_key=k) for k in self.api_keys]
        self.current_index = 0
        
        # OpenAI 설정 (폴백용)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_key) if (OpenAI and self.openai_key) else None
        
        # 모델 매핑 테이블 (Gemini -> OpenAI)
        self.model_mapping = {
            "gemini-1.5-flash": "gpt-4o-mini",
            "gemini-1.5-pro": "gpt-4o",
            "gemini-2.0-flash-exp": "gpt-4o",
            "gemini-3-flash-preview": "gpt-4o-mini"
        }
        
        self.call_history: List[float] = []
        self._provider = "gemini"
        self._initialized = True

    def _track_call(self):
        now = time.time()
        self.call_history.append(now)
        self.call_history = [t for t in self.call_history if now - t < 60]
        if len(self.call_history) > 15:
            logger.warning(f"🚀 API call frequency is high: {len(self.call_history)} calls/min")

    def get_call_count(self) -> int:
        now = time.time()
        self.call_history = [t for t in self.call_history if now - t < 60]
        return len(self.call_history)

    def switch_account(self, error_message: str) -> bool:
        """다음 Gemini 계정으로 전환하거나 OpenAI로 폴백함"""
        if self.current_index < len(self.clients) - 1:
            old_idx = self.current_index
            self.current_index += 1
            wait_time = random.uniform(5.5, 12.0)
            logger.warning(f"[⚠️ QUOTA] Gemini {old_idx+1} 소진. {wait_time:.1f}초 대기 후 다음 키로 전환.")
            time.sleep(wait_time)
            return True
        elif self.openai_client:
            self._provider = "openai"
            logger.warning("🚨 모든 Gemini 키가 소진되었습니다. OpenAI로 전환합니다!")
            return True
        return False

    def _generate_openai(self, model_id: str, contents: Any, config: Optional[Any]) -> Any:
        """OpenAI를 통한 대체 생성"""
        if not self.openai_client:
            raise Exception("OpenAI 클라이언트가 설정되지 않았습니다.")
            
        target_model = self.model_mapping.get(model_id, "gpt-4o-mini")
        logger.info(f"🔄 OpenAI Fallback: {model_id} -> {target_model}")
        
        # google-genai 형식을 OpenAI 형식으로 변환 (단순화)
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
        
        # google-genai Response 객체 덕타이핑
        class OpenAIResponseAdapter:
            def __init__(self, res):
                self.text = res.choices[0].message.content
        
        return OpenAIResponseAdapter(response)

    def generate(self, model_id: str, contents: Any, config: Optional[Any] = None) -> Any:
        self._track_call()
        
        if self._provider == "openai":
            return self._generate_openai(model_id, contents, config)

        max_retries = len(self.clients) + 1
        for attempt in range(max_retries):
            try:
                client = self.clients[self.current_index]
                return client.models.generate_content(model=model_id, contents=contents, config=config)
            except Exception as e:
                error_str = str(e)
                if any(x in error_str for x in ["429", "QuotaExhausted", "ResourceExhausted"]):
                    if self.switch_account(error_str):
                        if self._provider == "openai":
                            return self._generate_openai(model_id, contents, config)
                        continue
                    break
                elif any(x in error_str for x in ["500", "503"]):
                    logger.warning(f"❗ 서버 일시 오류. 3초 후 재시도... ({attempt+1})")
                    time.sleep(3)
                    continue
                else:
                    logger.error(f"❌ 치명적 API 에러: {e}")
                    raise e
        
        raise Exception("🚫 모든 서비스(Gemini, OpenAI)의 할당량이 소진되었거나 사용 불가능합니다.")
