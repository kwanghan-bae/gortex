from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY_1: Optional[str] = None
    GEMINI_API_KEY_2: Optional[str] = None
    WORKING_DIR: str = "./workspace"
    LOG_LEVEL: str = "INFO"
    MAX_CODER_ITERATIONS: int = 30
    TREND_SCAN_INTERVAL_HOURS: int = 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
