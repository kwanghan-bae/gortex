import logging
import os
from typing import List, Dict, Any, Tuple
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory

logger = logging.getLogger("GortexSummarizer")

class ContextSummarizer:
    """
    대화 맥락을 분석하고 핵심 정보를 압축하는 전문 요약기.
    """
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()

    def summarize(self, state: GortexState) -> str:
        """대화 이력을 분석하여 구조화된 프로젝트 상태 요약을 생성함."""
        messages = state.get("messages", [])
        active_constraints = state.get("active_constraints", [])
        
        # 모델 결정
        is_ollama = os.getenv("LLM_BACKEND", "hybrid").lower() == "ollama"
        summary_model = "gemini-2.0-flash" if not is_ollama else os.getenv("OLLAMA_MODEL", "llama3")

        prompt = """너는 숙련된 프로젝트 매니저다. 지금까지의 대화를 분석하여 
다음 에이전트가 작업을 완벽히 이어받을 수 있도록 현재 상태를 요약하라.

[요약 스키마]
1. 목표(Goal): 사용자가 최종적으로 달성하고자 하는 것
2. 진행 상황(Progress): 지금까지 완료된 단계 및 성과
3. 주요 컨텍스트(Context): 핵심 파일 경로, 함수명, 설정값
4. 당면 과제(Challenges): 현재 해결 중인 오류나 방해 요소
5. 다음 단계(Next Steps): 즉시 수행해야 할 행동 계획

답변은 오직 요약된 텍스트만 출력하라. 군더더기 없는 명확한 문장으로 작성하라."""

        if active_constraints:
            prompt += f"\n\n[필수 준수 규칙]\n" + "\n".join([f"- {c}" for c in active_constraints])

        # 메시지 정제
        formatted_msgs = [{"role": "system", "content": prompt}]
        for msg in messages:
            if isinstance(msg, (tuple, list)):
                formatted_msgs.append({"role": msg[0], "content": msg[1]})
            elif hasattr(msg, 'type') and hasattr(msg, 'content'): # BaseMessage 객체 대응
                role = "ai" if msg.type == "ai" else "user"
                formatted_msgs.append({"role": role, "content": msg.content})
            elif isinstance(msg, dict):
                formatted_msgs.append(msg)

        try:
            summary = self.backend.generate(summary_model, formatted_msgs, {"temperature": 0.0})
            return summary.strip()
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return state.get("history_summary", "요약 생성 실패")

def get_summarizer() -> ContextSummarizer:
    return ContextSummarizer()
