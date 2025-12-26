import os
import hashlib
import json
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger("GortexIntegrity")

class IntegrityGuard:
    """
    Gortex 시스템의 소스 코드 무결성을 수호하는 보안 모듈.
    파일 해시 서명을 관리하고 승인되지 않은 변경을 감지합니다.
    """
    def __init__(self, signature_path: str = "logs/system_signature.json"):
        self.signature_path = signature_path
        self.core_dirs = ["core", "agents", "utils", "ui"]
        self.ignore_patterns = ["__pycache__", ".pyc", ".tmp", ".bak"]

    def _calculate_hash(self, file_path: str) -> str:
        """파일의 SHA-256 해시 계산"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_master_signature(self) -> Dict[str, str]:
        """현재 시스템 상태를 '정상 상태'로 기록한 마스터 서명 생성"""
        signature = {}
        for d in self.core_dirs:
            for root, _, files in os.walk(d):
                for f in files:
                    if any(p in f for p in self.ignore_patterns): continue
                    if not f.endswith(".py"): continue
                    
                    path = os.path.join(root, f)
                    signature[path] = self._calculate_hash(path)
        
        os.makedirs(os.path.dirname(self.signature_path), exist_ok=True)
        with open(self.signature_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "files": signature
            }, f, indent=2)
            
        logger.info(f"🛡️ Master System Signature generated at {self.signature_path}")
        return signature

    def check_integrity(self) -> Tuple[List[str], List[str]]:
        """마스터 서명과 현재 상태를 비교하여 변경/삭제된 파일 식별"""
        if not os.path.exists(self.signature_path):
            return [], []

        with open(self.signature_path, "r", encoding="utf-8") as f:
            master = json.load(f)["files"]

        modified = []
        deleted = []
        
        # 1. 기존 파일 검사
        for path, old_hash in master.items():
            if not os.path.exists(path):
                deleted.append(path)
                continue
            
            new_hash = self._calculate_hash(path)
            if old_hash != new_hash:
                modified.append(path)
                
        return modified, deleted

# 글로벌 인스턴스
guard = IntegrityGuard()
