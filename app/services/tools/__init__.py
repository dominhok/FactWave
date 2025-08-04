"""Academic research tools for FactWave agents"""

from .wikipedia_tool import WikipediaSearchTool
from .semantic_scholar_tool import SemanticScholarTool
from .arxiv_tool import ArxivSearchTool
from .worldbank_tool import WorldBankTool
from .naver_news_tool import NaverNewsTool
from .global_statistics_tool import GlobalStatisticsTool, create_global_statistics_tool

__all__ = [
    "WikipediaSearchTool",
    "SemanticScholarTool",
    "ArxivSearchTool",
    "WorldBankTool",
    "NaverNewsTool",
    "GlobalStatisticsTool",
    "create_global_statistics_tool"
]