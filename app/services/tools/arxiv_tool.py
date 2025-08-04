"""ArXiv Search Tool for Academic Agent"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import arxiv
from datetime import datetime
from rich.console import Console

console = Console()


class ArxivSearchInput(BaseModel):
    """Input schema for ArXiv search"""
    query: str = Field(..., description="Search query for ArXiv papers")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    sort_by: str = Field(default="relevance", description="Sort by: relevance, lastUpdatedDate, submittedDate")


class ArxivSearchTool(BaseTool):
    """ArXiv search tool for finding CS, Physics, Math papers"""
    
    name: str = "ArXiv Search"
    description: str = """
    Search for preprint papers on ArXiv, especially useful for:
    - Computer Science (CS)
    - Physics
    - Mathematics
    - Statistics
    - Quantitative Biology
    - Quantitative Finance
    Returns the latest research papers with abstracts and direct PDF links.
    """
    args_schema: Type[BaseModel] = ArxivSearchInput
    
    def _run(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> str:
        """Execute ArXiv search and return papers"""
        try:
            # ArXiv 검색 클라이언트 설정
            sort_criterion = arxiv.SortCriterion.Relevance
            if sort_by == "lastUpdatedDate":
                sort_criterion = arxiv.SortCriterion.LastUpdatedDate
            elif sort_by == "submittedDate":
                sort_criterion = arxiv.SortCriterion.SubmittedDate
            
            # 검색 실행
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=sort_criterion
            )
            
            papers = list(search.results())
            
            if not papers:
                return f"ArXiv에서 '{query}'에 대한 논문을 찾을 수 없습니다."
            
            # 결과 포맷팅
            result = f"📚 ArXiv 검색 결과: '{query}'\n"
            result += f"📊 총 {len(papers)}개 논문 발견\n\n"
            
            for i, paper in enumerate(papers, 1):
                result += f"📄 논문 {i}: {paper.title}\n"
                
                # 저자 정보
                authors = [author.name for author in paper.authors[:3]]
                if len(paper.authors) > 3:
                    authors.append(f"외 {len(paper.authors)-3}명")
                result += f"👥 저자: {', '.join(authors)}\n"
                
                # 날짜 정보
                published = paper.published.strftime("%Y-%m-%d")
                updated = paper.updated.strftime("%Y-%m-%d")
                result += f"📅 출판일: {published}"
                if updated != published:
                    result += f" (업데이트: {updated})"
                result += "\n"
                
                # 카테고리
                categories = paper.categories
                result += f"🏷️ 카테고리: {', '.join(categories[:3])}\n"
                
                # 초록 (처음 300자)
                abstract = paper.summary.replace('\n', ' ')
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                result += f"📝 초록: {abstract}\n"
                
                # 링크
                result += f"🔗 논문 링크: {paper.entry_id}\n"
                result += f"📎 PDF 다운로드: {paper.pdf_url}\n"
                
                # ArXiv ID
                arxiv_id = paper.entry_id.split('/')[-1]
                result += f"📌 ArXiv ID: {arxiv_id}\n"
                
                # 코멘트 (있는 경우)
                if paper.comment:
                    result += f"💬 코멘트: {paper.comment}\n"
                
                result += "\n" + "-"*50 + "\n\n"
            
            return result
            
        except Exception as e:
            console.print(f"[red]ArXiv 검색 오류: {str(e)}[/red]")
            return f"ArXiv 검색 중 오류가 발생했습니다: {str(e)}"