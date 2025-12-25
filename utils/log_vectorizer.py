import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("GortexLogVectorizer")

class SemanticLogSearch:
    """
    trace.jsonl 로그 데이터를 분석하고 검색하여 과거 해결 사례를 찾아주는 엔진.
    """
    def __init__(self, log_path: str = "logs/trace.jsonl"):
        self.log_path = log_path
        self.index = []

    def load_and_index(self):
        """로그 파일을 읽어 검색 가능한 인덱스 생성"""
        if not os.path.exists(self.log_path):
            return
        
        try:
            with open(self.log_path, "r", encoding='utf-8') as f:
                lines = f.readlines()
                
            new_index = []
            for line in lines:
                try:
                    entry = json.loads(line)
                    # 중요한 이벤트만 인덱싱 (error, node_complete 등)
                    if entry.get("event") in ["error", "node_complete", "tool_call"]:
                        # 검색용 텍스트 생성
                        search_text = f"{entry.get('agent')} {entry.get('event')} {json.dumps(entry.get('payload'))}"
                        new_index.append({
                            "timestamp": entry.get("timestamp"),
                            "text": search_text,
                            "entry": entry
                        })
                except Exception:
                    continue
            self.index = new_index
            logger.info(f"✅ Indexed {len(self.index)} log entries for semantic search.")
        except Exception as e:
            logger.error(f"Failed to index logs: {e}")

    def search_similar_cases(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """쿼리와 유사한 과거 사례 검색 (단순 키워드 매칭 기반 우선 구현)"""
        if not self.index:
            self.load_and_index()
            
        results = []
        query_parts = query.lower().split()
        
        for item in self.index:
            score = sum(1 for part in query_parts if part in item["text"].lower())
            if score > 0:
                results.append((score, item))
        
        # 스코어 순 정렬
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1]["entry"] for r in results[:limit]]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    searcher = SemanticLogSearch()
    searcher.load_and_index()
    print(f"Sample Search Results: {searcher.search_similar_cases('error python')}")
