import gc
import logging
import os
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory

from gortex.core.llm.summarizer import get_summarizer

logger = logging.getLogger("GortexMemory")

def compress_synapse(state: GortexState) -> GortexState:
    """
    대화가 길어질 때 LLM을 사용하여 맥락을 압축함.
    """
    messages = state.get("messages", [])
    backend_type = os.getenv("LLM_BACKEND", "hybrid").lower()
    
    # 임계값 결정: Ollama(로컬)인 경우 더 일찍 요약 시작
    threshold = 8 if backend_type == "ollama" else 15
    
    if len(messages) < threshold:
        return state

    logger.info(f"🧠 Synaptic Compression active (Threshold: {threshold})...")
    
    summarizer = get_summarizer()
    summary_text = summarizer.summarize(state)
    
    # 새로운 메시지 리스트 구성
    # 1. 시스템 요약본 주입
    new_messages = [("system", f"[PROJECT STATE SUMMARY]\n{summary_text}")]
    
    # 2. 최근 중요한 대화 맥락 보존 (최근 4개)
    if len(messages) > 4:
        new_messages.extend(messages[-4:])
    
    return {
        "messages": new_messages,
        "history_summary": summary_text
    }

def prune_synapse(state: GortexState) -> GortexState:
    """메시지가 너무 많을 경우 강제 절삭하여 토큰 한계 보호"""
    messages = state.get("messages", [])
    backend_type = os.getenv("LLM_BACKEND", "hybrid").lower()
    
    # 최대 한도: 로컬 모델은 20개, 클라우드는 50개
    limit = 20 if backend_type == "ollama" else 50
    
    if len(messages) <= limit:
        return state
        
    logger.info(f"✂️ Pruning synapse: {len(messages)} -> {limit} messages.")
    
    # 첫 번째 요약 메시지와 마지막 limit-1개 메시지 유지
    pruned = [messages[0]] + messages[-(limit-1):]
    
    return {"messages": pruned}

def summarizer_node(state: GortexState):
    """LangGraph node for compression & pruning"""
    # 1. 압축 수행
    state = compress_synapse(state)
    # 2. 강제 가지치기(Pruning) 수행
    state = prune_synapse(state)
    return state