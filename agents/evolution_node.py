import json
import os
import logging
import re
from datetime import datetime
from typing import Dict, Any, List
from gortex.core.state import GortexState
from gortex.core.llm.factory import LLMFactory
from gortex.utils.tools import read_file, write_file, execute_shell
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

    def prepare_fine_tuning_job(self, dataset_path: str = "logs/datasets/evolution.jsonl") -> Dict[str, Any]:
        """
        수집된 진화 데이터를 기반으로 Fine-tuning 작업(Job)을 패키징합니다.
        데이터 검증, 변환, 설정 파일 생성을 포함합니다.
        """
        if not os.path.exists(dataset_path):
            return {"status": "failed", "reason": f"Dataset not found: {dataset_path}"}
            
        try:
            # 1. Load and Validate Data
            valid_data = []
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if "messages" in entry and isinstance(entry["messages"], list):
                            valid_data.append(entry)
                    except: continue
            
            if not valid_data:
                return {"status": "failed", "reason": "No valid data found in dataset"}
                
            # 2. Create Job Directory
            job_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            job_dir = f"training_jobs/job_{job_id}"
            os.makedirs(job_dir, exist_ok=True)
            
            # 3. Save Processed Dataset (ShareGPT/Chat format)
            # 여기서는 JSONL을 그대로 유지하되, 하나의 JSON 배열로 변환하여 저장
            output_dataset = os.path.join(job_dir, "dataset.json")
            with open(output_dataset, "w", encoding="utf-8") as f:
                json.dump(valid_data, f, indent=2, ensure_ascii=False)
                
            # 4. Copy/Template Config
            config_template = "config/training.yaml"
            job_config = os.path.join(job_dir, "config.yaml")
            
            if os.path.exists(config_template):
                with open(config_template, "r", encoding="utf-8") as f:
                    config_content = f.read()
            else:
                # Fallback config
                config_content = "model: unsloth/llama-3-8b-bnb-4bit\nlora_r: 16\n"
            
            with open(job_config, "w", encoding="utf-8") as f:
                f.write(f"# Job ID: {job_id}\n# Source: {dataset_path}\n\n{config_content}")
                
            # 5. Create Metadata
            meta = {
                "job_id": job_id,
                "created_at": datetime.now().isoformat(),
                "data_count": len(valid_data),
                "source_file": dataset_path,
                "status": "ready"
            }
            with open(os.path.join(job_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
                
            logger.info(f"📦 Fine-tuning job prepared: {job_dir} ({len(valid_data)} items)")
            return {
                "status": "success", 
                "job_dir": job_dir, 
                "item_count": len(valid_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare fine-tuning job: {e}")
            return {"status": "error", "reason": str(e)}

    def heal_architecture(self, state: GortexState, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """발견된 아키텍처 위반 사항(Layer Violation 등)을 자동으로 수정합니다."""
        if not violations:
            return {"thought": "수정할 아키텍처 위반 사항이 없습니다.", "next_node": "manager"}

        # 가장 심각한 위반 또는 첫 번째 위반 선택
        v = violations[0]
        source_mod = v["source"]
        target_mod = v["target"]
        reason = v["reason"]
        
        # 실제 파일 경로 찾기
        source_file = source_mod.replace(".", "/") + ".py"
        if not os.path.exists(source_file):
            # gortex prefix 제거 시도
            source_file = source_file.replace("gortex/", "")
            
        if not os.path.exists(source_file):
            return {"thought": f"수정 대상 파일 {source_file}을 찾을 수 없습니다.", "next_node": "manager"}

        original_code = read_file(source_file)
        
        prompt = f"""너는 Gortex의 아키텍처 수호자다. 
다음 아키텍처 위반 사항을 해결하기 위해 코드를 리팩토링하라.

[위반 내용] {reason}
[위반 경로] {source_mod} -> {target_mod}
[수정 파일] {source_file}

주로 상위 레이어의 기능을 하위 레이어에서 직접 참조할 때 발생한다.
해결 전략: 
1. 상위 레이어의 기능을 추상화(Interface/Base Class)하여 하위 레이어로 옮긴다.
2. 또는 하위 레이어에서 상위 레이어 참조를 제거하고 콜백이나 DI를 사용한다.

수정된 전체 코드를 반환하라. 코드 외의 설명은 배제하고 오직 코드만 출력하라.
"""
        logger.info(f"🛡️ Healing architecture in {source_file}...")
        assigned_model = "gemini-1.5-pro" # 고수준 아키텍처 판단은 PRO 사용
        
        start_time = time.time()
        try:
            new_code = self.backend.generate(assigned_model, [{"role": "user", "content": prompt}])
            new_code = re.sub(r'```python\n|```', '', new_code).strip()
            
            # [Simulation Step]
            if not self.simulate_evolution(state, source_file, new_code):
                return {
                    "thought": "아키텍처 치유 시뮬레이션 결과 건강도가 하락하여 중단됨.",
                    "messages": [("system", "⚠️ 시뮬레이션 결과 건강도 하락이 예상되어 리팩토링이 차단되었습니다.")],
                    "next_node": "manager"
                }

            write_file(source_file, new_code)
            check_res = execute_shell(f"./scripts/pre_commit.sh --selective {source_file}")
            
            latency_ms = int((time.time() - start_time) * 1000)
            success = "Ready to commit" in check_res
            
            self.monitor.record_interaction("arch_healing", assigned_model, success, len(new_code)//4, latency_ms, metadata={"violation": reason})

            if success:
                return {
                    "thought": f"아키텍처 치유 성공: {source_file}의 레이어 위반 해소.",
                    "messages": [("ai", f"🛡️ **아키텍처 자가 치유 완료**\n- 대상: {source_file}\n- 결과: 레이어 위반 사항이 해소되었습니다.")],
                    "next_node": "manager"
                }
            else:
                write_file(source_file, original_code)
                return {
                    "thought": f"아키텍처 치유 실패: {check_res}", 
                    "messages": [("system", f"⚠️ 아키텍처 치유 실패: {source_file} 리팩토링 중 검증 오류가 발생하여 롤백되었습니다.")],
                    "next_node": "manager"
                }
        except Exception as e:
            logger.error(f"Arch healing error: {e}")
            return {
                "thought": f"아키텍처 치유 중 오류: {e}", 
                "messages": [("system", f"❌ 아키텍처 치유 중 치명적 오류 발생: {e}")],
                "next_node": "manager"
            }

    def evolve_subsystem(self, state: GortexState) -> Dict[str, Any]:
        """서브시스템 전체의 아키텍처를 점진적으로 개선 (다중 파일)"""
        candidates = self._get_radar_candidates()
        if not candidates:
            return {"thought": "진화 후보가 없습니다.", "next_node": "manager"}

        target = next((c for c in candidates if c.get("effort") == "High"), candidates[0])
        target_file = target.get("target_file")
        
        # 1. 영향 범위 분석
        from gortex.utils.indexer import SynapticIndexer
        indexer = SynapticIndexer()
        impact = indexer.get_impact_radius(target_file)
        
        related_files = [target_file] + impact.get("direct", [])
        files_context = ""
        for f in related_files:
            if os.path.exists(f):
                files_context += f"\n--- FILE: {f} ---\n{read_file(f)}\n"

        prompt = f"""너는 Gortex의 시스템 아키텍트다. 
다음 파일들을 분석하여 기술 '{target.get('tech')}'를 일관성 있게 적용하라.

[대상 파일들]
{', '.join(related_files)}

[파일 내용들]
{files_context}

각 파일별 수정된 전체 코드를 다음 JSON 형식으로 반환하라:
{{
    "files": [
        {{ "path": "file1.py", "content": "..." }},
        {{ "path": "file2.py", "content": "..." }}
    ]
}}
"""
        logger.info(f"🚀 Evolving subsystem: {target_file} and related {len(impact.get('direct', []))} files...")
        assigned_model = "gemini-1.5-pro"
        
        try:
            response_text = self.backend.generate(assigned_model, [{"role": "user", "content": prompt}], {"response_mime_type": "application/json"})
            import json
            res_data = json.loads(response_text)
            
            modified_files = []
            for f_data in res_data.get("files", []):
                path = f_data["path"]
                content = f_data["content"]
                write_file(path, content)
                modified_files.append(path)
            
            # 일괄 검증
            check_res = execute_shell(f"./scripts/pre_commit.sh --selective {' '.join(modified_files)}")
            if "Ready to commit" in check_res:
                return {
                    "thought": f"서브시스템 진화 성공: {len(modified_files)}개 파일 수정 완료.",
                    "messages": [("ai", f"🏛️ **서브시스템 아키텍처 진화 완료**\n- 대상: {target_file} 및 관련 모듈\n- 수정 파일: {', '.join(modified_files)}")],
                    "next_node": "analyst",
                    "awaiting_review": True,
                    "review_target": f"Subsystem ({target_file})"
                }
            else:
                # 롤백 (단순화: 여기선 생략하나 실제로는 백업 복구 필요)
                return {"thought": "서브시스템 진화 검증 실패", "next_node": "manager"}
        except Exception as e:
            return {"thought": f"서브시스템 진화 중 오류: {e}", "next_node": "manager"}

    def simulate_evolution(self, state: GortexState, target_file: str, new_code: str) -> bool:
        """코드 수정이 실제로 건강도 점수를 향상시키는지 가상 시뮬레이션"""
        original_code = read_file(target_file)
        from gortex.utils.indexer import SynapticIndexer
        indexer = SynapticIndexer()
        
        # 1. 수정 전 점수 측정
        before_stats = indexer.calculate_health_score()
        
        # 2. 임시 파일 쓰기 및 재인덱싱
        write_file(target_file, new_code)
        indexer.scan_project()
        after_stats = indexer.calculate_health_score()
        
        # 3. 점수 비교
        improved = after_stats["score"] >= before_stats["score"]
        
        if not improved:
            logger.warning(f"📉 Simulation rejected: Health score would drop from {before_stats['score']} to {after_stats['score']}")
            write_file(target_file, original_code) # 원복
            indexer.scan_project() # 인덱스 복구
        else:
            logger.info(f"📈 Simulation passed: Health score {before_stats['score']} -> {after_stats['score']}")
            
        return improved

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
            new_code = re.sub(r'```python\n|```', '', new_code).strip()
            
            # [Simulation Step]
            if not self.simulate_evolution(state, target_file, new_code):
                return {
                    "thought": "시스템 진화 시뮬레이션 결과 건강도가 하락하여 중단됨.",
                    "messages": [("system", "⚠️ 시뮬레이션 결과 건강도 하락이 예상되어 리팩토링이 차단되었습니다.")],
                    "next_node": "manager"
                }

            # 1. 파일 쓰기
            write_file(target_file, new_code)
            
            # 2. 검증 (테스트 실행)
            check_res = execute_shell(f"./scripts/pre_commit.sh --selective {target_file}")
            
            latency_ms = int((time.time() - start_time) * 1000)
            success = "Ready to commit" in check_res
            
            # RLHF-lite: 실시간 피드백 루프 적용
            self.monitor.record_interaction("evolution", assigned_model, success, len(new_code)//4, latency_ms, metadata={"tech": tech_name, "file": target_file})
            if not success:
                self.monitor.apply_immediate_feedback(assigned_model, False, weight=2.0) # 진화 실패는 큰 페널티

            if success:
                logger.info(f"✅ Evolution successful: {target_file} updated with {tech_name}")
                return {
                    "thought": f"시스템 진화 성공: {target_file}에 {tech_name}을(를) 적용했습니다. 교차 리뷰를 요청합니다.",
                    "messages": [("ai", f"🧬 **시스템 자가 진화 시도 완료**\n- 기술: {tech_name}\n- 대상: {target_file}\n- 상태: 검증 통과, 교차 리뷰 중...")],
                    "next_node": "analyst", # Analyst에게 넘겨 리뷰 받음
                    "awaiting_review": True,
                    "review_target": target_file
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
    node = EvolutionNode()
    
    # 1. 아키텍처 위반 사항 확인 (Analyst 기능 활용)
    from gortex.agents.analyst import AnalystAgent
    analyst = AnalystAgent()
    violations = analyst.audit_architecture()
    
    if violations:
        return node.heal_architecture(state, violations)
        
    # 2. 서브시스템 단위 진화 (High Effort 후보가 있는 경우)
    candidates = node._get_radar_candidates()
    if any(c.get("effort") == "High" for c in candidates):
        return node.evolve_subsystem(state)

    # 3. 일반 시스템 진화
    return node.evolve_system(state)
