from typing import Annotated, Sequence, TypedDict, List, Dict, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GortexState(TypedDict):
    """
    Gortex 시스템의 전역 상태(Global State).
    LangGraph의 StateGraph에서 노드 간 데이터 전달에 사용됩니다.
    """
    # 1. Chat History (LangGraph가 자동으로 메시지를 병합/누적함)
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # 2. Planner Context (작업 계획 및 진행 상황)
    plan: List[str]          # Planner가 수립한 원자적 작업 단계들
    current_step: int        # 현재 실행 중인 단계 인덱스 (0부터 시작)
    
    # 3. File System Context (파일 시스템 상태)
    working_dir: str         # 현재 작업 디렉토리 경로
    file_cache: Dict[str, str] # {파일경로: 내용해시} - 토큰 절약을 위한 캐시
    
    # 4. Control Flow & Safety (제어 흐름 및 안전장치)
    # 다음으로 실행할 노드 지정
    next_node: Literal["manager", "planner", "coder", "researcher", "analyst", "trend_scout", "__end__"]
    coder_iteration: int     # Coder 무한 루프 방지용 카운터 (최대 30)
    
    # 5. Advanced Memory & Evolution (기억 및 진화)
    history_summary: str     # 컨텍스트 압축 요약본
    active_constraints: List[str] # Evolution Engine에서 주입된 사용자 맞춤형 제약 조건
    api_call_count: int      # 최근 API 호출 빈도 (스로틀링용)

