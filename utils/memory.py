import gc
import logging
import os
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory

logger = logging.getLogger("GortexMemory")

def compress_synapse(state: GortexState) -> GortexState:
    """
    대화가 길어질 때 LLM을 사용하여 맥락을 압축함.
    지능형 작업 상태(Task State) 보존 로직 포함.
    """
    messages = state.get("messages", [])
    # 메시지 개수가 12개 미만이고, 전체 요약이 이미 있다면 스킵
    if len(messages) < 12 and not state.get("history_summary"):
        return state

    logger.info("🧠 Synaptic Compression active: Structuring project state...")
    
    # LLM 백엔드 획득
    backend = LLMFactory.get_default_backend()
    
    # 모델명 결정 (환경변수 우선, 없으면 기본값)
        # Gemini: gemini-2.5-flash-lite, Ollama: qwen2.5-coder:7b (예시)
        
        # LLM_BACKEND가 ollama면 OLLAMA_DEFAULT_MODEL 사용
    
    if os.getenv("LLM_BACKEND", "gemini").lower() == "ollama":
        summary_model = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen2.5-coder:7b")
    else:
        summary_model = "gemini-2.5-flash-lite"

    prompt = """지금까지의 모든 대화 내용을 정밀 분석하여 다음 [Project State Schema]에 맞춰 현재 상황을 '구조화된 텍스트'로 요약하라. 
이 요약은 다음 에이전트가 너의 정체성과 작업 상태를 완벽히 계승하는 데 사용된다.

[Project State Schema]
1. IDENTITY: 시스템의 정체성 및 절대 준수해야 할 핵심 규칙 (active_constraints 참조)
2. GOAL: 현재 사용자가 요청한 최종 목표
3. PROGRESS: 이미 완료된 작업 목록 (체크리스트 형태)
4. CHALLENGES: 현재 직면한 문제 또는 해결해야 할 오류
5. NEXT_STEPS: 다음에 즉시 실행해야 할 행동 계획
6. CONTEXT_VARS: 중요 파일 경로, 변수명, API 정보 등

[Constraint]
- 가장 중요한 규칙과 정체성은 요약본 최상단에 배치하라.
- 군더더기 없는 명확한 명령조로 작성하라.
- 답변은 오직 요약 텍스트만 출력하라."""

    # active_constraints가 있다면 프롬프트에 추가 주입
    if state.get("active_constraints"):
        constraints = "\n".join([f"- {c}" for c in state["active_constraints"]])
        prompt += f"\n\n[Active System Constraints (MUST PERSIST)]\n{constraints}"
        
    # 시스템 프롬프트를 메시지 구조에 반영
    # LLMBackend.generate는 List[Dict]를 받음
    # messages 리스트 앞에 시스템 프롬프트를 추가하거나, generate 내부에서 처리하도록 유도
    # 여기서는 messages 리스트를 복사하여 맨 앞에 system 메시지로 추가
    
    context_messages = [{"role": "system", "content": prompt}]
    
    # 기존 messages 변환 (Tuple -> Dict)
    # state["messages"]는 보통 [(role, content), ...] 튜플 리스트임
    for msg in messages:
        if isinstance(msg, tuple) or isinstance(msg, list):
            context_messages.append({"role": msg[0], "content": msg[1]})
        elif isinstance(msg, dict):
            context_messages.append(msg)

    try:
        # 설정 딕셔너리 사용 (types.GenerateContentConfig 제거)
        config = {"temperature": 0.0}
        
        summary_text = backend.generate(summary_model, context_messages, config)
        
        gc.collect()
        
        # 첫 번째 메시지는 시스템의 정체성을 담은 요약으로 대체
        new_messages = [("system", f"[SYNAPTIC SUMMARY - PROJECT STATE]\n{summary_text}")]
        
        # 최근 메시지 3개는 컨텍스트 유지를 위해 보존
        if len(messages) > 3:
            new_messages.extend(messages[-3:])
        
        return {
            "messages": new_messages,
            "history_summary": summary_text
        }
    except Exception as e:
        logger.error(f"Synaptic compression failed: {e}")
        return state

def prune_synapse(state: GortexState, limit: int = 50) -> GortexState:
    """메시지가 임계값을 넘을 경우 중간 메시지를 삭제하여 토큰 및 메모리 최적화"""
    messages = state.get("messages", [])
    pinned = state.get("pinned_messages", [])
    
    if len(messages) <= limit:
        return state
        
    logger.info(f"✂️ Pruning synapse: {len(messages)} -> {limit} messages. (Pinned: {len(pinned)})")
    
    # 1. 고정된 메시지(Pinned)를 최상단에 배치
    pruned = list(pinned)
    
    # 2. 요약본이 포함된 첫 번째 시스템 메시지 보존
    if messages[0] not in pruned:
        pruned.append(messages[0])
    
    # 3. 중간 메시지 절삭 후 최근 메시지들로 채움
    remaining_slots = limit - len(pruned)
    if remaining_slots > 0:
        pruned.extend(messages[-remaining_slots:])
    
    return {"messages": pruned}

def summarizer_node(state: GortexState):
    """LangGraph node for compression & pruning"""
    # 1. 압축 수행
    state = compress_synapse(state)
    # 2. 강제 가지치기(Pruning) 수행
    state = prune_synapse(state)
    return state