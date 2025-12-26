import subprocess
import logging
import time
import psutil
from typing import Dict, Any

logger = logging.getLogger("GortexInfra")

class InfraManager:
    """
    Gortex 군집의 물리적/가상 인프라를 관리함.
    워커 프로세스 생성, 리소스 감시, 자동 확장을 담당합니다.
    """
    def __init__(self):
        self.active_workers = []
        self.worker_script = "scripts/gortex_worker.py"

    def spawn_local_worker(self) -> Dict[str, Any]:
        """새로운 로컬 워커 프로세스를 가동함"""
        try:
            # 백그라운드 프로세스로 실행
            process = subprocess.Popen(
                [ "python3", self.worker_script ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            worker_info = {
                "pid": process.pid,
                "type": "local",
                "started_at": time.time()
            }
            self.active_workers.append(worker_info)
            logger.info(f"🏗️ Spawned new local worker: PID {process.pid}")
            return {"status": "success", "info": worker_info}
        except Exception as e:
            logger.error(f"Failed to spawn worker: {e}")
            return {"status": "failed", "error": str(e)}

    def check_cluster_load(self) -> Dict[str, float]:
        """전체 군집의 평균 부하를 계산함"""
        from gortex.core.mq import mq_bus
        workers = mq_bus.list_active_workers()
        if not workers:
            return {"avg_cpu": 0.0, "count": 0}
            
        total_cpu = sum(w.get("cpu_percent", 0) for w in workers)
        return {
            "avg_cpu": total_cpu / len(workers),
            "count": len(workers)
        }

    def shutdown_worker(self, pid: int):
        """특정 워커 프로세스 종료"""
        try:
            p = psutil.Process(pid)
            p.terminate()
            logger.info(f"🛑 Terminated worker PID {pid}")
            return True
        except:
            return False

# 글로벌 인스턴스
infra = InfraManager()
