"""Semantic Scholar API Tool for Academic Agent"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests
from datetime import datetime
from rich.console import Console

console = Console()


class SemanticScholarInput(BaseModel):
    """Input schema for Semantic Scholar search"""
    query: str = Field(..., description="Search query for academic papers")
    limit: int = Field(default=5, description="Number of papers to return")
    year_filter: Optional[str] = Field(default=None, description="Filter by year range (e.g., '2020-2024')")


class SemanticScholarTool(BaseTool):
    """Semantic Scholar search tool for finding academic papers"""
    
    name: str = "Semantic Scholar Search"
    description: str = """
    Search for academic papers and research using Semantic Scholar API.
    Returns paper titles, authors, abstracts, citations, and AI-generated summaries (TL;DR).
    Covers 214M+ papers across all academic fields.
    """
    args_schema: Type[BaseModel] = SemanticScholarInput
    
    def _run(self, query: str, limit: int = 5, year_filter: Optional[str] = None) -> str:
        """Execute Semantic Scholar search and return papers"""
        try:
            # Semantic Scholar API endpoint
            base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            
            # 쿼리 파라미터 설정
            params = {
                "query": query,
                "limit": limit,
                "fields": "paperId,title,abstract,authors,year,citationCount,tldr,publicationDate,venue,openAccessPdf"
            }
            
            # 연도 필터 적용
            if year_filter:
                params["year"] = year_filter
            
            # API 요청
            headers = {
                "User-Agent": "FactWave/1.0 (contact@factwave.ai)"
            }
            
            # Rate limit 대응을 위한 재시도 로직
            import time
            max_retries = 3
            retry_delay = 2  # 초
            
            for attempt in range(max_retries):
                response = requests.get(base_url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 429:  # Too Many Requests
                    if attempt < max_retries - 1:
                        console.print(f"[yellow]Rate limit 도달. {retry_delay}초 후 재시도... (시도 {attempt + 1}/{max_retries})[/yellow]")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        return "Semantic Scholar API rate limit 초과. 잠시 후 다시 시도해주세요."
                
                if response.status_code != 200:
                    return f"Semantic Scholar API 오류: {response.status_code} - {response.text[:200]}"
                
                break  # 성공시 루프 종료
            
            data = response.json()
            papers = data.get("data", [])
            
            if not papers:
                return f"'{query}'에 대한 학술 논문을 찾을 수 없습니다."
            
            # 결과 포맷팅
            result = f"🎓 Semantic Scholar 검색 결과: '{query}'\n"
            result += f"📊 총 {len(papers)}개 논문 발견\n\n"
            
            for i, paper in enumerate(papers, 1):
                result += f"📄 논문 {i}: {paper.get('title', 'N/A')}\n"
                
                # 저자 정보
                authors = paper.get('authors', [])
                if authors:
                    author_names = [author.get('name', 'Unknown') for author in authors[:3]]
                    if len(authors) > 3:
                        author_names.append(f"외 {len(authors)-3}명")
                    result += f"👥 저자: {', '.join(author_names)}\n"
                
                # 출판 정보
                year = paper.get('year', 'N/A')
                venue = paper.get('venue', 'N/A')
                result += f"📅 출판: {year}년"
                if venue and venue != 'N/A':
                    result += f" | {venue}"
                result += "\n"
                
                # 인용 수
                citations = paper.get('citationCount', 0)
                result += f"📈 인용 수: {citations}회\n"
                
                # TL;DR (AI 요약)
                tldr = paper.get('tldr')
                if tldr and tldr.get('text'):
                    result += f"🤖 AI 요약: {tldr['text']}\n"
                
                # 초록 (TL;DR이 없는 경우)
                elif paper.get('abstract'):
                    abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
                    result += f"📝 초록: {abstract}\n"
                
                # 오픈 액세스 링크
                pdf = paper.get('openAccessPdf')
                if pdf and pdf.get('url'):
                    result += f"📎 PDF: {pdf['url']}\n"
                
                # Paper ID (상세 정보 조회용)
                paper_id = paper.get('paperId')
                if paper_id:
                    result += f"🔗 상세 정보: https://www.semanticscholar.org/paper/{paper_id}\n"
                
                result += "\n" + "-"*50 + "\n\n"
            
            return result
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Semantic Scholar API 요청 오류: {str(e)}[/red]")
            return f"Semantic Scholar API 요청 중 오류가 발생했습니다: {str(e)}"
        except Exception as e:
            console.print(f"[red]Semantic Scholar 검색 오류: {str(e)}[/red]")
            return f"Semantic Scholar 검색 중 오류가 발생했습니다: {str(e)}"