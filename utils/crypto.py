import os
import logging
import base64
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    Fernet = None

logger = logging.getLogger("GortexCrypto")

class GortexCrypto:
    """
    민감한 데이터를 안전하게 암호화하고 복호화하는 보안 유틸리티.
    """
    def __init__(self, key: Optional[str] = None):
        self.fernet = None
        if not Fernet:
            logger.warning("cryptography library not installed. Crypto functions will be disabled.")
            return
            
        # 키가 없으면 환경 변수 또는 고정 솔트 기반 생성
        if not key:
            key = os.getenv("GORTEX_MASTER_KEY", "default-secret-salt-12345")
            
        # PBKDF2를 사용하여 마스터 키로부터 암호화 키 생성
        salt = b'gortex_security_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        final_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
        self.fernet = Fernet(final_key)

    def encrypt(self, data: str) -> str:
        """텍스트 암호화"""
        if not self.fernet:
            return data
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """텍스트 복호화"""
        if not self.fernet:
            return encrypted_data
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data

if __name__ == "__main__":
    crypto = GortexCrypto()
    secret = "My API Key 12345"
    enc = crypto.encrypt(secret)
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {crypto.decrypt(enc)}")
