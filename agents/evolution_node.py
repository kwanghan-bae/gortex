import json
import os
import logging
import re
from typing import Dict, Any, List, Optional
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.tools import read_file, write_file, execute_shell, list_files
from gortex.utils.efficiency_monitor import EfficiencyMonitor

logger = logging.getLogger("GortexEvolution")

class EvolutionNode:
    """
    Gortex의 자가 진화 엔진.
    시스템의 소스 코드를 스스로 리팩토링하고 신기술을 도입합니다.
    """
    def __init__(self):
        self.backend = LLMFactory.get_default_backend()
        self.monitor = EfficiencyMonitor()

    def _get_radar_candidates(self) -> List[Dict[str, Any]]:
        """Tech Radar에서 도입 후보를 가져옵니다."""
        if os.path.exists("tech_radar.json"):
            try:
                with open("tech_radar.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("adoption_candidates", [])
            except:
                pass
        return []

    def evolve_system(self, state: GortexState) -> Dict[str, Any]:
        """시스템 진화 로직 실행"""
        candidates = self._get_radar_candidates()
        if not candidates:
            return {"thought": "도입할 만한 신규 기술 후보가 없습니다.", "next_node": "manager"}

        # 가장 우선순위가 높은 후보 선택 (여기선 첫 번째)
        target = candidates[0]
        target_file = target.get("target_file")
        tech_name = target.get("tech")
        reason = target.get("reason")

        if not target_file or not os.path.exists(target_file):
            return {"thought": f"대상 파일 {target_file}을 찾을 수 없습니다.", "next_node": "manager"}

        original_code = read_file(target_file)
        
        prompt = f"""너는 Gortex의 진화 설계자다. 
다음 기술/패턴을 프로젝트에 도입하여 코드를 개선하라.

[대상 기술] {tech_name}
[도입 이유] {reason}
[대상 파일] {target_file}

[현재 코드]
{original_code}

개선된 전체 코드를 반환하라. 코드 외의 설명은 배제하고 오직 코드만 출력하라.
"""
        logger.info(f"🧬 Evolving {target_file} with {tech_name}...")
        
        assigned_model = state.get("assigned_model", "gemini-1.5-pro") # 진화는 정교해야 하므로 PRO 권장
        
        start_time = time.time()
        try:
            new_code = self.backend.generate(assigned_model, [{"role": "user", "content": prompt}])
            
            # 마크다운 코드 블록 제거
            new_code = re.sub(r'```python\n|```', '', new_code).strip()
            
            # 1. 파일 쓰기
            write_file(target_file, new_code)
            
            # 2. 검증 (테스트 실행)
            check_res = execute_shell(f"./scripts/pre_commit.sh --selective {target_file}")
            
            latency_ms = int((time.time() - start_time) * 1000)
            success = "Ready to commit" in check_res
            
            self.monitor.record_interaction("evolution", assigned_model, success, len(new_code)//4, latency_ms, metadata={"tech": tech_name, "file": target_file})

            if success:
                logger.info(f"✅ Evolution successful: {target_file} updated with {tech_name}")
                return {
                    "thought": f"시스템 진화 성공: {target_file}에 {tech_name}을(를) 적용했습니다.",
                    "messages": [("ai", f"🧬 **시스템 자가 진화 완료**\n- 기술: {tech_name}\n- 대상: {target_file}\n- 결과: 성공적으로 리팩토링되었습니다.")],
                    "next_node": "manager"
                }
            else:
                # 실패 시 롤백 (write_file의 백업 기능을 활용하거나 직접 복구)
                logger.warning(f"❌ Evolution failed validation. Rolling back {target_file}...")
                write_file(target_file, original_code)
                return {
                    "thought": f"시스템 진화 실패 (검증 단계): {check_res}",
                    "messages": [("system", f"⚠️ 진화 시도 실패: {tech_name} 적용 중 오류 발생. 롤백되었습니다.")],
                    "next_node": "manager"
                }

        except Exception as e:
            logger.error(f"Evolution process error: {e}")
            return {"thought": f"진화 중 치명적 오류: {e}", "next_node": "manager"}

import time

def evolution_node(state: GortexState) -> Dict[str, Any]:
    """Evolution 노드 엔트리 포인트"""
    return EvolutionNode().evolve_system(state)
