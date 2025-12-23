import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("GortexEvolutionaryMemory")

class EvolutionaryMemory:
    """
    주제별 샤딩(Sharding) 기술을 적용하여 지능 데이터를 분산 관리하는 메모리 클래스.
    """
    def __init__(self, base_dir: str = "logs/memory"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.legacy_path = "experience.json"
        self.shards: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_shards()

    def _initialize_shards(self):
        """기존 지식 마이그레이션 및 샤드 로드"""
        # 1. 마이그레이션: 구버전 experience.json이 있으면 분해하여 샤딩
        if os.path.exists(self.legacy_path):
            logger.info("📦 Migrating legacy experience.json to shards...")
            try:
                with open(self.legacy_path, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                for item in legacy_data:
                    # 간단한 분류 (키워드 기반)
                    category = self._guess_category(item.get("learned_instruction", ""))
                    self.save_rule(
                        instruction=item["learned_instruction"],
                        trigger_patterns=item["trigger_patterns"],
                        category=category,
                        severity=item.get("severity", 3),
                        source_session=item.get("source_session", "legacy_migration")
                    )
                # 마이그레이션 완료 후 백업 및 원본 삭제
                os.rename(self.legacy_path, self.legacy_path + ".migrated.bak")
            except Exception as e:
                logger.error(f"Migration failed: {e}")

        # 2. 기본 샤드 로드 (초기에는 비어있을 수 있음)
        for cat in ["coding", "research", "design", "general"]:
            self.shards[cat] = self._load_shard(cat)

    def _load_shard(self, category: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.base_dir, f"{category}_shard.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _persist_shard(self, category: str):
        path = os.path.join(self.base_dir, f"{category}_shard.json")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.shards.get(category, []), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist {category} shard: {e}")

    def _guess_category(self, text: str) -> str:
        """텍스트 내용을 분석하여 적절한 샤드 카테고리 결정"""
        text = text.lower()
        if any(k in text for k in ["code", "python", "import", "class", "def", "syntax"]):
            return "coding"
        elif any(k in text for k in ["search", "trend", "latest", "find", "google"]):
            return "research"
        elif any(k in text for k in ["ui", "dashboard", "layout", "design", "color"]):
            return "design"
        return "general"

    def save_rule(self, instruction: str, trigger_patterns: List[str], category: Optional[str] = None, severity: int = 3, source_session: Optional[str] = None, context: Optional[str] = None):
        """새로운 규칙을 특정 샤드에 저장 (지능형 병합 포함)"""
        cat = category or self._guess_category(instruction + " " + " ".join(trigger_patterns))
        
        if cat not in self.shards:
            self.shards[cat] = self._load_shard(cat)
            
        shard = self.shards[cat]
        new_patterns = set(trigger_patterns)
        
        # 중복/병합 체크
        for existing in shard:
            if existing["learned_instruction"].strip() == instruction.strip():
                existing["trigger_patterns"] = list(set(existing["trigger_patterns"]).union(new_patterns))
                existing["reinforcement_count"] = existing.get("reinforcement_count", 0) + 1
                self._persist_shard(cat)
                return

        rule_id = f"RULE_{cat.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        new_rule = {
            "id": rule_id,
            "category": cat,
            "trigger_patterns": trigger_patterns,
            "learned_instruction": instruction,
            "context": context,
            "severity": severity,
            "reinforcement_count": 1,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_count": 0,
            "failure_count": 0
        }
        shard.append(new_rule)
        self._persist_shard(cat)
        logger.info(f"New rule saved to '{cat}' shard: {rule_id}")

    def get_active_constraints(self, context_text: str) -> List[str]:
        """맥락과 관련된 샤드만 로드하여 활성 제약 조건 추출"""
        target_cat = self._guess_category(context_text)
        # 검색 대상 샤드 결정 (현재 카테고리 + general)
        search_cats = {target_cat, "general"}
        
        active_rules = []
        for cat in search_cats:
            shard = self.shards.get(cat) or self._load_shard(cat)
            for rule in shard:
                if any(p.lower() in context_text.lower() for p in rule["trigger_patterns"]):
                    active_rules.append(rule["learned_instruction"])
                    rule["usage_count"] = rule.get("usage_count", 0) + 1
            # 사용 통계 업데이트를 위해 해당 샤드만 저장
            self._persist_shard(cat)
            
        return active_rules

    def record_rule_outcome(self, rule_id: str, success: bool):
        """전체 샤드를 스캔하여 특정 규칙의 성과 기록 (ID에 카테고리 힌트 포함됨)"""
        for cat, shard in self.shards.items():
            for rule in shard:
                if rule["id"] == rule_id:
                    rule["usage_count"] = rule.get("usage_count", 0) + 1
                    if success: rule["success_count"] = rule.get("success_count", 0) + 1
                    else: rule["failure_count"] = rule.get("failure_count", 0) + 1
                    self._persist_shard(cat)
                    return

    def prune_memory(self, model_id: str = "gemini-2.0-flash"):
        """샤드별로 의미론적 통합 수행하여 중복 지식 제거"""
        for cat in list(self.shards.keys()):
            shard = self.shards[cat]
            if len(shard) < 2: continue
            
            logger.info(f"✨ Pruning '{cat}' memory shard semantically...")
            rules_text = "\n".join([f"[{i}] {r['learned_instruction']} (Patterns: {r['trigger_patterns']})" for i, r in enumerate(shard)])
            
            prompt = f"""당신은 지식 최적화 전문가입니다. 다음 '{cat}' 분야의 규칙들을 분석하여:
            1. 내용이 중복되거나 매우 유사한 규칙은 하나로 통합하십시오.
            2. 더 구체적이고 실행 가능한 지침을 우선순위에 두십시오.
            
            [규칙 리스트]
            {rules_text}
            
            결과는 반드시 통합된 최종 규칙 리스트만 JSON 형식으로 반환하십시오:
            [{{ "instruction": "...", "trigger_patterns": ["...", "..."], "severity": 1~5 }}]
            """
            
            try:
                from gortex.core.llm.factory import LLMFactory
                backend = LLMFactory.get_default_backend()
                response = backend.generate(model_id, [{"role": "user", "content": prompt}])
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    new_rules_data = json.loads(json_match.group(0))
                    if isinstance(new_rules_data, list) and len(new_rules_data) > 0:
                        updated_shard = []
                        for idx, r_data in enumerate(new_rules_data):
                            updated_shard.append({
                                "id": f"RULE_{cat.upper()}_PRUNED_{datetime.now().strftime('%Y%m%d')}_{idx}",
                                "category": cat,
                                "learned_instruction": r_data["instruction"],
                                "trigger_patterns": r_data["trigger_patterns"],
                                "severity": r_data.get("severity", 3),
                                "reinforcement_count": 1,
                                "created_at": datetime.now().isoformat(),
                                "usage_count": 0,
                                "success_count": 0,
                                "failure_count": 0
                            })
                        self.shards[cat] = updated_shard
                        self._persist_shard(cat)
                        logger.info(f"✅ Shard '{cat}' optimized: {len(shard)} -> {len(updated_shard)} rules.")
            except Exception as e:
                logger.error(f"Failed to prune shard {cat}: {e}")


