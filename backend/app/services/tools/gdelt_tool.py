"""GDELT v2 Tool - Events/Doc API lightweight wrapper"""

from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests


class GDELTInput(BaseModel):
    query: str = Field(..., description="검색 키워드 (GDELT Doc API) ")
    max_records: Optional[int] = Field(50, description="최대 문서 수(기본 50)")
    timespan: Optional[str] = Field("7d", description="기간(예: 7d, 30d, 12h)")
    sort: Optional[str] = Field("DateDesc", description="정렬: DateDesc|DateAsc|ToneDesc 등")


class GDELTTool(BaseTool):
    """GDELT Doc API search wrapper"""

    name: str = "GDELT_Doc_Search"
    description: str = (
        "GDELT v2 Doc API(기사 검색)를 호출해 전세계 뉴스/문서 메타를 검색합니다. 인증 불필요."
    )
    args_schema: Type[BaseModel] = GDELTInput

    def _run(
        self,
        query: str,
        max_records: Optional[int] = 50,
        timespan: Optional[str] = "7d",
        sort: Optional[str] = "DateDesc",
    ) -> str:
        # See: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "JSON",
            "timespan": timespan or "7d",
            "maxrecords": max(1, min(250, max_records or 50)),
            "sort": sort or "DateDesc",
        }
        try:
            resp = requests.get(url, params=params, timeout=25)
            if resp.status_code != 200:
                return f"GDELT API 오류: HTTP {resp.status_code} - {resp.text[:300]}"
            data = resp.json()
            arts = (data.get("articles") or [])
            if not arts:
                return f"'{query}'에 대한 GDELT 결과가 없습니다."
            lines = [f"🌐 GDELT 검색: '{query}' (표시 {len(arts)}건)\n"]
            for i, a in enumerate(arts[:10], 1):
                title = a.get("title") or "제목 없음"
                source = a.get("sourceCommonName") or a.get("domain") or "출처 미상"
                date = a.get("seendate") or ""
                url_a = a.get("url") or ""
                lines.append(f"[{i}] {title}\n- 출처: {source}\n- 일시: {date}\n- 링크: {url_a}")
            if len(arts) > 10:
                lines.append("... (더 많은 결과가 있습니다)")
            return "\n".join(lines)
        except requests.exceptions.RequestException as e:
            return f"GDELT API 요청 오류: {str(e)}"

