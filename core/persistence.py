import json
import logging
from typing import Any, Dict
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from gortex.utils.crypto import GortexCrypto

logger = logging.getLogger("GortexPersistence")

class SecureSqliteSaver(AsyncSqliteSaver):
    """
    상태 저장 시 민감한 데이터를 자동으로 암호화하는 보안 강화형 체크포인터.
    """
    def __init__(self, conn, **kwargs):
        super().__init__(conn, **kwargs)
        self.crypto = GortexCrypto()

    def _encrypt_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """상태 내의 민감한 정보 암호화"""
        new_state = state.copy()
        # messages나 file_cache 내의 특정 패턴 암호화 고려 가능
        # 여기서는 전체 직렬화된 JSON 내의 민감 키워드 보호 로직으로 구현 가능하나,
        # 단순화를 위해 특정 필드(history_summary 등) 암호화 예시
        if "history_summary" in new_state and new_state["history_summary"]:
            new_state["history_summary"] = self.crypto.encrypt(new_state["history_summary"])
        return new_state

    def _decrypt_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """상태 복구 시 암호화된 정보 복호화"""
        new_state = state.copy()
        if "history_summary" in new_state and isinstance(new_state["history_summary"], str):
            # 암호화된 형태인지 확인 후 복호화 (Fernet 토큰은 대략적으로 판별 가능)
            if new_state["history_summary"].startswith("gAAAA"):
                new_state["history_summary"] = self.crypto.decrypt(new_state["history_summary"])
        return new_state

    # 참고: 실제 LangGraph의 AsyncSqliteSaver 내부 메서드를 오버라이딩하여 
    # 저장/로드 시점에 암복호화를 개입시켜야 함. 
    # (여기서는 기초 구조만 제시하며, 실제 라이브러리 hook 지점에 맞춰 확장 필요)
