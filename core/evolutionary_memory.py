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
        """새로운 규칙을 저장 (중복 체크, 병합, 충돌 감지 및 우선순위 강화 로직 포함)"""
        # 1. 기존 규칙 분석 (중복 및 충돌 검사)
        for existing in self.memory:
            # 동일 지침 확인
            if existing["learned_instruction"].strip() == instruction.strip():
                logger.info(f"Duplicate rule detected. Reinforcing existing rule: {existing['id']}")
                existing["trigger_patterns"] = list(set(existing["trigger_patterns"] + trigger_patterns))
                existing["severity"] = max(existing["severity"], severity)
                existing["reinforcement_count"] = existing.get("reinforcement_count", 0) + 1
                existing["last_reinforced"] = datetime.now().isoformat()
                if context: existing["context"] = context
                self._persist()
                return
            
            # 충돌 감지 (단순화: 트리거 패턴이 50% 이상 겹치는데 지침이 다를 경우)
            existing_patterns = set(existing["trigger_patterns"])
            new_patterns = set(trigger_patterns)
            intersection = existing_patterns.intersection(new_patterns)
            
            if len(intersection) > 0 and (len(intersection) >= len(new_patterns) / 2):
                logger.warning(f"⚠️ Potential rule conflict detected with {existing['id']} over patterns: {intersection}")
                # 충돌 발생 시 현재는 새 규칙을 추가하되 중요도(severity)를 조정하거나 로그에 기록
                # (향후 LLM을 통한 자동 해결 로직으로 확장 가능)

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
            # 단순 키워드 매칭 (나중에 임베딩 기반 검색으로 확장 가능)
            if any(pattern.lower() in context_text.lower() for pattern in rule["trigger_patterns"]):
                active_rules.append(rule["learned_instruction"])
                rule["usage_count"] += 1
        
        if active_rules:
            self._persist() # usage_count 업데이트 저장
        return active_rules
