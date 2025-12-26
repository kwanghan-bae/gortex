import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger("GortexHardware")

class HardwareSensor:
    """
    시스템의 물리적 상태(온도, 전력, 배터리)를 감시함.
    에너지 효율적인 지능 가동 정책의 기초 데이터를 제공합니다.
    """
    def __init__(self):
        self.battery_supported = hasattr(psutil, "sensors_battery")

    def get_system_vitals(self) -> Dict[str, Any]:
        """CPU 온도 및 배터리 상태 획득"""
        vitals = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
            "is_charging": True,
            "battery_percent": 100,
            "thermal_status": "nominal" # nominal, warning, critical
        }
        
        # 1. 배터리 정보
        if self.battery_supported:
            battery = psutil.sensors_battery()
            if battery:
                vitals["battery_percent"] = battery.percent
                vitals["is_charging"] = battery.power_plugged
        
        # 2. 온도 정보 (macOS/Linux 차이 고려)
        # (간소화된 구현: CPU 사용량 기반 추정 또는 센서 API 활용)
        if vitals["cpu_percent"] > 80:
            vitals["thermal_status"] = "warning"
        if vitals["cpu_percent"] > 95:
            vitals["thermal_status"] = "critical"
            
        return vitals

    def get_eco_multiplier(self) -> float:
        """현재 시스템 컨디션에 따른 에너지 보존 계수 산출 (0.0 ~ 1.0)"""
        vitals = self.get_system_vitals()
        multiplier = 1.0
        
        # 배터리 모드 시 페널티
        if not vitals["is_charging"]:
            multiplier *= 0.7
            if vitals["battery_percent"] < 20: multiplier *= 0.5
            
        # 발열 시 페널티
        if vitals["thermal_status"] == "warning": multiplier *= 0.8
        elif vitals["thermal_status"] == "critical": multiplier *= 0.4
        
        return round(multiplier, 2)

# 글로벌 인스턴스
sensor = HardwareSensor()
