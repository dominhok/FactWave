"""Academic research tools for FactWave agents"""

from .wikipedia_tool import WikipediaSearchTool
from .arxiv_tool import ArxivSearchTool
from .naver_news_tool import NaverNewsTool
from .openalex_tool import OpenAlexTool

__all__ = [
    "WikipediaSearchTool",
    "ArxivSearchTool",
    "NaverNewsTool",
    "OpenAlexTool"
]