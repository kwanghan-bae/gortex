import json
import os
import logging
from typing import List, Dict, Any
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexVectorStore")

class LongTermMemory:
    """
    세션이 종료되어도 유지되는 의미 기반 지식 저장소 (장기 기억).
    """
    def __init__(self, store_path: str = "logs/long_term_memory.json"):
        self.store_path = store_path
        self.memory = self._load_store()
        self.auth = GortexAuth()

    def _load_store(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_store(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

    def memorize(self, text: str, metadata: Dict[str, Any] = None):
        """새로운 지식을 기억 (저장)"""
        # 실제 운영 환경에서는 임베딩을 통한 벡터 저장이 필요하나, 
        # 여기서는 기초 구조를 위해 텍스트 기반 저장 우선 구현
        self.memory.append({
            "content": text,
            "metadata": metadata or {},
            "timestamp": os.getenv("CURRENT_TIME", "2024-12-20"),
            "usage_count": 0 # 신규 필드 추가
        })
        self._save_store()
        logger.info(f"🧠 New knowledge memorized into long-term store.")

    def recall(self, query: str, limit: int = 3) -> List[str]:
        """관련 지식 소환 (검색)"""
        # 단순 키워드 기반 검색으로 우선 구현 (향후 임베딩 벡터 검색으로 고도화 예정)
        query_parts = query.lower().split()
        results = []
        for item in self.memory:
            score = sum(1 for p in query_parts if p in item["content"].lower())
            if score > 0:
                results.append((score, item))
        
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 검색된 지식의 사용량 증가
        top_results = results[:limit]
        for score, item in top_results:
            item["usage_count"] = item.get("usage_count", 0) + 1
            
        if top_results:
            self._save_store()
            
        return [r[1]["content"] for r in top_results]

if __name__ == "__main__":
    ltm = LongTermMemory()
    ltm.memorize("Gortex의 마스터 키는 보안 폴더에 저장되어 있다.", {"topic": "security"})
    print(ltm.recall("마스터 키"))
