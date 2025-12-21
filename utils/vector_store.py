import json
import os
import logging
import math
from typing import List, Dict, Any
from gortex.core.auth import GortexAuth

logger = logging.getLogger("GortexVectorStore")

class LongTermMemory:
    """
    세션이 종료되어도 유지되는 의미 기반 지식 저장소 (장기 기억).
    텍스트 임베딩을 통한 벡터 검색을 지원합니다.
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

    def _get_embedding(self, text: str) -> List[float]:
        """Gemini API를 사용하여 텍스트 임베딩 생성"""
        try:
            # 텍스트가 너무 길면 절삭
            clean_text = text[:2000]
            # GortexAuth를 통해 현재 활성 클라이언트 획득
            client = self.auth.get_current_client()
            response = client.models.embed_content(
                model="models/embedding-001",
                contents=clean_text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.warning(f"Embedding failed: {e}. Falling back to zero-vector.")
            return [0.0] * 768 # 기본 차원

    def memorize(self, text: str, metadata: Dict[str, Any] = None):
        """새로운 지식을 벡터와 함께 기억 (저장)"""
        vector = self._get_embedding(text)
        
        self.memory.append({
            "content": text,
            "vector": vector, # 벡터 데이터 저장
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "usage_count": 0,
            "links": [] # 지식 간 상관관계 링크 필드 추가
        })
        self._save_store()
        logger.info(f"🧠 Knowledge vectorized and memorized.")

    def recall(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """의미론적 유사도(Cosine Similarity) 기반 지식 소환 (메타데이터 포함)"""
        if not self.memory:
            return []
            
        query_vector = self._get_embedding(query)
        
        scored_results = []
        for item in self.memory:
            if "vector" in item and len(item["vector"]) == len(query_vector):
                # 코사인 유사도 계산
                dot_product = sum(a * b for a, b in zip(query_vector, item["vector"]))
                norm_a = math.sqrt(sum(a * a for a in query_vector))
                norm_b = math.sqrt(sum(b * b for b in item["vector"]))
                similarity = dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
                
                scored_results.append((similarity, item))
            else:
                # 벡터가 없는 경우 키워드 매칭으로 폴백
                match_score = 0.1 if any(p in item["content"].lower() for p in query.lower().split()) else 0
                scored_results.append((match_score, item))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # 검색된 지식의 사용량 증가 및 결과 반환
        final_results = []
        top_results = scored_results[:limit]
        for score, item in top_results:
            if score > 0.3: # 임계값 적용
                if score > 0.5:
                    item["usage_count"] = item.get("usage_count", 0) + 1
                
                final_results.append({
                    "content": item["content"],
                    "metadata": item.get("metadata", {}),
                    "score": round(score, 2)
                })
            
        if final_results:
            self._save_store()
            
        return final_results

from datetime import datetime

if __name__ == "__main__":
    ltm = LongTermMemory()
    ltm.memorize("Gortex의 마스터 키는 보안 폴더에 저장되어 있다.", {"topic": "security"})
    print(ltm.recall("마스터 키"))
