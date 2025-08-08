"""
OpenAlex Tool - Academic Paper Search (Semantic Scholar Alternative)

OpenAlex API를 사용한 학술 논문 검색 도구
- 240M+ 논문 (Semantic Scholar보다 많음)
- Rate limit: 100,000 calls/day (매우 관대함)
- API 키 불필요
"""

import requests
import json
from typing import Dict, List, Optional, Any, Type
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class OpenAlexClient:
    """OpenAlex API 클라이언트"""
    
    def __init__(self):
        self.base_url = "https://api.openalex.org"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "FactWave/1.0 (https://github.com/FactWave)"  # Polite request header
        }
    
    def search_works(self, query: str, limit: int = 10, 
                    year_from: Optional[int] = None,
                    year_to: Optional[int] = None) -> Dict[str, Any]:
        """
        논문 검색
        
        Args:
            query: 검색어
            limit: 결과 개수 제한
            year_from: 시작 연도
            year_to: 종료 연도
        """
        
        # 검색 파라미터 구성
        params = {
            "search": query,
            "per-page": min(limit, 200),  # 최대 200개
            "page": 1
        }
        
        # 연도 필터 추가
        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_to:
            filters.append(f"to_publication_date:{year_to}-12-31")
        
        if filters:
            params["filter"] = ",".join(filters)
        
        try:
            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return self._format_results(data, query)
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"OpenAlex API 오류: {str(e)}"
            }
    
    def get_paper_details(self, openalex_id: str) -> Dict[str, Any]:
        """논문 상세 정보 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/works/{openalex_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"논문 상세 조회 오류: {str(e)}"
            }
    
    def _format_results(self, data: Dict, query: str) -> Dict[str, Any]:
        """검색 결과 포맷팅"""
        results = data.get("results", [])
        meta = data.get("meta", {})
        
        formatted_papers = []
        for paper in results:
            # 저자 정보 추출
            authors = []
            for authorship in paper.get("authorships", []):
                author = authorship.get("author", {})
                if author.get("display_name"):
                    authors.append(author["display_name"])
            
            # 출판 정보 추출
            primary_location = paper.get("primary_location") or {}
            source = primary_location.get("source") or {}
            
            # 논문 정보 포맷팅
            formatted_paper = {
                "id": paper.get("id", "").split("/")[-1],  # OpenAlex ID
                "title": paper.get("display_name", "제목 없음"),
                "authors": authors[:5],  # 최대 5명
                "year": paper.get("publication_year"),
                "date": paper.get("publication_date"),
                "abstract": self._clean_abstract(paper.get("abstract")),
                "doi": paper.get("doi"),
                "citations_count": paper.get("cited_by_count", 0),
                "journal": source.get("display_name", ""),
                "type": paper.get("type", ""),
                "open_access": paper.get("open_access", {}).get("is_oa", False),
                "pdf_url": paper.get("open_access", {}).get("oa_url"),
                "openalex_url": paper.get("id"),
                "concepts": [c["display_name"] for c in paper.get("concepts", [])[:5]]
            }
            
            formatted_papers.append(formatted_paper)
        
        return {
            "success": True,
            "query": query,
            "total_results": meta.get("count", 0),
            "returned_results": len(formatted_papers),
            "papers": formatted_papers,
            "meta": {
                "db_response_time_ms": meta.get("db_response_time_ms"),
                "page": meta.get("page", 1),
                "per_page": meta.get("per_page")
            }
        }
    
    def _clean_abstract(self, abstract: Optional[str]) -> str:
        """초록 정리"""
        if not abstract:
            return ""
        
        # 팩트체킹을 위해 초록 전체 반환 (최대 2000자)
        if len(abstract) > 2000:
            return abstract[:1997] + "..."
        
        return abstract


# CrewAI Tool Input Schema
class OpenAlexInput(BaseModel):
    """Input schema for OpenAlex search"""
    query: str = Field(description="검색어 (논문 제목, 키워드, 저자명 등)")
    limit: int = Field(default=10, description="반환할 논문 수 (최대 200)")
    year_from: Optional[int] = Field(default=None, description="검색 시작 연도")
    year_to: Optional[int] = Field(default=None, description="검색 종료 연도")


# CrewAI Tool Wrapper
class OpenAlexTool(BaseTool):
    """OpenAlex 학술 논문 검색 도구"""
    
    name: str = "OpenAlex Academic Search"
    description: str = """
    OpenAlex를 통한 학술 논문 검색 도구입니다.
    240M+ 논문을 검색할 수 있으며, Semantic Scholar보다 더 많은 논문을 포함합니다.
    
    특징:
    - Rate limit: 100,000 calls/day (매우 관대함)
    - API 키 불필요
    - 논문 제목, 저자, 초록, 인용수, DOI, 오픈액세스 여부 등 제공
    - 연도별 필터링 지원
    
    검색 가능한 내용:
    - 논문 제목 및 키워드
    - 저자명
    - 학술 개념 및 주제
    - DOI
    """
    args_schema: Type[BaseModel] = OpenAlexInput
    
    def __init__(self):
        super().__init__()
        self._tool = OpenAlexClient()
    
    def _run(self, query: str, limit: int = 10,
             year_from: Optional[int] = None,
             year_to: Optional[int] = None) -> str:
        """
        OpenAlex 학술 논문 검색 실행
        
        Args:
            query: 검색어
            limit: 반환할 논문 수
            year_from: 검색 시작 연도
            year_to: 검색 종료 연도
        
        Returns:
            str: JSON 형식의 검색 결과
        """
        try:
            result = self._tool.search_works(query, limit, year_from, year_to)
            
            if result.get("success") and result.get("papers"):
                # 결과 요약 추가
                papers = result["papers"]
                summary = f"\n📚 OpenAlex 검색 결과: '{query}'\n"
                summary += f"📊 총 {result['total_results']:,}개 논문 중 {len(papers)}개 표시\n\n"
                
                for i, paper in enumerate(papers, 1):
                    summary += f"📄 논문 {i}: {paper['title']}\n"
                    if paper['authors']:
                        summary += f"👥 저자: {', '.join(paper['authors'])}\n"
                    summary += f"📅 출판: {paper['year']}년\n"
                    if paper['journal']:
                        summary += f"📖 저널: {paper['journal']}\n"
                    summary += f"📈 인용수: {paper['citations_count']:,}회\n"
                    if paper['open_access']:
                        summary += f"🔓 오픈액세스: 가능\n"
                        if paper['pdf_url']:
                            summary += f"📎 PDF: {paper['pdf_url']}\n"
                    if paper['abstract']:
                        # 팩트체킹을 위해 초록 전체 포함
                        summary += f"📝 초록: {paper['abstract']}\n"
                    summary += f"🔗 OpenAlex: {paper['openalex_url']}\n"
                    summary += "-" * 50 + "\n\n"
                
                result["summary"] = summary
            
            # LLM이 이해하기 쉽게 텍스트 형식으로 변환
            if result.get("success") and result.get("papers"):
                return result.get("summary", "검색 결과가 없습니다.")
            else:
                return f"❌ OpenAlex 검색 실패: {result.get('error', '알 수 없는 오류')}"
            
        except Exception as e:
            return f"❌ OpenAlex 검색 중 오류 발생: {str(e)}"


if __name__ == "__main__":
    # 테스트 코드
    client = OpenAlexClient()
    
    print("=== OpenAlex Tool 테스트 ===")
    
    # GPT-4 검색 테스트
    print("\n1. GPT-4 논문 검색")
    result = client.search_works("GPT-4", limit=3)
    if result.get("success"):
        print(f"✅ 성공: {result['total_results']}개 논문 발견")
        for paper in result["papers"][:2]:
            print(f"  - {paper['title']} ({paper['year']})")
            print(f"    인용수: {paper['citations_count']}, 오픈액세스: {paper['open_access']}")
    else:
        print(f"❌ 실패: {result.get('error')}")