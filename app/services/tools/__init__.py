"""Academic research tools for FactWave agents"""

# 학술/연구 도구
from .wikipedia_tool import WikipediaSearchTool
from .arxiv_tool import ArxivSearchTool
from .openalex_tool import OpenAlexTool

# 뉴스/미디어 도구
from .naver_news_tool import NaverNewsTool
from .newsapi_tool import NewsAPITool
from .gdelt_tool import GDELTTool
from .factcheck_google_tool import GoogleFactCheckTool

# 자연어 검색 가능한 통계 도구
from .kosis_search_tool import KOSISSearchTool
from .worldbank_search_tool import WorldBankSearchTool  
from .fred_search_tool import FREDSearchTool

# 특수 도구
from .owid_rag_tool import OWIDRAGTool

# LLM 에이전트가 직접 사용 가능한 도구만 export
__all__ = [
    # 학술/연구 (자연어 검색 가능)
    "WikipediaSearchTool",
    "ArxivSearchTool", 
    "OpenAlexTool",
    
    # 뉴스/미디어 (자연어 검색 가능)
    "NaverNewsTool",
    "NewsAPITool",
    "GDELTTool",
    "GoogleFactCheckTool",
    
    # 통계 데이터 (자연어 검색 가능)
    "KOSISSearchTool",      # 한국 통계청 자연어 검색
    "WorldBankSearchTool",  # World Bank 자연어 검색
    "FREDSearchTool",       # FRED 자연어 검색
    "OWIDRAGTool",          # Our World in Data RAG
]

# 제거된 도구들 (코드/ID 필요):
# - FREDTool: series_id 필요
# - WorldBankTool: indicator 코드 필요
# - OECDTool: dataset ID 필요
# - IMFSDMXTool: dataflow, key 필요
# - KOSISTool: orgId, tblId 필요