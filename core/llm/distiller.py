import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from gortex.core.evolutionary_memory import EvolutionaryMemory
from gortex.core.llm.factory import LLMFactory

logger = logging.getLogger("GortexNeuralDistiller")

class NeuralDistiller:
    """
    시스템의 흩어진 지식(Experience Shards)을 분석하여 
    핵심 원칙으로 증류(Distillation)하고 자가 학습 데이터셋을 생성함.
    """
    def __init__(self):
        self.memory = EvolutionaryMemory()
        self.backend = LLMFactory.get_default_backend()

    def distill_wisdom(self, category: str = "coding") -> Optional[str]:
        """특정 분야의 고성과 규칙들을 하나의 정제된 원칙으로 압축함."""
        shard = self.memory.shards.get(category, [])
        # 성공률 90% 이상, 사용 5회 이상의 '공인된' 지식만 선별
        certified = [r for r in shard if r.get("is_certified") or (r.get("usage_count", 0) >= 5 and (r.get("success_count", 0)/r["usage_count"]) >= 0.9)]
        
        if len(certified) < 3:
            return None
            
        logger.info(f"🔮 Distilling wisdom from {len(certified)} certified rules in '{category}'...")
        
        rules_text = "\n".join([f"- {r['learned_instruction']}" for r in certified])
        prompt = f"""당신은 지식 증류 전문가입니다. 다음 {category} 분야의 공인된 지식들을 분석하여, 
        에이전트가 반드시 준수해야 할 하나의 통합된 '최상위 원칙'으로 요약하십시오.
        불필요한 수식어를 빼고 매우 엄격하고 기술적인 문체로 작성하십시오.
        
        [Certified Knowledge]:
        {rules_text}
        """
        
        try:
            distilled = self.backend.generate("gemini-2.0-flash", [{"role": "user", "content": prompt}])
            return distilled.strip()
        except Exception as e:
            logger.error(f"Distillation failed: {e}")
            return None

    def prepare_training_dataset(self, output_dir: str = "training_jobs"):
        """성공적인 버그 수정 및 최적화 사례를 LLM Fine-tuning용 JSONL로 변환."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"gortex_dataset_{timestamp}.jsonl")
        
        # 1. 모든 샤드에서 지식 수집
        all_rules = self.memory.memory
        valid_samples = 0
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                for rule in all_rules:
                    # 문맥과 해답이 모두 존재하는 고품질 데이터만 사용
                    if rule.get("context") and rule.get("learned_instruction"):
                        entry = {
                            "instruction": f"As a Gortex Agent, provide a solution for the following technical situation in {rule.get('category', 'general')} domain.",
                            "input": rule["context"],
                            "output": rule["learned_instruction"]
                        }
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                        valid_samples += 1
            
            if valid_samples > 0:
                logger.info(f"📂 Created self-learning dataset with {valid_samples} samples: {output_path}")
                return output_path
            else:
                os.remove(output_path)
                return None
        except Exception as e:
            logger.error(f"Failed to prepare dataset: {e}")
            return None

# 글로벌 인스턴스
distiller = NeuralDistiller()
