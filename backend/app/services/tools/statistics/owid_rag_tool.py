"""
OWID RAG Tool - Final Production Version
Enhanced RAG with Multilingual Support + Hybrid Search + Reranking
38개 OWID 데이터셋 기반 통계 검색 도구
"""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from pathlib import Path
import logging
import json
import os

# Import the enhanced RAG system
from .owid_enhanced_rag import EnhancedOWIDRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OWIDRAGToolInput(BaseModel):
    """OWID RAG Tool 입력 스키마"""
    query: str = Field(
        description="Search query for OWID statistics (Korean or English)"
    )
    n_results: int = Field(
        default=5,
        description="Number of results to return (1-10)"
    )
    use_reranker: bool = Field(
        default=True,
        description="Whether to use cross-encoder reranking for better accuracy"
    )


class OWIDRAGTool(BaseTool):
    """
    OWID Statistics RAG Search Tool
    
    Features:
    - Multilingual embeddings (Korean + English)
    - Hybrid search (Vector + BM25)
    - Cross-encoder reranking
    - Statistical data-optimized chunking
    - 38 real OWID datasets
    
    Available categories:
    - Climate & Environment (16 datasets): CO2, temperature, renewable energy, etc.
    - Health (10 datasets): life expectancy, COVID-19, mortality, etc.
    - Economy (4 datasets): GDP, poverty, trade, financial inclusion
    - Society (5 datasets): population, education, mobile phones, etc.
    - Others (3 datasets): government effectiveness, voice accountability, etc.
    """
    
    name: str = "OWID_Statistics_Search"
    description: str = """
    Search Our World in Data statistics using natural language queries.
    Supports both Korean and English queries.
    
    Example queries:
    - "한국의 CO2 배출량 추세"
    - "renewable energy adoption rates"
    - "COVID-19 vaccination statistics"
    - "최신 GDP 성장률 데이터"
    - "global temperature anomaly trends"
    
    Returns relevant statistical data with metadata about dataset, type, and confidence scores.
    """
    
    args_schema: Type[BaseModel] = OWIDRAGToolInput
    rag_system: Optional[EnhancedOWIDRAG] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rag_system = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize the Enhanced RAG system"""
        try:
            logger.info("Initializing OWID Enhanced RAG System...")
            
            # Check if required packages are installed
            try:
                import chromadb
                from sentence_transformers import SentenceTransformer
                from rank_bm25 import BM25Okapi
            except ImportError as e:
                logger.error(f"Missing required package: {e}")
                logger.error("Install with: uv pip install chromadb sentence-transformers rank-bm25")
                return
            
            # Initialize the RAG system
            self.rag_system = EnhancedOWIDRAG(
                data_dir="./owid_datasets",
                db_path="./owid_enhanced_vectordb"
            )
            
            # Build index if needed
            if self.rag_system.collection:
                existing_count = self.rag_system.collection.count()
                if existing_count == 0:
                    logger.info("Building index for first time use...")
                    self.rag_system.build_enhanced_index(force_rebuild=False)
                else:
                    logger.info(f"Using existing index with {existing_count} chunks")
                    # Build BM25 index (in-memory)
                    self.rag_system._build_bm25_index()
            
            logger.info("✅ OWID RAG System ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.rag_system = None
    
    def _run(self, query: str, n_results: int = 5, use_reranker: bool = True) -> str:
        """
        Search OWID statistics
        
        Args:
            query: Search query in Korean or English
            n_results: Number of results (1-10)
            use_reranker: Whether to use reranking for better accuracy
            
        Returns:
            Formatted search results with statistics
        """
        
        if not self.rag_system:
            return "Error: RAG system not initialized. Please check installation."
        
        # Validate n_results
        n_results = max(1, min(10, n_results))
        
        try:
            # Perform search
            results = self.rag_system.search(
                query=query,
                n_results=n_results,
                use_reranker=use_reranker
            )
            
            if not results:
                return f"No results found for: {query}"
            
            # Format results
            output = self._format_results(query, results)
            return output
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Error performing search: {str(e)}"
    
    def _format_results(self, query: str, results: List[Dict]) -> str:
        """구조화된 OWID 출력 형식 - 모든 메타데이터 있는 그대로 전달"""
        
        result_lines = []
        result_lines.append(f"📊 OWID 통계 검색 결과: '{query}'")
        result_lines.append("━" * 60)
        result_lines.append("📌 출처: Our World in Data")
        result_lines.append(f"📊 발견된 결과: {len(results)}개\n")
        
        for i, result in enumerate(results, 1):
            result_lines.append(f"📈 [{i}] OWID 데이터")
            result_lines.append("─" * 40)
            
            # 모든 메타데이터를 있는 그대로 표시
            result_lines.append("📁 검색 결과 메타데이터:")
            for key, value in result.items():
                if value is not None and str(value).strip():
                    # 중첩된 객체 처리
                    if isinstance(value, dict):
                        result_lines.append(f"  - {key}:")
                        for sub_key, sub_value in value.items():
                            if sub_value is not None:
                                result_lines.append(f"    {sub_key}: {sub_value}")
                    else:
                        result_lines.append(f"  - {key}: {value}")
            
            # 콘텐츠 전체를 있는 그대로 표시
            content = result.get('content', '')
            if content:
                result_lines.append("\n📊 원본 데이터:")
                # 콘텐츠를 줄 단위로 나누어 표시
                for line in content.split('\n'):
                    if line.strip():
                        result_lines.append(f"  {line.strip()}")
            
            result_lines.append("")
        
        return "\n".join(result_lines)
    
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available datasets"""
        if not self.rag_system:
            return []
        
        return [d['id'] for d in self.rag_system.datasets]
    
    def get_dataset_info(self, dataset_id: str) -> Optional[Dict]:
        """Get detailed information about a specific dataset"""
        if not self.rag_system:
            return None
        
        for dataset in self.rag_system.datasets:
            if dataset['id'] == dataset_id:
                return {
                    'id': dataset['id'],
                    'csv_path': str(dataset['csv_path']),
                    'has_readme': dataset.get('readme_path') is not None,
                    'has_metadata': dataset.get('metadata_path') is not None
                }
        return None


# Quick test function
def test_owid_rag_tool():
    """Test the OWID RAG Tool"""
    
    print("Testing OWID RAG Tool...")
    tool = OWIDRAGTool()
    
    # Test queries
    test_queries = [
        ("한국의 재생에너지 비율", 3, True),
        ("COVID-19 mortality rates", 3, False),
        ("global GDP growth trends", 3, True)
    ]
    
    for query, n_results, use_reranker in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Settings: n_results={n_results}, reranker={use_reranker}")
        print('='*60)
        
        result = tool._run(query, n_results, use_reranker)
        print(result)
    
    # Show available datasets
    datasets = tool.get_available_datasets()
    print(f"\n📚 Available datasets: {len(datasets)}")
    print(f"Sample: {datasets[:5]}")


if __name__ == "__main__":
    test_owid_rag_tool()