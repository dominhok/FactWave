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
        """Format search results for display"""
        
        output = f"🔍 OWID Statistics Search: '{query}'\n"
        output += "=" * 60 + "\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"📊 Result {i}:\n"
            output += f"  Dataset: {result.get('dataset_id', 'Unknown')}\n"
            output += f"  Type: {result.get('chunk_type', 'Unknown')}\n"
            
            # Add metadata if available
            metadata = result.get('metadata', {})
            if metadata.get('year'):
                output += f"  Year: {metadata['year']}\n"
            if metadata.get('country'):
                output += f"  Country: {metadata['country']}\n"
            
            # Confidence score
            score = result.get('score', 0)
            if score > 0:
                output += f"  Confidence: {self._score_to_confidence(score)}\n"
            
            # Content preview
            content = result.get('content', '')
            # Extract key statistics from content
            stats = self._extract_key_stats(content)
            if stats:
                output += f"  Key Stats:\n"
                for stat in stats[:3]:  # Show top 3 stats
                    output += f"    • {stat}\n"
            
            output += "\n"
        
        # Add summary
        output += self._add_search_summary(results)
        
        return output
    
    def _score_to_confidence(self, score: float) -> str:
        """Convert score to confidence level"""
        if score > 5:
            return "⭐⭐⭐⭐⭐ Very High"
        elif score > 3:
            return "⭐⭐⭐⭐ High"
        elif score > 1:
            return "⭐⭐⭐ Medium"
        elif score > 0:
            return "⭐⭐ Low"
        else:
            return "⭐ Very Low"
    
    def _extract_key_stats(self, content: str) -> List[str]:
        """Extract key statistics from content"""
        stats = []
        
        # Look for patterns like "- Latest: X", "Average: Y", etc.
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- ') and ':' in line:
                stats.append(line[2:])  # Remove "- " prefix
            elif 'Latest' in line or 'Average' in line or 'Mean' in line:
                if ':' in line:
                    stats.append(line.split(':', 1)[1].strip())
        
        return stats
    
    def _add_search_summary(self, results: List[Dict]) -> str:
        """Add summary of search results"""
        
        # Count datasets and types
        datasets = set()
        types = set()
        for result in results:
            datasets.add(result.get('dataset_id', ''))
            types.add(result.get('chunk_type', ''))
        
        summary = "📈 Summary:\n"
        summary += f"  Found data from {len(datasets)} dataset(s)\n"
        summary += f"  Data types: {', '.join(types)}\n"
        
        # Suggest related searches based on results
        if any('korea' in r.get('chunk_type', '') for r in results):
            summary += "  💡 Tip: Found Korea-specific data\n"
        if any('trend' in r.get('chunk_type', '') for r in results):
            summary += "  💡 Tip: Time-series trends available\n"
        
        return summary
    
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