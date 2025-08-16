#!/usr/bin/env python3
"""
OWID RAG 인덱스 사전 빌드 스크립트
한 번만 실행하면 이후에는 빠르게 로드 가능
"""

from app.services.tools.owid_enhanced_rag import EnhancedOWIDRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_index():
    """인덱스 빌드 및 저장"""
    logger.info("🏗️ Building OWID RAG Index...")
    logger.info("This will take about 30-40 seconds but only needs to be done once.")
    
    rag = EnhancedOWIDRAG()
    
    # 강제로 재빌드
    rag.build_enhanced_index(force_rebuild=True)
    
    # 테스트 쿼리로 확인
    test_results = rag.search("Korea CO2", n_results=1)
    if test_results:
        logger.info("✅ Index built successfully!")
        logger.info(f"   Total chunks: {rag.collection.count()}")
        logger.info("   Index is saved and ready for use.")
    else:
        logger.error("❌ Index build failed")
        return False
    
    return True

if __name__ == "__main__":
    build_index()