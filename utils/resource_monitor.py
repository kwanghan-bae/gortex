import os
import logging
import time
from typing import Dict, Any

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger("GortexResourceMonitor")

class ResourceMonitor:
    """
    시스템 및 프로세스 리소스 사용량을 측정하는 모니터링 도구.
    """
    def __init__(self):
        self.process = psutil.Process(os.getpid()) if psutil else None

    def get_stats(self) -> Dict[str, Any]:
        """현재 리소스 사용량 스냅샷 반환"""
        if not psutil:
            return {"error": "psutil not installed"}
            
        try:
            # 시스템 전체
            cpu_total = psutil.cpu_percent(interval=None)
            mem_total = psutil.virtual_memory().percent
            
            # 현재 Gortex 프로세스
            cpu_proc = self.process.cpu_percent(interval=None)
            mem_proc = self.process.memory_info().rss / (1024 * 1024) # MB
            
            return {
                "cpu_total": cpu_total,
                "mem_total": mem_total,
                "cpu_proc": cpu_proc,
                "mem_proc_mb": round(mem_proc, 2),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get resource stats: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    monitor = ResourceMonitor()
    while True:
        print(monitor.get_stats())
        time.sleep(1)
