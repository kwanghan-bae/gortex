import gc
import logging
from gortex.core.state import GortexState
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexMemory")

def compress_synapse(state: GortexState) -> GortexState:
    """
    대화가 길어질 때 Gemini 2.5 Flash-Lite를 사용하여 맥락을 압축함.
    SPEC: 메시지 수가 12개 이상일 때 트리거.
    """
    messages = state.get("messages", [])
    if len(messages) < 12:
        return state

    logger.info("🧠 Compressing synapses (context compression)...")
    auth = GortexAuth()
    summary_model = "gemini-2.5-flash-lite"
    
    prompt = """지금까지의 모든 대화 내용을 분석하여 다음 정보를 추출해줘:
1. 현재 프로젝트의 목표
2. 이미 완료된 작업 리스트
3. 현재 직면한 문제점 및 남은 단계
4. 주요 변수 및 설정값

이 정보를 바탕으로 대화를 요약해. 이전 대화 기록을 이 요약본으로 대체할 거야."""

    try:
        response = auth.generate(summary_model, messages, None)
        summary_text = response.text
        
        # 메모리 강제 정리
        gc.collect()
        
        # 이전 메시지들을 요약본으로 대체 (첫 번째 시스템 메시지와 마지막 메시지 유지 고려 가능하나 여기선 단순 대체)
        new_message = [("system", f"이전 대화 요약: {summary_text}")]
        
        return {
            "messages": new_message,
            "history_summary": summary_text
        }
    except Exception as e:
        logger.error(f"Synaptic compression failed: {e}")
        return state

def summarizer_node(state: GortexState):
    """LangGraph node for compression"""
    return compress_synapse(state)
