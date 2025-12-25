
import asyncio
import logging
import sys
import os
import shutil

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SanityCheck")

# Gortex 모듈 임포트
try:
    from gortex.core.engine import GortexEngine
    from gortex.core.state import GortexState
    from gortex.core.config import GortexConfig
    from gortex.core.persistence import DistributedSaver
except ImportError as e:
    logger.error(f"❌ Failed to import Gortex modules: {e}")
    sys.exit(1)

async def main():
    logger.info("🏥 Starting Gortex Sanity Check...")
    
    # 1. 환경 준비 (Clean State)
    test_mirror_path = "logs/sanity_mirror.json"
    if os.path.exists(test_mirror_path):
        os.remove(test_mirror_path)
        
    # 2. Config 검증
    try:
        config = GortexConfig()
        logger.info("✅ GortexConfig loaded successfully.")
    except Exception as e:
        logger.error(f"❌ GortexConfig failed: {e}")
        sys.exit(1)
        
    # 3. Engine 초기화
    try:
        # Mock UI & Observer (Sanity Check는 헤드리스 실행)
        engine = GortexEngine(ui=None, observer=None)
        logger.info("✅ GortexEngine initialized.")
    except Exception as e:
        logger.error(f"❌ Engine initialization failed: {e}")
        sys.exit(1)
        
    # 4. Persistence 검증
    try:
        saver = DistributedSaver(mirror_path=test_mirror_path)
        dummy_state = {"messages": [], "config": {"test": "ok"}} # ChainMap 대응 확인
        saver._replicate({"th": "1"}, dummy_state, {})
        
        if os.path.exists(test_mirror_path):
            logger.info("✅ Persistence layer is WRITING correctly.")
        else:
            logger.error("❌ Persistence check failed: Mirror file not created.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Persistence check crashed: {e}")
        sys.exit(1)
        
    # 5. Graph Compilation Check (정적 분석)
    if engine.graph:
        logger.info("✅ Agent Graph compiled successfully.")
    else:
        logger.error("❌ Agent Graph is empty.")
        sys.exit(1)
        
    logger.info("🎉 SANITY CHECK PASSED! System is healthy and ready to boot.")
    
    # Clean up
    if os.path.exists(test_mirror_path):
        os.remove(test_mirror_path)

if __name__ == "__main__":
    asyncio.run(main())
