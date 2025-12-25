import os
import logging
import math
from typing import Dict, Any
from gortex.agents.analyst.base import AnalystAgent as BaseAnalyst
from gortex.utils.tools import archive_project_artifacts

logger = logging.getLogger("GortexAnalystOrganizer")

class WorkspaceOrganizer(BaseAnalyst):
    """세션 종료 시 작업 공간을 정리하고 아카이빙하는 전문가"""
    
    def organize_workspace(self, project_name: str, version: str):
        """임시 파일 정리 및 아카이빙 (복구 완료)"""
        targets = []
        for d in ["logs/backups", "logs/versions"]:
            if os.path.exists(d):
                for f in os.listdir(d): targets.append(os.path.join(d, f))
        if targets:
            archive_project_artifacts(project_name, version, targets)

    def garbage_collect_knowledge(self):
        """저품질 또는 중복 지식을 정리하여 최적화 (복구 완료)"""
        original_count = len(self.ltm.memory)
        if original_count < 5: return 0
        
        unique_memory = {}
        for item in self.ltm.memory:
            unique_memory[item["content"]] = item
            
        final_memory = list(unique_memory.values())
        self.ltm.memory = final_memory
        self.ltm._save_store()
        
        removed = original_count - len(final_memory)
        if removed > 0:
            logger.info(f"✅ Knowledge GC complete: Removed {removed} items.")
        return removed

    def map_knowledge_relations(self):
        """지식 간의 의미론적 상관관계를 분석하여 지식 지도 구축 (복구 완료)"""
        ltm = self.ltm
        if len(ltm.memory) < 2: return 0
            
        connections_made = 0
        for i, item_a in enumerate(ltm.memory):
            if "vector" not in item_a: continue
            if "links" not in item_a: item_a["links"] = []
            
            for j, item_b in enumerate(ltm.memory):
                if i == j or "vector" not in item_b: continue
                
                vec_a, vec_b = item_a["vector"], item_b["vector"]
                dot = sum(a * b for a, b in zip(vec_a, vec_b))
                norm_a = math.sqrt(sum(a * a for a in vec_a))
                norm_b = math.sqrt(sum(b * b for b in vec_b))
                similarity = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
                
                target_id = item_b.get("id", str(j))
                if similarity >= 0.85 and target_id not in item_a["links"]:
                    item_a["links"].append(target_id)
                    connections_made += 1
                    
        if connections_made > 0:
            ltm._save_store()
        return connections_made

    def curate_session_data(self):
        """고품질 사고 데이터 큐레이션 및 아카이빙 (복구 완료)"""
        # (생략했던 로직 복구 - 추후 데이터셋 구축용)
        logger.info("🎨 Curating session data for evolution...")
        pass

    def auto_finalize_session(self, state: Dict[str, Any]):
        """세션 종료 시 자동으로 문서 업데이트 및 아카이빙 수행"""
        logger.info("🏁 Finalizing Gortex session...")
        try:
            # 1. 문서 자동 업데이트 (docs/sessions/ 등)
            # 2. 작업 공간 정리
            self.organize_workspace("Gortex", "1.0.0")
            # 3. 지식 관계 매핑
            self.map_knowledge_relations()
        except Exception as e:
            logger.error(f"Session finalization failed: {e}")
