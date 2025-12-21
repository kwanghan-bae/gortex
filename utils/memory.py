import gc
import logging
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexMemory")

def compress_synapse(state: GortexState) -> GortexState:
    """
    대화가 길어질 때 Gemini 2.5 Flash-Lite를 사용하여 맥락을 압축함.
    지능형 작업 상태(Task State) 보존 로직 추가.
    """
    messages = state.get("messages", [])
    # 메시지 개수가 12개 미만이고, 전체 요약이 이미 있다면 스킵 (단, 토큰이 많으면 압축 필요)
    if len(messages) < 12 and not state.get("history_summary"):
        return state

    logger.info("🧠 Synaptic Compression active: Structuring project state...")
    auth = GortexAuth()
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
- 군더더기 없는 명확한 명령조로 작성하라."""

    # active_constraints가 있다면 프롬프트에 추가 주입
    if state.get("active_constraints"):
        constraints = "\n".join([f"- {c}" for c in state["active_constraints"]])
        prompt += f"\n\n[Active System Constraints (MUST PERSIST)]\n{constraints}"

    try:
        # 요약 생성 시 온도를 낮게 설정하여 정확도 확보
        from google.genai import types
        config = types.GenerateContentConfig(temperature=0.0)
        
        response = auth.generate(summary_model, messages, config)
        summary_text = response.text
        
        gc.collect()
        
        # 첫 번째 메시지는 시스템의 정체성을 담은 요약으로 대체
        new_messages = [("system", f"[SYNAPTIC SUMMARY - PROJECT STATE]\n{summary_text}")]
        
        # 최근 메시지 3개는 컨텍스트 유지를 위해 보존 (사용자 마지막 입력 등)
        if len(messages) > 3:
            new_messages.extend(messages[-3:])
        
        return {
            "messages": new_messages,
            "history_summary": summary_text
        }
    except Exception as e:
        logger.error(f"Synaptic compression failed: {e}")
        return state
    except Exception as e:
        logger.error(f"Synaptic compression failed: {e}")
        return state

def summarizer_node(state: GortexState):
    """LangGraph node for compression"""
    return compress_synapse(state)
