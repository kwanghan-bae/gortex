import json
import os
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger("GortexTrainer")

class GortexTrainer:
    """
    에이전트 전용 소형 모델(SLM)의 학습 과정을 관리함.
    데이터셋 검증, 학습 잡 예약, 모델 배포를 담당합니다.
    """
    def __init__(self):
        self.jobs_dir = "training_jobs"
        self.models_dir = "models/custom"
        os.makedirs(self.jobs_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

    def create_training_job(self, dataset_path: str, base_model: str = "qwen2.5-coder:7b") -> str:
        """새로운 학습 잡을 생성하고 ID를 반환함."""
        job_id = f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        job_dir = os.path.join(self.jobs_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        job_config = {
            "job_id": job_id,
            "status": "pending",
            "dataset": dataset_path,
            "base_model": base_model,
            "created_at": datetime.now().isoformat(),
            "metrics": {}
        }
        
        config_path = os.path.join(job_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(job_config, f, indent=2)
            
        logger.info(f"🏗️ Created training job: {job_id} using {dataset_path}")
        return job_id

    def start_job(self, job_id: str):
        """학습 잡을 백그라운드에서 실행함 (시뮬레이션)."""
        job_dir = os.path.join(self.jobs_dir, job_id)
        config_path = os.path.join(job_dir, "config.json")
        
        if not os.path.exists(config_path):
            return False
            
        with open(config_path, "r") as f:
            config = json.load(f)
            
        config["status"] = "running"
        config["started_at"] = datetime.now().isoformat()
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"🚀 Training started for {job_id}...")
        
        # [SIMULATION] 실제 환경에서는 여기에 fine-tuning 스크립트 실행 로직이 들어감
        # 예: subprocess.Popen(["python3", "scripts/finetune.py", "--config", config_path])
        # 데모를 위해 5초 후 완료 처리하는 코루틴처럼 동작하도록 설계
        return True

    def check_status(self, job_id: str) -> Dict[str, Any]:
        """잡의 진행 상태와 결과 모델 경로를 반환함."""
        path = os.path.join(self.jobs_dir, job_id, "config.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {"status": "not_found"}

    def register_custom_model(self, job_id: str, agent_name: str):
        """학습이 완료된 모델을 특정 에이전트의 전용 모델로 등록함."""
        status = self.check_status(job_id)
        if status.get("status") == "completed":
            model_name = f"gortex-{agent_name.lower()}-{job_id}"
            # GortexAuth에 사용자 정의 모델 힌트 추가 (Ollama 등에 로드 가능하도록)
            from gortex.core.auth import GortexAuth
            auth = GortexAuth()
            # OLLAMA_ROLE_MAP에 우선순위로 추가
            if agent_name.lower() in auth.OLLAMA_ROLE_MAP:
                auth.OLLAMA_ROLE_MAP[agent_name.lower()].insert(0, model_name)
                logger.info(f"🎓 Custom model '{model_name}' registered for agent '{agent_name}'.")
                return True
        return False

# 글로벌 인스턴스
trainer = GortexTrainer()
