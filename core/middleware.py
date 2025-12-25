
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("GortexMiddleware")

class HealingMiddleware:
    """에이전트 실행 실패를 감지하고 자율 치유(Healing) 로직으로 라우팅하는 미들웨어"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def process_request(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """요청 전처리 (Optional: 입력값 검증 등)"""
        return state

    def process_response(self, output: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """실행 결과 후처리 및 에러 감지/복구 라우팅"""
        
        # 1. 실패 감지
        if output.get("status") == "failed":
            error_msg = output.get("error", "Unknown Error")
            retry_count = state.get("retry_count", 0)
            
            # 2. 재시도 한도 체크
            if retry_count < self.max_retries:
                logger.warning(f"⚠️ Failure detected: {error_msg}. Initiating Healing Loop (Attempt {retry_count + 1}/{self.max_retries})")
                
                # 3. 상태 업데이트: Healer 노드로 라우팅 변경
                state["retry_count"] = retry_count + 1
                state["next_node"] = "healer"
                state["error_context"] = {
                    "last_error": error_msg,
                    "failed_node": output.get("source", "unknown")
                }
                
                # (선택) Output에 healing 플래그 주입
                output["healing_triggered"] = True
            else:
                logger.error(f"❌ Max retries ({self.max_retries}) exceeded. Giving up on error: {error_msg}")
                # 재시도 포기 -> 에러 전파 (또는 human_review 라우팅)
                state["next_node"] = "__end__" 
        
        return output
