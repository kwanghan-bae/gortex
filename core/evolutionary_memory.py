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
    def __init__(self, base_dir: Optional[str] = None, **kwargs):
        # 하위 호환성: file_path가 kwargs로 들어오면 base_dir로 사용 (디렉토리로 취급)
        file_path = kwargs.get("file_path")
        self.base_dir = base_dir or (os.path.dirname(file_path) if file_path else "logs/memory") or "logs/memory"
        
        if not self.base_dir or self.base_dir == ".":
             self.base_dir = "logs/memory"

        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "snapshots"), exist_ok=True)
        self.legacy_path = "experience.json"
        self.shards: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_shards()

    @property
    def memory(self) -> List[Dict[str, Any]]:
        """모든 샤드의 규칙을 취합하여 반환 (하위 호환성 유지)"""
        all_rules = []
        for cat in self.shards:
            all_rules.extend(self.shards[cat])
        return all_rules

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
        # Storage Provider Abstraction (Redis or Local/SQLite)
        from gortex.core.mq import mq_bus
        key = f"gortex:memory:shard:{category}"
        try:
            data_str = mq_bus.storage.get(key)
            if data_str:
                logger.debug(f"Loaded '{category}' shard from Storage.")
                return json.loads(data_str)
        except Exception as e:
            logger.warning(f"Failed to load shard from Storage: {e}")
        
        # Legacy File Fallback (Migration support only, prioritized Storage)
        path = os.path.join(self.base_dir, f"{category}_shard.json")
        if os.path.exists(path):
             try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
             except: pass
        return []

    def _persist_shard(self, category: str):
        data = self.shards.get(category, [])
        from gortex.core.mq import mq_bus
        key = f"gortex:memory:shard:{category}"
        
        # Logic: Acquire Lock -> Set to Storage -> Publish Event
        lock_name = f"shard_write:{category}"
        if mq_bus.acquire_lock(lock_name):
            try:
                # Save to Unified Storage
                mq_bus.storage.set(key, json.dumps(data, ensure_ascii=False, indent=2))
                mq_bus.publish_event("gortex:memory_updates", "Memory", "shard_updated", {"category": category})
            except Exception as e:
                logger.error(f"Failed to persist {category} shard to Storage: {e}")
            finally:
                mq_bus.release_lock(lock_name)
        else:
            logger.warning(f"Failed to acquire lock for shard '{category}'. Possible concurrent write.")

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

    def save_rule(self, instruction: str, trigger_patterns: List[str], category: Optional[str] = None, severity: int = 3, source_session: Optional[str] = None, context: Optional[str] = None, is_super_rule: bool = False) -> str:
        """새로운 규칙을 특정 샤드에 저장 (ID 반환 및 밀리초 단위 식별자 사용)"""
        # 0. 전역 중복 체크 (모든 샤드에서 검색)
        instruction_clean = instruction.strip()
        for cat_name, shard_list in self.shards.items():
            for existing in shard_list:
                if existing["learned_instruction"].strip() == instruction_clean:
                    existing["trigger_patterns"] = list(set(existing["trigger_patterns"]).union(set(trigger_patterns)))
                    existing["reinforcement_count"] = existing.get("reinforcement_count", 0) + 1
                    # 메타데이터 업데이트
                    if severity > existing.get("severity", 0):
                        existing["severity"] = severity
                    if context:
                        existing["context"] = context
                    if is_super_rule:
                        existing["is_super_rule"] = True
                    self._persist_shard(cat_name)
                    return existing["id"]

        cat = category or self._guess_category(instruction + " " + " ".join(trigger_patterns))
        if cat not in self.shards:
            self.shards[cat] = self._load_shard(cat)
            
        shard = self.shards[cat]
        
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
            "is_certified": False,
            "is_super_rule": is_super_rule
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
                    rule["is_super_rule"] = bool(rule.get("is_super_rule", False))
                    
                    matching_rules.append(rule)
                    # 통계 갱신 (실제 반영은 record_rule_outcome에서 하되, 
                    # 조회 횟수 증가는 추적용으로 남길 수 있음. 여기선 생략하여 순수 조회 유지)
            
        # [Precision Sorting] 1. 초월적 규칙(Super), 2. 공인 여부(Cert), 3. 영향력 점수, 4. 심각도 순 정렬
        # reverse=True -> 큰 값이 앞으로 (1 > 0, 0.8 > 0.3, 5 > 1)
        def get_sort_key(r):
            super_val = 1 if r.get("is_super_rule") is True else 0
            cert_val = 1 if r.get("is_certified") is True else 0
            impact = float(r.get("impact_score", 0.0))
            sev = int(r.get("severity", 0))
            return (super_val, cert_val, impact, sev)

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

    def calculate_rule_value(self, rule: Dict[str, Any]) -> float:
        """경험 규칙의 생존 가치를 평가함 (0~100)."""
        # 1. 보호 대상: 초월적 규칙, 공인 지혜 또는 생성된 지 얼마 안 된 규칙
        if rule.get("is_super_rule") or rule.get("is_certified"): return 100.0
        
        created_at = datetime.fromisoformat(rule.get("created_at", datetime.now().isoformat()))
        age_days = (datetime.now() - created_at).days
        if age_days < 7: return 90.0 # 일주일 내 생성된 지식은 보존
        
        # 2. 성능 기반 점수 (성공률)
        usage = rule.get("usage_count", 0)
        success = rule.get("success_count", 0)
        success_rate = (success / usage) if usage > 0 else 0.5
        
        # 3. 사용 빈도 점수 (10세션 기준)
        usage_score = min(1.0, usage / 10.0)
        
        # 4. 최종 가치 계산: (성공률 * 0.7) + (빈도 * 0.3)
        # 단, 사용이 전혀 없는 노후 지식은 감점
        value = (success_rate * 70) + (usage_score * 30)
        if usage == 0 and age_days > 14: value -= 40
        
        return round(max(0.0, min(100.0, value)), 1)

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