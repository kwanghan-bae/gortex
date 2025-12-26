import json
import logging
import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Literal
import operator
from langgraph.graph.message import add_messages

logger = logging.getLogger("GortexState")

class GortexState(TypedDict, total=False):
    # Use add_messages to append messages instead of overwriting, ensuring chat history is preserved.
    messages: Annotated[List[Any], add_messages]
    
    # 2. Planner Context (작업 계획 및 진행 상황)
    plan: List[str]          # Planner가 수립한 원자적 작업 단계들
    current_step: int        # 현재 실행 중인 단계 인덱스 (0부터 시작)
    
    # 3. File System Context (파일 시스템 상태)
    working_dir: str         # 현재 작업 디렉토리 경로
    file_cache: Dict[str, Any] # {파일경로: 내용해시} - 토큰 절약을 위한 캐시
    
    # 4. Control Flow & Safety (제어 흐름 및 안전장치)
    # 다음으로 실행할 노드 지정
    next_node: Literal["manager", "planner", "coder", "researcher", "analyst", "trend_scout", "swarm", "optimizer", "summarizer", "evolution", "__end__"]
    assigned_model: str      # Manager가 할당한 모델 ID (예: gemini-1.5-pro)
    assigned_persona: str    # 현재 작업 맥락에 최적화된 에이전트 페르소나 (standard, innovation 등)
    coder_iteration: int     # Coder 무한 루프 방지용 카운터 (최대 30)
    step_count: int          # 전체 그래프 실행 단계 카운터 (무한 루프 방지용)
    
    # 5. Advanced Memory & Evolution (기억 및 진화)
    history_summary: str     # 컨텍스트 압축 요약본
    active_constraints: List[str] # Evolution Engine에서 주입된 사용자 맞춤형 제약 조건
    api_call_count: int      # 최근 API 호출 빈도 (스로틀링용)
    
    # 6. Agent Economy (게임화 및 평판)
    # {agent_name: {"points": int, "level": str, "achievements": List[str]}}
    agent_economy: Dict[str, Any] 
    # 에이전트별 가상 화폐 (고성능 모델 사용권 구매용)
    token_credits: Dict[str, float]
    # UI 및 에이전트 출력 타겟 언어 (ko, en, ja, zh 등)
    ui_language: str    
    # 7. Energy Awareness (작업 여력 관리)
    # 0~100 사이의 가상 에너지 수치
    agent_energy: int 
    # 최근 작업의 효율성 점수 (0.0~100.0)
    last_efficiency: float
    efficiency_history: List[float]
    
    # Additional fields that might be used
    pinned_messages: List[Any]
    last_event_id: Optional[str]
    last_question: Optional[str]
    current_predicted_usage: Optional[Any]
    total_tokens: int
    total_cost: float
    required_capability: Optional[str]
    question_to_user: Optional[str]
    predicted_usage: Optional[Any]
    session_cache: Dict[str, Any]


# We also need a way to manage the persistent session cache which was in main.py
class SessionManager:
    def __init__(self, cache_path: str = "logs/file_cache.json"):
        self.cache_path = cache_path
        self.all_sessions_cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load session cache: {e}")
        return {}

    def save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding='utf-8') as f:
                json.dump(self.all_sessions_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save session cache: {e}")

    def get_session(self, thread_id: str) -> Dict[str, Any]:
        return self.all_sessions_cache.get(thread_id, {})

    def update_session(self, thread_id: str, session_data: Dict[str, Any]):
        self.all_sessions_cache[thread_id] = session_data
        self.save_cache()