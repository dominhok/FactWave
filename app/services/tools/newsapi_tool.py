"""NewsAPI.org Tool - International news search"""

from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os
import requests


class NewsAPIInput(BaseModel):
    """Input schema for NewsAPI search"""
    query: str = Field(..., description="검색 키워드/문구")
    from_date: Optional[str] = Field(None, description="ISO8601 시작 날짜(예: 2025-08-08)")
    to_date: Optional[str] = Field(None, description="ISO8601 종료 날짜")
    language: Optional[str] = Field(None, description="언어 코드, 예: en, ko")
    sort_by: Optional[str] = Field("publishedAt", description="정렬: relevancy|popularity|publishedAt")
    page_size: Optional[int] = Field(20, description="페이지당 결과수(최대 100)")


class NewsAPITool(BaseTool):
    """NewsAPI.org everything endpoint wrapper"""

    name: str = "NewsAPI Search"
    description: str = (
        "NewsAPI.org의 /v2/everything 엔드포인트로 국제 뉴스 검색을 수행합니다. "
        "키워드, 날짜 범위, 언어, 정렬을 지원합니다."
    )
    args_schema: Type[BaseModel] = NewsAPIInput

    def _run(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: Optional[str] = None,
        sort_by: Optional[str] = "publishedAt",
        page_size: Optional[int] = 20,
    ) -> str:
        api_key = os.getenv("NEWSAPI_API_KEY")
        if not api_key:
            return "NewsAPI API 키가 설정되지 않았습니다. 환경변수 NEWSAPI_API_KEY를 설정하세요."

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": sort_by or "publishedAt",
            "pageSize": max(1, min(100, page_size or 20)),
        }
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if language:
            params["language"] = language

        headers = {"X-Api-Key": api_key}

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            if resp.status_code != 200:
                return f"NewsAPI 오류: HTTP {resp.status_code} - {resp.text[:300]}"
            data = resp.json()
            if data.get("status") != "ok":
                return f"NewsAPI 오류: {data}"

            articles = data.get("articles", [])
            if not articles:
                return f"'{query}'에 대한 뉴스 결과가 없습니다."

            lines = [
                f"📰 NewsAPI 검색 결과: '{query}' (총 {data.get('totalResults', 0):,}건 중 {len(articles)}건 표시)\n"
            ]
            for i, a in enumerate(articles, 1):
                title = a.get("title") or "제목 없음"
                source = (a.get("source") or {}).get("name") or "출처 미상"
                published = a.get("publishedAt") or ""
                desc = a.get("description") or ""
                if len(desc) > 200:
                    desc = desc[:200] + "..."
                url_a = a.get("url") or ""
                lines.append(
                    f"[{i}] {title}\n- 출처: {source}\n- 일시: {published}\n- 요약: {desc}\n- 링크: {url_a}\n"
                )
            return "\n".join(lines)
        except requests.exceptions.RequestException as e:
            return f"NewsAPI 요청 오류: {str(e)}"

