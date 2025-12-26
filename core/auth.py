import os
import json
import time
import random
import logging
from typing import List, Optional, Any, Dict
from google import genai
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None
try:
    import requests
except ImportError:
    requests = None

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
        if self.error_log is None:
            self.error_log = []

class GortexAuth:
    """
    지능형 API 키 로테이션 및 실시간 건강 체크를 지원하는 인증 엔진.
    Gemini, OpenAI, Ollama(Local)를 모두 지원하는 멀티 프로바이더 라우터입니다.
    """
    _instance = None
    _CONFIG_PATH = "logs/system_config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GortexAuth, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    @classmethod
    def _reset(cls):
        cls._instance = None

    # docs/OLLAMA.md 기준 표준 모델 매핑
    OLLAMA_ROLE_MAP = {
        "manager": ["functiongemma:latest", "granite3.1-moe:3b", "llama3.2:3b"],
        "planner": ["qwen3:8b", "qwen2.5:7b", "falcon3:7b", "llama3.2:3b"],
        "coder": ["qwen2.5-coder:7b", "qwen3:8b", "codellama:7b"],
        "analyst": ["qwen3:8b", "qwen2.5:7b", "phi3:3.8b"],
        "researcher": ["falcon3:7b", "smollm2:1.7b", "phi3:3.8b"],
        "utility": ["smollm2:1.7b", "granite3.1-moe:3b", "tinyllama"],
        # Gemini 모델명 호환성 유지
        "gemini-1.5-flash": ["qwen3:8b", "qwen2.5:7b", "llama3:8b"],
        "gemini-1.5-pro": ["qwen3:8b", "qwen2.5:14b", "llama3:8b"],
    }

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
            if k and k.strip():
                self.key_pool.append(APIKeyInfo(key=k, client=genai.Client(api_key=k)))
        
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_key) if (OpenAI and self.openai_key) else None
        
        # Ollama 설정
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        
        self.model_mapping = {
            "gemini-1.5-flash": "gpt-4o-mini",
            "gemini-1.5-pro": "gpt-4o",
            "gemini-2.0-flash": "gpt-4o",
            "gemini-2.5-flash-lite": "gpt-4o-mini"
        }
        
        self.call_history: List[float] = []
        
        # --- Persistence 로직 ---
        # 1. 기본값 설정 (Gemini 키가 있으면 Gemini, 없으면 Ollama)
        self._provider = "gemini" if self.key_pool else "ollama"
        
        # 2. 저장된 설정 로드 시도
        if os.path.exists(self._CONFIG_PATH):
            try:
                # 파일이 비어있는지 확인
                if os.path.getsize(self._CONFIG_PATH) > 0:
                    with open(self._CONFIG_PATH, "r", encoding='utf-8') as f:
                        config = json.load(f)
                        saved_provider = config.get("provider")
                        if saved_provider in ["gemini", "ollama", "openai"]:
                            self._provider = saved_provider
                            logger.info(f"💾 Loaded saved provider: {self._provider.upper()}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load system config: {e}")

        self._initialized = True
        
        if not self.key_pool and self._provider == "gemini":
            logger.info("⚠️ No Gemini keys found. Switching fallback to OLLAMA.")
            self._provider = "ollama"

    def _save_config(self):
        """현재 설정을 파일에 저장"""
        try:
            os.makedirs(os.path.dirname(self._CONFIG_PATH), exist_ok=True)
            with open(self._CONFIG_PATH, "w", encoding='utf-8') as f:
                json.dump({"provider": self._provider, "last_update": datetime.now().isoformat()}, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Failed to save system config: {e}")

    def check_ollama_connection(self) -> bool:
        """Ollama 서버 연결 상태 확인"""
        if requests is None:
            return False
        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def list_ollama_models(self) -> List[str]:
        """설치된 Ollama 모델 목록 반환"""
        if requests is None:
            return []
        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if resp.status_code == 200:
                return [m['name'] for m in resp.json().get('models', [])]
        except Exception:
            pass
        return []

    def pull_ollama_model(self, model_name: str) -> bool:
        """Ollama 모델 다운로드 (Blocking)"""
        try:
            import subprocess
            print(f"⏳ Pulling {model_name}... (This may take a while)")
            subprocess.run(["ollama", "pull", model_name], check=True)
            print(f"✅ Successfully pulled {model_name}!")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False

    def pull_recommended_stack(self):
        """표준 추천 모델 스택 전체 다운로드"""
        core_models = ["functiongemma:latest", "qwen3:8b", "qwen2.5-coder:7b", "falcon3:7b"]
        for m in core_models:
            self.pull_ollama_model(m)

    def get_current_client(self) -> Optional[Any]:
        """Returns the current active client instance (Gemini, OpenAI, or None for Ollama)"""
        if self._provider == "gemini":
            key_info = self._get_available_gemini_key()
            return key_info.client if key_info else None
        elif self._provider == "openai":
            return self.openai_client
        return None

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
        
        if not self.key_pool:
             status_list.append({
                "idx": 0,
                "status": "active",
                "success": 0, "failure": 0, "cooldown": 0,
                "key_hint": "Local (Ollama)"
            })
             return status_list

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

    def set_provider(self, provider_name: str):
        """런타임에 LLM 공급자를 변경합니다."""
        normalized = provider_name.lower().strip()
        if normalized in ["gemini", "ollama", "openai"]:
            self._provider = normalized
            self._save_config()
            logger.info(f"🔄 Provider switched to: {self._provider.upper()}")
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    def generate(self, model_id: str, contents: Any, config: Optional[Any] = None) -> Any:
        self._track_call()
        current_provider = self._provider.lower()
        start_time = time.time()
        
        # 1. Gemini Strategy
        if current_provider == "gemini":
            if self.key_pool:
                for _ in range(len(self.key_pool) * 2):
                    key_info = self._get_available_gemini_key()
                    if not key_info:
                        break
                    try:
                        # contents가 이미 Part/Content 리스트인 경우 그대로 전달
                        res = key_info.client.models.generate_content(model=model_id, contents=contents, config=config)
                        self.report_key_success(key_info)
                        duration = (time.time() - start_time) * 1000
                        logger.info(f"⚡ [Latency] Gemini ({model_id}): {duration:.2f}ms")
                        return res
                    except Exception as e:
                        err = str(e)
                        self.report_key_failure(key_info, err)
                        time.sleep(random.uniform(0.5, 1.5))
                        continue
            # Fallback if keys are dead or empty
            logger.warning("⚠️ Gemini keys exhausted or missing. Falling back to Ollama.")
            return self._generate_ollama(model_id, contents, config)

        # 2. OpenAI Strategy
        elif current_provider == "openai":
            if self.openai_client:
                res = self._generate_openai(model_id, contents, config)
                duration = (time.time() - start_time) * 1000
                logger.info(f"⚡ [Latency] OpenAI ({model_id}): {duration:.2f}ms")
                return res
            else:
                logger.warning("⚠️ OpenAI client not available. Falling back to Ollama.")
                return self._generate_ollama(model_id, contents, config)

        # 3. Ollama Strategy (Default)
        else:
            res = self._generate_ollama(model_id, contents, config)
            duration = (time.time() - start_time) * 1000
            logger.info(f"⚡ [Latency] Ollama ({model_id}): {duration:.2f}ms")
            return res

    def _generate_ollama(self, model_id: str, contents: Any, config: Optional[Any]) -> Any:
        """
        Ollama API를 사용하여 응답을 생성하고 Gemini 호환 객체로 반환.
        docs/OLLAMA_PLAN.md에 정의된 전략에 따라 모델을 자동 선택합니다.
        """
        if requests is None:
            raise ImportError("requests module is required for Ollama. Please install it via 'pip install requests'")

        # --- Role-Based Model Routing Strategy ---
        # 요청된 model_id가 "manager", "coder" 등의 역할 이름일 경우 실제 모델명으로 매핑
        target_model = self.ollama_model # 기본값
        
        # 1. model_id가 역할 이름인지 확인
        candidates = self.OLLAMA_ROLE_MAP.get(model_id.lower(), [])
        
        # 2. model_id가 직접 모델명인 경우 (매핑에 없으면 그대로 사용)
        if not candidates:
            candidates = [model_id]

        # 3. 사용 가능한 모델 찾기 (Ollama Tags API 호출)
        try:
            tags_resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if tags_resp.status_code == 200:
                available_models = [m['name'] for m in tags_resp.json().get('models', [])]
                
                # 후보군 순회하며 매칭 시도
                model_found = False
                for cand in candidates:
                    # 정확한 매칭 or 태그 무시 매칭 (e.g. qwen2.5:7b -> qwen2.5)
                    matched = next((m for m in available_models if m.startswith(cand)), None)
                    if matched:
                        target_model = matched
                        logger.debug(f"🤖 Routing '{model_id}' to local model '{target_model}'")
                        model_found = True
                        break
                
                # 모델을 찾지 못한 경우 (Non-interactive only)
                if not model_found:
                    primary_candidate = candidates[0]
                    logger.warning(f"⚠️ Local model '{primary_candidate}' required for role '{model_id}' is missing.")
                    
                    # Auto-Approve check (환경변수 기반으로만 동작, input() 제거)
                    should_pull = False
                    if os.getenv("GORTEX_AUTO_APPROVE", "false").lower() == "true":
                        should_pull = True
                        logger.info(f"🤖 Auto-approving pull request for '{primary_candidate}'")
                    
                    if should_pull:
                        logger.info(f"⏳ Pulling {primary_candidate}... (Non-interactive)")
                        try:
                            import subprocess
                            subprocess.run(["ollama", "pull", primary_candidate], check=True)
                            logger.info(f"✅ Successfully pulled {primary_candidate}!")
                            target_model = primary_candidate
                        except Exception as e:
                            logger.error(f"Failed to pull model: {e}")
                            target_model = self.ollama_model
                    else:
                        logger.warning(f"Skipping pull for {primary_candidate}. Using default model '{self.ollama_model}'.")
                        target_model = self.ollama_model

        except Exception as e:
            logger.warning(f"Failed to fetch available Ollama models: {e}. Using default '{target_model}'")

        # --- Request Generation ---
        messages = []
        if hasattr(config, 'system_instruction') and config.system_instruction:
             messages.append({"role": "system", "content": str(config.system_instruction)})

        if isinstance(contents, list):
            for c in contents:
                role = "user" if (isinstance(c, tuple) and c[0] == "user") or (hasattr(c, 'role') and c.role == "user") else "assistant"
                text = c[1] if isinstance(c, tuple) else (c.parts[0].text if hasattr(c, 'parts') else str(c))
                messages.append({"role": role, "content": text})
        else:
            messages.append({"role": "user", "content": str(contents)})

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": getattr(config, 'temperature', 0.7) if config else 0.7,
                # "num_ctx": 4096 # 컨텍스트 길이 필요시 설정
            }
        }
        
        try:
            resp = requests.post(f"{self.ollama_base_url}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            
            raw_text = resp.text
            if not raw_text.strip():
                logger.error(f"Ollama returned an empty response. Status: {resp.status_code}")
                raise Exception("Empty response from Ollama")

            try:
                result_json = resp.json()
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode Ollama JSON: {raw_text[:200]}")
                raise e

            content_text = result_json.get("message", {}).get("content", "")
            
            class OllamaResponseAdapter:
                def __init__(self, text): self.text = text
            return OllamaResponseAdapter(content_text)
            
        except Exception as e:
            logger.error(f"Ollama generation failed ({target_model}): {e}")
            raise Exception(f"All LLM services exhausted (Gemini -> OpenAI -> Ollama failed: {e})")

    def _generate_openai(self, model_id: str, contents: Any, config: Optional[Any]) -> Any:
        target_model = self.model_mapping.get(model_id, "gpt-4o-mini")
        messages = []
        if hasattr(config, 'system_instruction') and config.system_instruction:
            messages.append({"role": "system", "content": str(config.system_instruction)})
            
        if isinstance(contents, list):
            for c in contents:
                role = "user" if (isinstance(c, tuple) and c[0] == "user") or (hasattr(c, 'role') and c.role == "user") else "assistant"
                text = c[1] if isinstance(c, tuple) else (c.parts[0].text if hasattr(c, 'parts') else str(c))
                messages.append({"role": role, "content": text})
        else:
            messages.append({"role": "user", "content": str(contents)})
            
        response = self.openai_client.chat.completions.create(
            model=target_model, messages=messages,
            temperature=getattr(config, 'temperature', 0.0) if config else 0.0
        )
        class OpenAIResponseAdapter:
            def __init__(self, res): self.text = res.choices[0].message.content
        return OpenAIResponseAdapter(response)
