from typing import Annotated, Sequence, TypedDict, List, Dict, Literal, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GortexState(TypedDict):
    """
    Gortex 시스템의 전역 상태(Global State).
    LangGraph의 StateGraph에서 노드 간 데이터 전달에 사용됩니다.
    """
    # 1. Chat History (LangGraph가 자동으로 메시지를 병합/누적함)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # 영구 고정된 핵심 컨텍스트 메시지 리스트
    pinned_messages: List[BaseMessage]
    
    # 2. Planner Context (작업 계획 및 진행 상황)
    plan: List[str]          # Planner가 수립한 원자적 작업 단계들
    current_step: int        # 현재 실행 중인 단계 인덱스 (0부터 시작)
    
    # 3. File System Context (파일 시스템 상태)
    working_dir: str         # 현재 작업 디렉토리 경로
    file_cache: Dict[str, str] # {파일경로: 내용해시} - 토큰 절약을 위한 캐시
    
    # 4. Control Flow & Safety (제어 흐름 및 안전장치)
    # 다음으로 실행할 노드 지정
    next_node: Literal["manager", "planner", "coder", "researcher", "analyst", "trend_scout", "swarm", "optimizer", "summarizer", "evolution", "__end__"]
    assigned_model: str      # Manager가 할당한 모델 ID (예: gemini-1.5-pro)
    assigned_persona: str    # 현재 작업 맥락에 최적화된 에이전트 페르소나 (standard, innovation 등)
    coder_iteration: int     # Coder 무한 루프 방지용 카운터 (최대 30)
    
    # 5. Advanced Memory & Evolution (기억 및 진화)
    history_summary: str     # 컨텍스트 압축 요약본
    active_constraints: List[str] # Evolution Engine에서 주입된 사용자 맞춤형 제약 조건
    api_call_count: int      # 최근 API 호출 빈도 (스로틀링용)
    
    # 6. Agent Economy (게임화 및 평판)
    # {agent_name: {"points": int, "level": str, "achievements": List[str]}}
    agent_economy: Dict[str, Dict[str, Any]] 
    # 에이전트별 가상 화폐 (고성능 모델 사용권 구매용)
    token_credits: Dict[str, float]
    # UI 및 에이전트 출력 타겟 언어 (ko, en, ja, zh 등)
    ui_language: str    
    # 7. Energy Awareness (작업 여력 관리)
    # 0~100 사이의 가상 에너지 수치
    agent_energy: int 
    # 최근 작업의 효율성 점수 (0.0~100.0)
    last_efficiency: float
    # 최근 효율성 점수 이력 (최대 10개 유지)
    efficiency_history: List[float]
    # 에이전트 간 토론 시나리오 데이터 (Consensus용)
    debate_context: List[Dict[str, Any]]
    # 합의 결과 및 사후 성과 데이터 이력
    consensus_history: List[Dict[str, Any]]

