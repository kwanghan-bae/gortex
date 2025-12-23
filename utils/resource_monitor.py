import os
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger("GortexResourceMonitor")

class ResourceMonitor:
    """시스템 자원 및 작업 부하를 실시간 모니터링함."""
    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def get_system_stats(self) -> Dict[str, Any]:
        """CPU, Memory 등 하드웨어 자원 상태 반환"""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_usage,
            "memory_percent": memory_info.percent,
            "memory_available_mb": memory_info.available / (1024 * 1024),
            "process_memory_mb": self.process.memory_info().rss / (1024 * 1024)
        }

    def get_load_level(self) -> str:
        """현재 시스템 부하 수준을 3단계로 판별"""
        stats = self.get_system_stats()
        cpu = stats["cpu_percent"]
        mem = stats["memory_percent"]
        
        if cpu > 80 or mem > 90:
            return "CRITICAL"
        elif cpu > 50 or mem > 70:
            return "MODERATE"
        return "LIGHT"

    def estimate_concurrency_limit(self, base_limit: int = 2) -> int:
        """자원 상태에 따른 권장 동시 실행 수 계산"""
        load = self.get_load_level()
        if load == "CRITICAL":
            return 1
        elif load == "LIGHT":
            return base_limit * 2
        return base_limit