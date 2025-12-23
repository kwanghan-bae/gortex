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
        os.makedirs(os.path.join(self.base_dir, "snapshots"), exist_ok=True)
        self.legacy_path = "experience.json"
        self.shards: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_shards()

    def detect_global_conflicts(self) -> List[Dict[str, Any]]:
        """전체 샤드를 스캔하여 트리거 중복 및 지침 모순을 감지하고 토론 의제를 설정함."""
        conflicts = []
        all_rules = []
        for cat, rules in self.shards.items():
            all_rules.extend(rules)
            
        for i, rule_a in enumerate(all_rules):
            patterns_a = set(rule_a["trigger_patterns"])
            for j, rule_b in enumerate(all_rules[i+1:]):
                if rule_a["id"] == rule_b["id"]: continue
                
                patterns_b = set(rule_b["trigger_patterns"])
                intersection = patterns_a.intersection(patterns_b)
                
                # 1. 트리거 패턴 중첩 (50% 이상) 또는 핵심 키워드 일치 시 갈등 후보
                if len(intersection) / max(len(patterns_a), len(patterns_b)) >= 0.5:
                    conflicts.append({
                        "type": "semantic_conflict",
                        "agenda": f"Conflict between {rule_a['category']} and {rule_b['category']} rules",
                        "rule_a": rule_a,
                        "rule_b": rule_b,
                        "overlap": list(intersection),
                        "severity": max(rule_a.get("severity", 3), rule_b.get("severity", 3))
                    })
        return conflicts

    def _initialize_shards(self):
        """기존 지식 마이그레이션 및 샤드 로드"""
        if os.path.exists(self.legacy_path):
            logger.info("📦 Migrating legacy experience.json to shards...")
            try:
                with open(self.legacy_path, 'r', encoding='utf-8') as f:
                    legacy_data = json.load(f)
                for item in legacy_data:
                    category = self._guess_category(item.get("learned_instruction", ""))
                    self.save_rule(
                        instruction=item["learned_instruction"],
                        trigger_patterns=item["trigger_patterns"],
                        category=category,
                        severity=item.get("severity", 3),
                        source_session=item.get("source_session", "legacy_migration")
                    )
                os.rename(self.legacy_path, self.legacy_path + ".migrated.bak")
            except Exception as e:
                logger.error(f"Migration failed: {e}")

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

    def save_rule(self, instruction: str, trigger_patterns: List[str], category: Optional[str] = None, severity: int = 3, source_session: Optional[str] = None, context: Optional[str] = None) -> str:
        """새로운 규칙을 특정 샤드에 저장 (ID 반환 및 밀리초 단위 식별자 사용)"""
        cat = category or self._guess_category(instruction + " " + " ".join(trigger_patterns))
        if cat not in self.shards:
            self.shards[cat] = self._load_shard(cat)
            
        shard = self.shards[cat]
        new_patterns = set(trigger_patterns)
        
        for existing in shard:
            if existing["learned_instruction"].strip() == instruction.strip():
                existing["trigger_patterns"] = list(set(existing["trigger_patterns"]).union(new_patterns))
                existing["reinforcement_count"] = existing.get("reinforcement_count", 0) + 1
                self._persist_shard(cat)
                return existing["id"]

        # %f 추가하여 밀리초 단위 충돌 방지
        rule_id = f"RULE_{cat.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
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
            "failure_count": 0,
            "is_certified": False
        }
        shard.append(new_rule)
        self._persist_shard(cat)
        logger.info(f"New rule saved to '{cat}' shard: {rule_id}")
        return rule_id

    def get_active_constraints(self, context_text: str) -> List[str]:
        """맥락과 관련된 샤드에서 활성 제약 조건 추출 (디스크 강제 동기화 및 3단계 정밀 정렬)"""
        target_cat = self._guess_category(context_text)
        search_cats = {target_cat, "general"}
        
        matching_rules = []
        for cat in search_cats:
            # 실시간 동기화: 항상 디스크에서 최신 샤드를 읽어옴
            shard = self._load_shard(cat)
            self.shards[cat] = shard
            
            for rule in shard:
                if any(p.lower() in context_text.lower() for p in rule["trigger_patterns"]):
                    # 1. 상태 보정 (누락된 필드 복구)
                    usage = int(rule.get("usage_count", 0))
                    success = int(rule.get("success_count", 0))
                    is_certified = bool(rule.get("is_certified", False))
                    
                    # 2. 영향력 점수 계산 (Laplace Smoothing)
                    # usage를 1 증가시킨 가상의 점수로 정렬
                    rule["impact_score"] = float((success + 1) / (usage + 2))
                    rule["is_certified"] = is_certified
                    
                    matching_rules.append(rule)
                    # 통계 갱신 (실제 반영은 record_rule_outcome에서 하되, 
                    # 조회 횟수 증가는 추적용으로 남길 수 있음. 여기선 생략하여 순수 조회 유지)
            
        # [Precision Sorting] 1. 공인 여부(우선), 2. 영향력 점수, 3. 심각도 순 정렬
        # reverse=True -> 큰 값이 앞으로 (1 > 0, 0.8 > 0.3, 5 > 1)
        def get_sort_key(r):
            cert_val = 1 if r.get("is_certified") is True else 0
            impact = float(r.get("impact_score", 0.0))
            sev = int(r.get("severity", 0))
            return (cert_val, impact, sev)

        matching_rules.sort(key=get_sort_key, reverse=True)
        return [r["learned_instruction"] for r in matching_rules]

    def record_rule_outcome(self, rule_id: str, success: bool):
        """특정 규칙의 성과 기록 및 자동 인증 체크"""
        for cat, shard in self.shards.items():
            for rule in shard:
                if rule["id"] == rule_id:
                    rule["usage_count"] = rule.get("usage_count", 0) + 1
                    if success: 
                        rule["success_count"] = rule.get("success_count", 0) + 1
                    else: 
                        rule["failure_count"] = rule.get("failure_count", 0) + 1
                    
                    # [Auto-Certification] 성과 기반 공인 지혜 승격 (임계치: 10회 사용, 성공률 90% 이상)
                    usage = rule.get("usage_count", 0)
                    success_count = rule.get("success_count", 0)
                    if usage >= 10 and (success_count / usage) >= 0.9:
                        if not rule.get("is_certified"):
                            rule["is_certified"] = True
                            logger.info(f"🎓 Rule {rule['id']} promoted to CERTIFIED WISDOM.")
                    
                    self._persist_shard(cat)
                    return

    def prune_memory(self, model_id: str = "gemini-2.0-flash"):
        """샤드별로 의미론적 통합 수행하여 중복 지식 제거"""
        for cat in list(self.shards.keys()):
            shard = self.shards[cat]
            if len(shard) < 2: continue
            
            logger.info(f"✨ Pruning '{cat}' memory shard semantically...")
            rules_text = "\n".join([f"[{i}] {r['learned_instruction']} (Patterns: {r['trigger_patterns']})" for i, r in enumerate(shard)])
            prompt = f"당신은 지식 최적화 전문가입니다. 다음 '{cat}' 분야의 규칙들을 분석하여 하나로 통합하십시오.\n{rules_text}"
            
            try:
                from gortex.core.llm.factory import LLMFactory
                backend = LLMFactory.get_default_backend()
                response = backend.generate(model_id, [{"role": "user", "content": prompt}])
                import re
                # 정규식 수정: [.*]
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    new_data = json.loads(json_match.group(0))
                    updated_shard = []
                    for idx, r_data in enumerate(new_data):
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
            except:
                pass