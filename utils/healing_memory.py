import json
import os
import logging
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger("GortexHealingMemory")

class SelfHealingMemory:
    """
    에러 패턴과 성공적인 해결책을 매핑하여 즉각적인 자가 수복을 지원하는 메모리 엔진.
    """
    def __init__(self, storage_path: str = "logs/healing_memory.json"):
        self.storage_path = storage_path
        self.memory = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def learn(self, error_pattern: str, solution_action: Dict[str, Any]):
        """에러와 해결책을 학습"""
        norm_error = self._normalize_error(error_pattern)
        self.memory.append({
            "error": norm_error,
            "solution": solution_action,
            "usage_count": 1
        })
        self._save()
        logger.info(f"🩹 Learned new healing patch for: {norm_error[:50]}...")

    def find_solution(self, error_msg: str) -> Optional[Dict[str, Any]]:
        """에러 메시지에 맞는 해결책 검색"""
        norm_error = self._normalize_error(error_msg)
        for item in self.memory:
            if item["error"] in norm_error or norm_error in item["error"]:
                item["usage_count"] += 1
                self._save()
                return item["solution"]
        return None

    def get_solution_hint(self, error_msg: str) -> Optional[str]:
        """에러 메시지에 대한 텍스트 힌트 반환"""
        solution = self.find_solution(error_msg)
        if solution:
            if isinstance(solution, dict) and "action" in solution:
                return f"Try this: {solution.get('target', '')} (Action: {solution['action']})"
            return str(solution)
        return None

    def _normalize_error(self, text: str) -> str:
        """에러 메시지에서 변하는 부분(경로 등)을 제거하여 일반화"""
        text = re.sub(r'\/[^\s]+', '<path>', text)
        return text.strip().lower()

if __name__ == "__main__":
    hm = SelfHealingMemory()
    hm.learn("ModuleNotFoundError: No module named 'requests'", {"action": "execute_shell", "target": "pip install requests"})
    print(hm.find_solution("Error: ModuleNotFoundError: No module named 'requests' in main.py"))