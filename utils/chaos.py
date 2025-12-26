import os
import random
import logging
import shutil
from typing import Dict, Any

logger = logging.getLogger("GortexChaos")

class ChaosEngine:
    """
    Gortex 시스템의 강건함을 테스트하기 위해 
    인위적인 결함을 주입하는 카오스 엔지니어링 모듈.
    """
    def __init__(self):
        self.targets = ["gortex/utils/tools.py", "gortex/core/state.py", "cli.py"]

    def inject_random_fault(self) -> Dict[str, Any]:
        """임의의 결함을 주입함"""
        fault_type = random.choice(["file_corruption", "directory_lock", "process_stress"])
        
        if fault_type == "file_corruption":
            target = random.choice(self.targets)
            if os.path.exists(target):
                # 백업 후 일부 내용 삭제 시뮬레이션
                shutil.copy2(target, f"{target}.corrupted.bak")
                with open(target, "a") as f:
                    f.write("\n# CHAOS_INJECTION: SyntaxError intentional\nimport invalid_module_chaos\n")
                logger.critical(f"🔥 [Chaos] Injected file corruption into {target}")
                return {"type": "file_corruption", "target": target}
                
        elif fault_type == "directory_lock":
            lock_dir = "logs/chaos_lock"
            os.makedirs(lock_dir, exist_ok=True)
            # 권한 박탈 시뮬레이션 (현재는 폴더 생성으로 대체)
            logger.critical(f"🔥 [Chaos] Injected directory lock: {lock_dir}")
            return {"type": "directory_lock", "target": lock_dir}
            
        return {"type": "none", "target": "none"}

# 글로벌 인스턴스
chaos = ChaosEngine()
