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
            
            # 팩트체킹을 위해 더 많은 내용 추출
            # 전체 요약 (최대 3000자)
            full_summary = page.summary
            if len(full_summary) > 3000:
                full_summary = full_summary[:2997] + "..."
            
            result = f"""
📚 Wikipedia 검색 결과: {page.title}

📝 요약:
{full_summary}

🔗 전체 문서: {page.fullurl}

📊 주요 섹션 내용:
"""
            # 주요 섹션의 내용도 포함 (팩트체킹에 중요)
            sections_content = []
            total_chars = len(full_summary)
            
            for section in page.sections[:10]:  # 더 많은 섹션 확인
                if total_chars > 5000:  # 최대 5000자까지
                    break
                    
                if section.title and section.title not in ["See also", "References", "External links", "같이 보기", "각주", "외부 링크"]:
                    section_text = section.text[:500] if section.text else ""
                    if section_text:
                        sections_content.append(f"\n### {section.title}")
                        sections_content.append(section_text)
                        total_chars += len(section_text)
            
            if sections_content:
                result += "\n".join(sections_content)
            else:
                result += "\n- 추가 섹션 내용 없음"
            
            return result
            
        except Exception as e:
            console.print(f"[red]Wikipedia 검색 오류: {str(e)}[/red]")
            return f"Wikipedia 검색 중 오류가 발생했습니다: {str(e)}"