import json
import logging
import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass, field
import operator
from langgraph.graph.message import add_messages

logger = logging.getLogger("GortexState")

class GortexState(TypedDict, total=False):
    # Use add_messages to append messages instead of overwriting, ensuring chat history is preserved.
    messages: Annotated[List[Any], add_messages]
    
    plan: List[str]
    current_step: int
    working_dir: str
    file_cache: Dict[str, Any]
    next_node: str
    assigned_model: str
    coder_iteration: int
    history_summary: str
    active_constraints: List[str]
    agent_energy: int
    last_efficiency: float
    efficiency_history: List[float]
    agent_economy: Dict[str, Any]
    
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
