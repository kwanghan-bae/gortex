import re
import json
import os
from datetime import datetime

def count_tokens(text: str) -> int:
    """
    텍스트의 토큰 수를 대략적으로 추정합니다.
    (Backend Agnostic Approximation)
    """
    if not text:
        return 0
    words = len(re.findall(r'\w+', text))
    chars = len(text)
    return int((chars * 0.5) + words)

def estimate_cost(tokens: int, model: str = "flash") -> float:
    """토큰 당 예상 비용 계산 (1M 토큰 당 가격 기준, USD)"""
    model_lower = model.lower()
    if any(k in model_lower for k in ["qwen", "llama", "mistral", "gemma", "phi"]):
        return 0.0
    if "pro" in model_lower:
        return (tokens / 1_000_000) * 3.5
    elif "flash" in model_lower:
        return (tokens / 1_000_000) * 0.075
    return 0.0

class DailyTokenTracker:
    """일일 토큰 소비량을 추적하고 예산을 관리함."""
    def __init__(self, storage_path: str = "logs/token_budget.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get("date") == self.today:
                        return data
            except Exception:
                pass
        return {"date": self.today, "total_tokens": 0, "costs": 0.0}

    def _save_data(self):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def update_usage(self, tokens: int, model: str):
        now_date = datetime.now().strftime("%Y-%m-%d")
        if now_date != self.today:
            self.today = now_date
            self.data = {"date": self.today, "total_tokens": 0, "costs": 0.0}
            
        cost = estimate_cost(tokens, model)
        self.data["total_tokens"] += tokens
        self.data["costs"] += cost
        self._save_data()

    def get_daily_total(self) -> int:
        return self.data.get("total_tokens", 0)

    def get_budget_status(self, limit: int = 500000) -> float:
        """현재 토큰 한도 대비 소모율(0.0~1.0) 반환"""
        total = self.get_daily_total()
        return min(1.0, total / limit)
