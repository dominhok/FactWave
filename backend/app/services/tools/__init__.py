"""Academic research tools for FactWave agents"""

# 학술/연구 도구
from .academic.wikipedia_tool import WikipediaSearchTool
from .academic.arxiv_tool import ArxivSearchTool
from .academic.openalex_tool import OpenAlexTool

# 뉴스/미디어 도구
from .news.naver_news_tool import NaverNewsTool
from .news.newsapi_tool import NewsAPITool
from .news.factcheck_google_tool import GoogleFactCheckTool

# 자연어 검색 가능한 통계 도구
from .statistics.kosis_search_tool import KOSISSearchTool
from .statistics.worldbank_search_tool import WorldBankSearchTool  
from .statistics.fred_search_tool import FREDSearchTool

# 특수 도구
from .statistics.owid_rag_tool import OWIDRAGTool

# 커뮤니티 도구
from .community.twitter_tool import TwitterTool
from .community.youtube_tool import YouTubeTool

# 검증 도구
from .verification.ai_image_detector import AIImageDetectorTool

# LLM 에이전트가 직접 사용 가능한 도구만 export
__all__ = [
    # 학술/연구 (자연어 검색 가능)
    "WikipediaSearchTool",
    "ArxivSearchTool", 
    "OpenAlexTool",
    
    # 뉴스/미디어 (자연어 검색 가능)
    "NaverNewsTool",
    "NewsAPITool",
    "GoogleFactCheckTool",
    
    # 통계 데이터 (자연어 검색 가능)
    "KOSISSearchTool",      # 한국 통계청 자연어 검색
    "WorldBankSearchTool",  # World Bank 자연어 검색
    "FREDSearchTool",       # FRED 자연어 검색
    "OWIDRAGTool",          # Our World in Data RAG
    
    # 커뮤니티 도구
    "TwitterTool",          # Twitter/X 커뮤니티 검색
    "YouTubeTool",          # YouTube 영상 검색 및 댓글 분석
    
    # 검증 도구
    "AIImageDetectorTool",  # AI 생성 이미지 탐지 (Sightengine)
]

# 제거된 도구들 (코드/ID 필요):
# - FREDTool: series_id 필요
# - WorldBankTool: indicator 코드 필요
# - OECDTool: dataset ID 필요
# - IMFSDMXTool: dataflow, key 필요
# - KOSISTool: orgId, tblId 필요