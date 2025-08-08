"""Google Fact Check Tools API - claims.search wrapper"""

from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os
import requests


class FactCheckSearchInput(BaseModel):
    query: str = Field(..., description="텍스트 쿼리")
    languageCode: Optional[str] = Field(None, description="BCP-47 언어 코드, 예: en, ko")
    maxAgeDays: Optional[int] = Field(None, description="결과의 최대 경과일(일 기준)")
    pageSize: Optional[int] = Field(10, description="페이지 크기(기본 10)")


class GoogleFactCheckTool(BaseTool):
    """Google Fact Check Tools - Claim Search API"""

    name: str = "Google_Fact_Check_Search"
    description: str = (
        "Google Fact Check Tools의 claims:search API를 통해 사실검증 기사(ClaimReview)를 검색합니다."
    )
    args_schema: Type[BaseModel] = FactCheckSearchInput

    def _run(
        self,
        query: str,
        languageCode: Optional[str] = None,
        maxAgeDays: Optional[int] = None,
        pageSize: Optional[int] = 10,
    ) -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Google API 키가 설정되지 않았습니다. 환경변수 GOOGLE_API_KEY를 설정하세요."

        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {
            "key": api_key,
            "query": query,
            "pageSize": max(1, min(20, pageSize or 10)),
        }
        if languageCode:
            params["languageCode"] = languageCode
        if maxAgeDays:
            params["maxAgeDays"] = max(1, maxAgeDays)

        try:
            resp = requests.get(url, params=params, timeout=20)
            if resp.status_code != 200:
                return f"Google Fact Check API 오류: HTTP {resp.status_code} - {resp.text[:300]}"
            data = resp.json()
            claims = data.get("claims", [])
            if not claims:
                return f"'{query}'에 대한 사실검증 결과가 없습니다."

            lines = [f"🔎 Fact Check 검색 결과: '{query}' (표시 {len(claims)}건)\n"]
            for i, c in enumerate(claims, 1):
                text = c.get("text") or "(claim 미상)"
                claimant = c.get("claimant") or "(주장자 미상)"
                date = c.get("claimDate") or ""
                reviews = c.get("claimReview", [])
                if reviews:
                    r = reviews[0]
                    pub = (r.get("publisher") or {}).get("name") or "출처 미상"
                    rating = r.get("textualRating") or ""
                    url_r = r.get("url") or ""
                    lines.append(
                        f"[{i}] {text}\n- 주장자: {claimant}\n- 일시: {date}\n- 출처: {pub}\n- 판정: {rating}\n- 링크: {url_r}\n"
                    )
                else:
                    lines.append(f"[{i}] {text} - 주장자: {claimant} ({date})\n")
            return "\n".join(lines)
        except requests.exceptions.RequestException as e:
            return f"Google Fact Check API 요청 오류: {str(e)}"

