import logging
import os
from typing import List, Any
from gortex.core.state import GortexState

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

class ContextPruner:
    """메시지의 가치와 관련성을 분석하여 선별적으로 가지치기를 수행함."""
    def __init__(self, state: GortexState):
        self.state = state
        self.messages = list(state.get("messages", []))
        self.pinned = state.get("pinned_messages", [])
        self.plan = state.get("plan", [])

    def get_semantic_scores(self, target_messages: List[Any]) -> List[float]:
        """AnalystAgent를 통해 시맨틱 관련성 점수 획득"""
        from gortex.agents.analyst.base import AnalystAgent
        analyst = AnalystAgent()
        
        # 메시지 텍스트 리스트 구성
        formatted_msgs = []
        for m in target_messages:
            content = str(m[1] if isinstance(m, tuple) else m.content if hasattr(m, 'content') else str(m))
            formatted_msgs.append({"role": m[0] if isinstance(m, tuple) else "ai", "content": content})
            
        return analyst.rank_context_relevance(formatted_msgs, self.plan)

    def prune(self, target_count: int = 15) -> List[Any]:
        """시맨틱 관련성이 낮은 메시지를 우선적으로 제거"""
        if len(self.messages) <= target_count:
            return self.messages
            
        logger.info(f"✂️ Semantic Pruning: {len(self.messages)} -> {target_count} messages.")
        
        # 무조건 보존 대상: 첫 번째 메시지, 최신 4개 메시지
        
        # 평가 대상 인덱스 추출
        eval_indices = [i for i in range(1, len(self.messages)-4)]
        eval_messages = [self.messages[i] for i in eval_indices]
        
        # 시맨틱 점수 획득
        scores = self.get_semantic_scores(eval_messages)
        
        eval_list = []
        for idx, i_orig in enumerate(eval_indices):
            # 시맨틱 점수 + 최신성 보너스
            final_score = scores[idx] + (i_orig / len(self.messages) * 0.2)
            eval_list.append({"index": i_orig, "score": final_score})
            
        # 점수 낮은 순 정렬 후 삭제 대상 선정
        eval_list.sort(key=lambda x: x["score"])
        
        remove_count = len(self.messages) - target_count
        to_remove_indices = {e["index"] for e in eval_list[:remove_count]}
        
        new_messages = [m for i, m in enumerate(self.messages) if i not in to_remove_indices]
        return new_messages


def prune_synapse(state: GortexState) -> GortexState:
    """지능형 가지치기 수행"""
    pruner = ContextPruner(state)
    backend_type = os.getenv("LLM_BACKEND", "hybrid").lower()
    limit = 15 if backend_type == "ollama" else 30
    
    new_messages = pruner.prune(target_count=limit)
    return {"messages": new_messages}


def summarizer_node(state: GortexState):
    """LangGraph node for compression & pruning"""
    # 1. 압축 수행
    state = compress_synapse(state)
    # 2. 강제 가지치기(Pruning) 수행
    state = prune_synapse(state)
    return state