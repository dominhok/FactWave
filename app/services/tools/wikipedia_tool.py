"""Wikipedia Search Tool for Academic Agent"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import wikipediaapi
import requests
from rich.console import Console

console = Console()


class WikipediaSearchInput(BaseModel):
    """Input schema for Wikipedia search"""
    query: str = Field(..., description="Search query for Wikipedia")
    lang: str = Field(default="ko", description="Language code (ko for Korean, en for English)")


class WikipediaSearchTool(BaseTool):
    """Wikipedia search tool for finding background information"""
    
    name: str = "Wikipedia Search"
    description: str = """
    Useful for finding general background information, definitions, and context about topics.
    Returns summary information from Wikipedia articles.
    Supports both Korean (ko) and English (en) searches.
    """
    args_schema: Type[BaseModel] = WikipediaSearchInput
    
    def _run(self, query: str, lang: str = "ko") -> str:
        """Execute Wikipedia search and return summary"""
        try:
            # Wikipedia API 초기화
            user_agent = "FactWave/1.0 (https://factwave.ai; contact@factwave.ai)"
            wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language=lang)
            
            # 페이지 검색
            page = wiki.page(query)
            
            if not page.exists():
                # 검색 API 사용하여 유사한 페이지 찾기
                search_url = f"https://{lang}.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 5
                }
                
                response = requests.get(search_url, params=params)
                data = response.json()
                
                if data["query"]["search"]:
                    # 첫 번째 검색 결과 사용
                    first_result = data["query"]["search"][0]["title"]
                    page = wiki.page(first_result)
                else:
                    return f"Wikipedia에서 '{query}'에 대한 정보를 찾을 수 없습니다."
            
            # 요약 정보 추출
            summary = page.summary[:1000]  # 처음 1000자만
            
            result = f"""
📚 Wikipedia 검색 결과: {page.title}

📝 요약:
{summary}

🔗 전체 문서: {page.fullurl}

📊 관련 섹션:
"""
            # 주요 섹션 목록 추가
            sections = []
            for section in page.sections[:5]:  # 처음 5개 섹션만
                if section.title and section.title != "See also" and section.title != "References":
                    sections.append(f"- {section.title}")
            
            if sections:
                result += "\n".join(sections)
            else:
                result += "- 추가 섹션 없음"
            
            return result
            
        except Exception as e:
            console.print(f"[red]Wikipedia 검색 오류: {str(e)}[/red]")
            return f"Wikipedia 검색 중 오류가 발생했습니다: {str(e)}"