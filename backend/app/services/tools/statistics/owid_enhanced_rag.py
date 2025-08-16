"""
Enhanced OWID RAG System - Production-Ready Implementation
Multilingual embeddings + Hybrid search + Reranking
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
import hashlib
from collections import defaultdict
import re

# Vector DB imports
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False
    print("ChromaDB not installed. Install with: pip install chromadb")

# Enhanced embeddings
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    print("sentence-transformers not installed")

# BM25 for hybrid search
try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False
    print("rank-bm25 not installed. Install with: pip install rank-bm25")

# Text processing
try:
    from konlpy.tag import Okt
    HAS_KONLPY = True
    okt = Okt()
except ImportError:
    HAS_KONLPY = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """검색 결과 데이터 클래스"""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str
    dataset_id: str
    chunk_type: str


class EnhancedOWIDRAG:
    """향상된 OWID RAG 시스템"""
    
    def __init__(self, data_dir: str = "./owid_datasets", db_path: str = "./owid_enhanced_vectordb"):
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        self._initialize_models()
        
        self.bm25_index = None
        self.bm25_documents = []
        self.bm25_metadata = []
        
        self._initialize_chromadb()
        self.datasets = self._load_datasets()
        
        self.cache = {}
        self.cache_size = 100
    
    def _initialize_models(self):
        """모델 초기화"""
        if HAS_SENTENCE_TRANSFORMERS:
            logger.info("Initializing enhanced models...")
            
            self.encoder = SentenceTransformer('intfloat/multilingual-e5-base')
            logger.info("✅ Loaded multilingual-e5-base (768d embeddings)")
            
            # Cross-encoder for reranking
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            logger.info("✅ Loaded cross-encoder reranker")
        else:
            logger.error("sentence-transformers not available")
            self.encoder = None
            self.reranker = None
    
    def _initialize_chromadb(self):
        """ChromaDB 초기화"""
        if HAS_CHROMADB and self.encoder:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            class E5EmbeddingFunction:
                def __init__(self, encoder):
                    self.encoder = encoder
                
                def __call__(self, texts: List[str]) -> List[List[float]]:
                    embeddings = self.encoder.encode(
                        ["query: " + text for text in texts],
                        normalize_embeddings=True
                    )
                    return embeddings.tolist()
            
            self.embedding_function = E5EmbeddingFunction(self.encoder)
            
            try:
                # 기존 컬렉션 사용 시도
                self.collection = self.chroma_client.get_collection("owid_enhanced")
                logger.info(f"✅ Using existing ChromaDB collection with {self.collection.count()} chunks")
            except:
                # 없으면 새로 생성
                self.collection = self.chroma_client.create_collection(
                    name="owid_enhanced",
                    metadata={"description": "Enhanced OWID with multilingual support"}
                )
                logger.info("✅ ChromaDB collection created")
    
    def _load_datasets(self) -> List[Dict]:
        """데이터셋 로드"""
        datasets = []
        
        for folder in sorted(self.data_dir.iterdir()):
            if not folder.is_dir():
                continue
            
            csv_files = list(folder.glob("*.csv"))
            if not csv_files:
                continue
            
            dataset_info = {
                "id": folder.name,
                "csv_path": csv_files[0],
                "readme_path": next(folder.glob("*readme.md"), None),
                "metadata_path": next(folder.glob("*.metadata.json"), None)
            }
            datasets.append(dataset_info)
        
        logger.info(f"Loaded {len(datasets)} datasets")
        return datasets
    
    def build_enhanced_index(self, force_rebuild: bool = False):
        """향상된 인덱스 구축"""
        if not force_rebuild and self.collection.count() > 0:
            logger.info(f"Index exists with {self.collection.count()} chunks")
            self._build_bm25_index()
            return
        
        logger.info("Building enhanced index...")
        
        all_chunks = []
        all_metadata = []
        all_texts_for_bm25 = []
        
        for dataset in self.datasets:
            logger.info(f"Processing {dataset['id']}...")
            
            chunks = self._create_smart_chunks(dataset)
            
            for chunk in chunks:
                all_chunks.append(chunk.content)
                all_metadata.append({
                    "dataset_id": chunk.dataset_id,
                    "chunk_type": chunk.chunk_type,
                    **chunk.metadata
                })
                
                processed_text = self._preprocess_for_bm25(chunk.content)
                all_texts_for_bm25.append(processed_text)
        
        if self.collection:
            batch_size = 50
            for i in range(0, len(all_chunks), batch_size):
                batch_end = min(i + batch_size, len(all_chunks))
                
                embeddings = self.encoder.encode(
                    ["passage: " + text for text in all_chunks[i:batch_end]],
                    normalize_embeddings=True
                )
                
                ids = []
                for j, (text, metadata) in enumerate(zip(all_chunks[i:batch_end], all_metadata[i:batch_end])):
                    unique_string = f"{i+j}_{metadata.get('dataset_id', '')}_{metadata.get('chunk_type', '')}_{text[:30]}"
                    ids.append(hashlib.md5(unique_string.encode()).hexdigest())
                
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    documents=all_chunks[i:batch_end],
                    metadatas=all_metadata[i:batch_end],
                    ids=ids
                )
                logger.info(f"Added {batch_end}/{len(all_chunks)} to vector index")
        
        self.bm25_documents = all_chunks
        self.bm25_metadata = all_metadata
        self._build_bm25_index()
        
        logger.info(f"✅ Enhanced index built: {len(all_chunks)} chunks")
    
    def _create_smart_chunks(self, dataset: Dict) -> List[SearchResult]:
        """통계 데이터에 최적화된 스마트 청킹 - 모든 국가 포함"""
        chunks = []
        dataset_id = dataset['id']
        
        # 1. Overview chunk (README 기반)
        if dataset['readme_path'] and dataset['readme_path'].exists():
            try:
                readme = dataset['readme_path'].read_text(encoding='utf-8')
                
                korean_keywords = self._get_korean_keywords(dataset_id)
                
                overview = f"""
Dataset: {dataset_id}
Description: {readme[:500]}
Korean Keywords: {korean_keywords}
Related Terms: {self._get_related_terms(dataset_id)}
"""
                chunks.append(SearchResult(
                    content=overview,
                    metadata={"lang": "multi"},
                    score=0.0,
                    source="index",
                    dataset_id=dataset_id,
                    chunk_type="overview"
                ))
            except:
                pass
        
        # 2. Statistical chunks (CSV 데이터 기반)
        try:
            df = pd.read_csv(dataset['csv_path'], nrows=5000)
            
            # 시계열 트렌드 청크
            if 'Year' in df.columns:
                trend_chunk = self._create_trend_chunk(df, dataset_id)
                if trend_chunk:
                    chunks.append(trend_chunk)
            
            country_chunks = self._create_country_chunks(df, dataset_id)
            chunks.extend(country_chunks)
            
            latest_chunk = self._create_latest_data_chunk(df, dataset_id)
            if latest_chunk:
                chunks.append(latest_chunk)
            
            stats_chunk = self._create_statistics_summary_chunk(df, dataset_id)
            if stats_chunk:
                chunks.append(stats_chunk)
                
        except Exception as e:
            logger.warning(f"Error processing {dataset_id}: {e}")
        
        return chunks
    
    def _create_trend_chunk(self, df: pd.DataFrame, dataset_id: str) -> Optional[SearchResult]:
        """시계열 트렌드 분석 청크"""
        if 'Year' not in df.columns:
            return None
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        main_indicator = [col for col in numeric_cols if col != 'Year'][0] if len(numeric_cols) > 1 else None
        
        if not main_indicator:
            return None
        
        yearly_avg = df.groupby('Year')[main_indicator].mean()
        
        content = f"""
Dataset: {dataset_id}
Indicator: {main_indicator}
Time Range: {df['Year'].min()}-{df['Year'].max()}
Trend Analysis:
- Starting Value ({df['Year'].min()}): {yearly_avg.iloc[0]:.2f}
- Ending Value ({df['Year'].max()}): {yearly_avg.iloc[-1]:.2f}
- Change: {((yearly_avg.iloc[-1] / yearly_avg.iloc[0] - 1) * 100):.1f}%
- Average Annual Growth: {((yearly_avg.pct_change().mean()) * 100):.2f}%
Keywords: trend, time series, growth rate, 추세, 시계열, 성장률
"""
        
        return SearchResult(
            content=content,
            metadata={"year_range": f"{df['Year'].min()}-{df['Year'].max()}"},
            score=0.0,
            source="index",
            dataset_id=dataset_id,
            chunk_type="trend"
        )
    
    def _create_country_chunks(self, df: pd.DataFrame, dataset_id: str) -> List[SearchResult]:
        """모든 국가 데이터를 포함하는 청크 생성"""
        chunks = []
        
        country_col = None
        for col in ['Entity', 'Country', 'Location']:
            if col in df.columns:
                country_col = col
                break
        
        if not country_col:
            return chunks
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        indicators = [col for col in numeric_cols if col not in ['Year', 'Code']]
        if not indicators:
            return chunks
        
        main_indicator = indicators[0]
        
        countries_data = {}
        unique_countries = df[country_col].unique()
        
        MAX_COUNTRIES_PER_CHUNK = 100
        if len(unique_countries) > MAX_COUNTRIES_PER_CHUNK:
            if 'Year' in df.columns:
                latest_year = df['Year'].max()
                latest_df = df[df['Year'] == latest_year]
                top_countries = latest_df.nlargest(MAX_COUNTRIES_PER_CHUNK, main_indicator)[country_col].tolist()
            else:
                top_countries = unique_countries[:MAX_COUNTRIES_PER_CHUNK]
            
            logger.info(f"{dataset_id}: {len(unique_countries)} countries found, using top {MAX_COUNTRIES_PER_CHUNK}")
        else:
            top_countries = unique_countries.tolist()
        
        for country in top_countries:
            country_data = df[df[country_col] == country]
            if not country_data.empty:
                if 'Year' in df.columns:
                    latest = country_data.iloc[-1]
                    countries_data[country] = {
                        'value': float(latest[main_indicator]) if pd.notna(latest[main_indicator]) else None,
                        'year': int(latest['Year'])
                    }
                else:
                    latest = country_data.iloc[-1]
                    countries_data[country] = {
                        'value': float(latest[main_indicator]) if pd.notna(latest[main_indicator]) else None
                    }
        
        content = f"""
Dataset: {dataset_id}
Indicator: {main_indicator}
Countries Coverage: {len(countries_data)} countries
Country Data:
"""
        sorted_countries = sorted(countries_data.items(), 
                                key=lambda x: x[1].get('value', 0) if x[1].get('value') else 0, 
                                reverse=True)
        
        for country, data in sorted_countries[:20]:
            if data.get('value') is not None:
                content += f"- {country}: {data['value']:.2f}"
                if 'year' in data:
                    content += f" ({data['year']})"
                content += "\n"
        
        all_country_names = ', '.join(top_countries[:50])
        content += f"\nAll Countries: {all_country_names[:500]}..."
        
        chunks.append(SearchResult(
            content=content,
            metadata={
                "countries_count": len(countries_data),
                "has_all_countries": True
            },
            score=0.0,
            source="index",
            dataset_id=dataset_id,
            chunk_type="countries"
        ))
        
        # 2. Regional Chunks (대륙별 청크)
        regions = {
            'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Thailand', 'Vietnam', 
                    'Philippines', 'Malaysia', 'Singapore', 'Bangladesh', 'Pakistan'],
            'Europe': ['Germany', 'France', 'United Kingdom', 'Italy', 'Spain', 'Netherlands', 
                      'Belgium', 'Sweden', 'Poland', 'Austria', 'Switzerland', 'Norway'],
            'Americas': ['United States', 'Canada', 'Brazil', 'Mexico', 'Argentina', 'Colombia', 
                        'Chile', 'Peru', 'Venezuela', 'Ecuador'],
            'Africa': ['Nigeria', 'Egypt', 'South Africa', 'Kenya', 'Ethiopia', 'Ghana', 
                      'Morocco', 'Algeria', 'Tunisia', 'Uganda'],
            'Oceania': ['Australia', 'New Zealand', 'Papua New Guinea', 'Fiji']
        }
        
        for region_name, region_countries in regions.items():
            region_df = df[df[country_col].isin(region_countries)]
            if not region_df.empty:
                region_content = f"""
Dataset: {dataset_id}
Region: {region_name}
Indicator: {main_indicator}
Regional Statistics:
"""
                if main_indicator in region_df.columns:
                    values = region_df[main_indicator].dropna()
                    if len(values) > 0:
                        region_content += f"- Average: {values.mean():.2f}\n"
                        region_content += f"- Median: {values.median():.2f}\n"
                        region_content += f"- Countries with data: {region_df[country_col].nunique()}\n"
                        
                        if 'Year' in region_df.columns:
                            latest_year = region_df['Year'].max()
                            latest_regional = region_df[region_df['Year'] == latest_year]
                        else:
                            latest_regional = region_df
                        
                        top3 = latest_regional.nlargest(3, main_indicator)
                        region_content += f"\nTop 3 in {region_name}:\n"
                        for _, row in top3.iterrows():
                            region_content += f"- {row[country_col]}: {row[main_indicator]:.2f}\n"
                
                chunks.append(SearchResult(
                    content=region_content,
                    metadata={"region": region_name},
                    score=0.0,
                    source="index",
                    dataset_id=dataset_id,
                    chunk_type="regional"
                ))
        
        korea_chunk = self._create_korea_focused_chunk(df, dataset_id)
        if korea_chunk:
            chunks.append(korea_chunk)
        
        return chunks
    
    def _create_korea_focused_chunk(self, df: pd.DataFrame, dataset_id: str) -> Optional[SearchResult]:
        """한국 중심 데이터 청크"""
        country_col = None
        for col in ['Entity', 'Country', 'Location']:
            if col in df.columns:
                country_col = col
                break
        
        if not country_col:
            return None
        
        korea_names = ['South Korea', 'Korea, Republic of', 'Republic of Korea', 'Korea']
        korea_df = df[df[country_col].isin(korea_names)]
        
        if korea_df.empty:
            return None
        
        numeric_cols = korea_df.select_dtypes(include=[np.number]).columns
        indicators = [col for col in numeric_cols if col not in ['Year', 'Code']]
        
        content = f"""
Dataset: {dataset_id}
Country: South Korea (대한민국)
Data Points: {len(korea_df)}
"""
        
        for indicator in indicators[:3]:
            if indicator in korea_df.columns:
                values = korea_df[indicator].dropna()
                if len(values) > 0:
                    content += f"""
{indicator}:
- Latest: {values.iloc[-1]:.2f}
- Average: {values.mean():.2f}
- Min/Max: {values.min():.2f} / {values.max():.2f}
"""
        
        content += """
Keywords: Korea, South Korea, 한국, 대한민국, Korean statistics
"""
        
        return SearchResult(
            content=content,
            metadata={"country": "South Korea"},
            score=0.0,
            source="index",
            dataset_id=dataset_id,
            chunk_type="korea"
        )
    
    def _create_latest_data_chunk(self, df: pd.DataFrame, dataset_id: str) -> Optional[SearchResult]:
        """최신 데이터 청크"""
        if 'Year' in df.columns:
            latest_year = df['Year'].max()
            latest_df = df[df['Year'] == latest_year]
        else:
            latest_df = df.tail(100)
            latest_year = "Recent"
        
        if latest_df.empty:
            return None
        
        numeric_cols = latest_df.select_dtypes(include=[np.number]).columns
        main_indicator = [col for col in numeric_cols if col not in ['Year', 'Code']][0] if len(numeric_cols) > 0 else None
        
        if not main_indicator:
            return None
        
        content = f"""
Dataset: {dataset_id}
Latest Data ({latest_year}):
Indicator: {main_indicator}
- Countries/Entities: {len(latest_df)}
- Average: {latest_df[main_indicator].mean():.2f}
- Median: {latest_df[main_indicator].median():.2f}
- Std Dev: {latest_df[main_indicator].std():.2f}
"""
        
        country_col = None
        for col in ['Entity', 'Country', 'Location']:
            if col in df.columns:
                country_col = col
                break
        
        if country_col:
            top5 = latest_df.nlargest(5, main_indicator)
            content += f"\nTop 5 by {main_indicator}:\n"
            for _, row in top5.iterrows():
                content += f"- {row[country_col]}: {row[main_indicator]:.2f}\n"
        
        content += "\nKeywords: latest, recent, current, 최신, 현재"
        
        return SearchResult(
            content=content,
            metadata={"year": int(latest_year) if latest_year != "Recent" else 2024},
            score=0.0,
            source="index",
            dataset_id=dataset_id,
            chunk_type="latest"
        )
    
    def _create_statistics_summary_chunk(self, df: pd.DataFrame, dataset_id: str) -> Optional[SearchResult]:
        """전체 통계 요약 청크"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        indicators = [col for col in numeric_cols if col not in ['Year', 'Code']]
        
        if not indicators:
            return None
        
        content = f"""
Dataset: {dataset_id}
Statistical Summary:
Total Records: {len(df)}
"""
        
        for indicator in indicators[:3]:
            stats = df[indicator].describe()
            content += f"""
{indicator}:
- Mean: {stats['mean']:.2f}
- Median: {stats['50%']:.2f}
- Range: {stats['min']:.2f} to {stats['max']:.2f}
- StdDev: {stats['std']:.2f}
"""
        
        content += "\nKeywords: statistics, summary, average, 통계, 요약, 평균"
        
        return SearchResult(
            content=content,
            metadata={"type": "summary"},
            score=0.0,
            source="index",
            dataset_id=dataset_id,
            chunk_type="statistics"
        )
    
    def _preprocess_for_bm25(self, text: str) -> str:
        """BM25를 위한 텍스트 전처리"""
        # 소문자 변환
        text = text.lower()
        
        # 숫자 정규화 (소수점 제거)
        text = re.sub(r'\d+\.\d+', lambda m: str(int(float(m.group()))), text)
        
        # 한국어 토크나이징 (가능한 경우)
        if HAS_KONLPY and self._contains_korean(text):
            tokens = okt.morphs(text)
            text = ' '.join(tokens)
        
        return text
    
    def _contains_korean(self, text: str) -> bool:
        """한국어 포함 여부 확인"""
        return bool(re.search(r'[가-힣]', text))
    
    def _build_bm25_index(self):
        """BM25 인덱스 구축"""
        if not HAS_BM25:
            logger.warning("BM25 not available")
            return
        
        if not self.bm25_documents:
            results = self.collection.get()
            self.bm25_documents = results['documents']
            self.bm25_metadata = results['metadatas']
        
        tokenized_docs = []
        for doc in self.bm25_documents:
            processed = self._preprocess_for_bm25(doc)
            tokens = processed.split()
            tokenized_docs.append(tokens)
        
        self.bm25_index = BM25Okapi(tokenized_docs)
        logger.info(f"✅ BM25 index built with {len(tokenized_docs)} documents")
    
    def search(self, query: str, n_results: int = 5, use_reranker: bool = True) -> List[Dict]:
        """향상된 하이브리드 검색"""
        cache_key = f"{query}_{n_results}_{use_reranker}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        vector_results = self._vector_search(query, k=20)
        bm25_results = self._bm25_search(query, k=20)
        
        combined_results = self._reciprocal_rank_fusion(
            vector_results, 
            bm25_results,
            k=60
        )
        
        if use_reranker and self.reranker and len(combined_results) > 0:
            reranked_results = self._rerank_results(query, combined_results[:20])
            final_results = reranked_results[:n_results]
        else:
            final_results = combined_results[:n_results]
        
        formatted_results = []
        for result in final_results:
            formatted_results.append({
                'content': result.content,
                'metadata': result.metadata,
                'score': result.score,
                'dataset_id': result.dataset_id,
                'chunk_type': result.chunk_type,
                'source': result.source
            })
        
        self.cache[cache_key] = formatted_results
        if len(self.cache) > self.cache_size:
            self.cache.pop(next(iter(self.cache)))
        
        return formatted_results
    
    def _vector_search(self, query: str, k: int = 20) -> List[SearchResult]:
        """벡터 검색"""
        if not self.collection:
            return []
        
        query_embedding = self.encoder.encode(
            ["query: " + query],
            normalize_embeddings=True
        )
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=k
        )
        
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append(SearchResult(
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                score=1.0 / (1.0 + results['distances'][0][i]),
                source='vector',
                dataset_id=results['metadatas'][0][i].get('dataset_id', ''),
                chunk_type=results['metadatas'][0][i].get('chunk_type', '')
            ))
        
        return search_results
    
    def _bm25_search(self, query: str, k: int = 20) -> List[SearchResult]:
        """BM25 키워드 검색"""
        if not self.bm25_index:
            return []
        
        processed_query = self._preprocess_for_bm25(query)
        query_tokens = processed_query.split()
        
        scores = self.bm25_index.get_scores(query_tokens)
        
        top_indices = np.argsort(scores)[-k:][::-1]
        
        search_results = []
        for idx in top_indices:
            if scores[idx] > 0:
                search_results.append(SearchResult(
                    content=self.bm25_documents[idx],
                    metadata=self.bm25_metadata[idx],
                    score=scores[idx],
                    source='bm25',
                    dataset_id=self.bm25_metadata[idx].get('dataset_id', ''),
                    chunk_type=self.bm25_metadata[idx].get('chunk_type', '')
                ))
        
        return search_results
    
    def _reciprocal_rank_fusion(self, vector_results: List[SearchResult], 
                                bm25_results: List[SearchResult], 
                                k: int = 60) -> List[SearchResult]:
        """Reciprocal Rank Fusion으로 결과 병합"""
        fusion_scores = defaultdict(float)
        result_map = {}
        
        for rank, result in enumerate(vector_results):
            doc_id = f"{result.dataset_id}_{result.chunk_type}_{result.content[:50]}"
            fusion_scores[doc_id] += 1.0 / (k + rank + 1)
            result_map[doc_id] = result
            result_map[doc_id].source = 'hybrid'
        
        for rank, result in enumerate(bm25_results):
            doc_id = f"{result.dataset_id}_{result.chunk_type}_{result.content[:50]}"
            fusion_scores[doc_id] += 1.0 / (k + rank + 1)
            if doc_id not in result_map:
                result_map[doc_id] = result
                result_map[doc_id].source = 'hybrid'
        
        sorted_ids = sorted(fusion_scores.keys(), key=lambda x: fusion_scores[x], reverse=True)
        
        # 결과 생성
        combined_results = []
        for doc_id in sorted_ids:
            result = result_map[doc_id]
            result.score = fusion_scores[doc_id]
            combined_results.append(result)
        
        return combined_results
    
    def _rerank_results(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Cross-encoder로 재순위화"""
        if not self.reranker or not results:
            return results
        
        # Query-document 쌍 생성
        pairs = [[query, result.content] for result in results]
        
        # Cross-encoder 점수 계산
        scores = self.reranker.predict(pairs)
        
        for i, score in enumerate(scores):
            results[i].score = float(score)
        
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        
        return sorted_results
    
    def _get_korean_keywords(self, dataset_id: str) -> str:
        """데이터셋 ID에 대한 한국어 키워드"""
        korean_mappings = {
            'co2': 'CO2, 이산화탄소, 탄소배출',
            'temperature': '온도, 기온, 지구온난화',
            'renewable': '재생에너지, 신재생에너지',
            'covid': '코로나, 코비드, 팬데믹',
            'gdp': 'GDP, 국내총생산, 경제성장',
            'poverty': '빈곤, 빈곤율, 극빈층',
            'life-expectancy': '기대수명, 평균수명',
            'mortality': '사망률, 사망',
            'education': '교육, 학업',
            'population': '인구, 인구증가'
        }
        
        for key, value in korean_mappings.items():
            if key in dataset_id.lower():
                return value
        
        return ""
    
    def _get_related_terms(self, dataset_id: str) -> str:
        """관련 용어 생성"""
        related_terms = {
            'co2': 'carbon dioxide, emissions, greenhouse gas, climate change',
            'renewable': 'solar, wind, clean energy, sustainable',
            'gdp': 'economic growth, income, development',
            'covid': 'pandemic, coronavirus, SARS-CoV-2'
        }
        
        for key, value in related_terms.items():
            if key in dataset_id.lower():
                return value
        
        return ""


def test_enhanced_rag():
    """향상된 RAG 시스템 테스트"""
    logger.info("🚀 Initializing Enhanced OWID RAG System...")
    rag = EnhancedOWIDRAG()
    
    logger.info("\n📦 Building enhanced index...")
    rag.build_enhanced_index(force_rebuild=True)
    
    test_queries = [
        ("한국의 재생에너지 비율은?", "Korean/energy query"),
        ("COVID-19 vaccination rates in 2023", "English/health query"),
        ("대한민국 CO2 배출량 추세", "Korean/climate query"),
        ("global temperature anomaly trend", "English/climate query"),
        ("최신 GDP 성장률 데이터", "Korean/economy query")
    ]
    
    logger.info("\n🧪 Testing enhanced search...")
    for query, description in test_queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Query: {query} ({description})")
        logger.info('='*60)
        
        results = rag.search(query, n_results=3)
        
        for i, result in enumerate(results, 1):
            logger.info(f"\n📊 Result {i}:")
            logger.info(f"  Dataset: {result['dataset_id']}")
            logger.info(f"  Type: {result['chunk_type']}")
            logger.info(f"  Source: {result['source']}")
            logger.info(f"  Score: {result['score']:.4f}")
            logger.info(f"  Preview: {result['content'][:150]}...")
    
    logger.info("\n\n📈 Performance Comparison:")
    logger.info("="*60)
    
    query = "한국 재생에너지"
    
    vector_results = rag._vector_search(query, k=5)
    logger.info(f"\nVector-only results for '{query}':")
    for r in vector_results[:3]:
        logger.info(f"  - {r.dataset_id}: {r.score:.4f}")
    
    bm25_results = rag._bm25_search(query, k=5)
    logger.info(f"\nBM25-only results for '{query}':")
    for r in bm25_results[:3]:
        logger.info(f"  - {r.dataset_id}: {r.score:.4f}")
    
    hybrid_results = rag.search(query, n_results=5, use_reranker=False)
    logger.info(f"\nHybrid results for '{query}':")
    for r in hybrid_results[:3]:
        logger.info(f"  - {r['dataset_id']}: {r['score']:.4f}")
    
    reranked_results = rag.search(query, n_results=5, use_reranker=True)
    logger.info(f"\nHybrid + Reranker results for '{query}':")
    for r in reranked_results[:3]:
        logger.info(f"  - {r['dataset_id']}: {r['score']:.4f}")


if __name__ == "__main__":
    import subprocess
    import sys
    
    required_packages = {
        'rank-bm25': HAS_BM25,
        'sentence-transformers': HAS_SENTENCE_TRANSFORMERS,
        'chromadb': HAS_CHROMADB
    }
    
    missing = [pkg for pkg, installed in required_packages.items() if not installed]
    
    if missing:
        logger.info(f"Installing missing packages: {missing}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        logger.info("Please restart the script after installation")
        sys.exit(0)
    
    test_enhanced_rag()