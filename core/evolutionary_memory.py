import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("GortexEvolutionaryMemory")

class EvolutionaryMemory:
    """
    사용자의 피드백을 통해 학습된 규칙(experience.json)을 관리하는 클래스.
    """
    def __init__(self, file_path: str = "experience.json"):
        self.file_path = file_path
        self.memory: List[Dict[str, Any]] = self._load_memory()

    def _load_memory(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load evolutionary memory: {e}")
                return []
        return []

    def save_rule(self, instruction: str, trigger_patterns: List[str], severity: int = 3, source_session: Optional[str] = None, context: Optional[str] = None):
        """새로운 규칙을 저장 (지능형 병합, 충돌 감지 및 우선순위 강화 로직)"""
        new_patterns = set(trigger_patterns)
        
        # 1. 기존 규칙 분석 (중복 및 충돌 검사)
        for existing in self.memory:
            existing_patterns = set(existing["trigger_patterns"])
            # 지침의 유사도 계산 (단순화: 완전 일치 또는 포함 관계)
            inst_match = existing["learned_instruction"].strip() == instruction.strip()
            # 트리거 패턴 겹침 정도 (Intersection over Union 유사도)
            intersection = existing_patterns.intersection(new_patterns)
            union = existing_patterns.union(new_patterns)
            pattern_similarity = len(intersection) / len(union) if union else 0

            # CASE A: 동일한 지침인 경우 -> 패턴 병합 및 강화
            if inst_match:
                logger.info(f"Duplicate rule detected. Reinforcing existing rule: {existing['id']}")
                existing["trigger_patterns"] = list(union)
                existing["severity"] = max(existing.get("severity", 3), severity)
                existing["reinforcement_count"] = existing.get("reinforcement_count", 0) + 1
                existing["last_reinforced"] = datetime.now().isoformat()
                if context: existing["context"] = context
                self._persist()
                return
            
            # CASE B: 지침은 다르지만 트리거 패턴이 매우 유사한 경우 (충돌 위험)
            if pattern_similarity >= 0.7:
                logger.warning(f"⚠️ POTENTIAL CONFLICT: New rule for {new_patterns} might contradict existing rule {existing['id']} ({existing_patterns})")
                # 중요도가 더 높은 쪽을 우선하거나, 사용자에게 알림을 줄 수 있는 데이터 추가
                existing["conflict_warning"] = True
                existing["potential_contradiction"] = instruction

        # 2. 새로운 규칙 생성
        rule_id = f"RULE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


        new_rule = {
            "id": rule_id,
            "trigger_patterns": trigger_patterns,
            "learned_instruction": instruction,
            "context": context,
            "severity": severity,
            "reinforcement_count": 1,
            "source_session": source_session,
            "created_at": datetime.now().isoformat(),
            "last_reinforced": datetime.now().isoformat(),
            "usage_count": 0
        }
        self.memory.append(new_rule)
        self._persist()
        logger.info(f"New rule saved: {rule_id} - {instruction}")



    def _persist(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist evolutionary memory: {e}")

    def get_active_constraints(self, context_text: str) -> List[str]:
        """컨텍스트와 매칭되는 활성 제약 조건(규칙) 목록 반환"""
        active_rules = []
        for rule in self.memory:
            if any(pattern.lower() in context_text.lower() for pattern in rule["trigger_patterns"]):
                active_rules.append(rule["learned_instruction"])
                rule["usage_count"] = rule.get("usage_count", 0) + 1
        
        if active_rules:
            self._persist()
        return active_rules

    def gc_rules(self, min_usage: int = 1, max_age_days: int = 30):
        """사용 빈도가 낮고 오래된 규칙 정리"""
        now = datetime.now()
        original_count = len(self.memory)
        
        def is_active(rule):
            created_at = datetime.fromisoformat(rule.get("created_at", now.isoformat()))
            age_days = (now - created_at).days
            usage = rule.get("usage_count", 0)
            # 생성된 지 max_age_days가 지났는데 사용 횟수가 min_usage 미만이면 삭제
            if age_days > max_age_days and usage < min_usage:
                return False
            return True

        self.memory = [r for r in self.memory if is_active(r)]
        if len(self.memory) < original_count:
            logger.info(f"Evolutionary Memory GC: Removed {original_count - len(self.memory)} rules.")
            self._persist()

