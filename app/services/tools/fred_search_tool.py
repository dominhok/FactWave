"""FRED Search Tool - 자연어로 FRED 시계열 검색"""

import os
from typing import Type, Optional, List, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests
from datetime import datetime, timedelta


class FREDSearchInput(BaseModel):
    query: str = Field(..., description="검색어 (예: unemployment, GDP, inflation)")
    fetch_data: bool = Field(True, description="데이터도 함께 가져올지 여부")
    limit: int = Field(10, description="최근 몇 개 데이터를 가져올지")


class FREDSearchTool(BaseTool):
    """FRED 자연어 검색 도구 - 경제 지표를 자연어로 검색"""

    name: str = "FRED_Natural_Search"
    description: str = (
        "FRED (Federal Reserve Economic Data)를 자연어로 검색합니다. "
        "예: 'unemployment rate', 'GDP', 'inflation', 'interest rate' 등"
    )
    args_schema: Type[BaseModel] = FREDSearchInput
    # Pydantic 필드로 선언
    common_series: Dict[str, str] = {
            "unemployment": "UNRATE",
            "gdp": "GDP",
            "real gdp": "GDPC1",
            "inflation": "CPIAUCSL",
            "interest rate": "DFF",
            "federal funds": "DFF",
            "10 year treasury": "DGS10",
            "sp500": "SP500",
            "exchange rate": "DEXUSEU"
    }
    
    def _search_series(self, query: str, limit: int = 5) -> List[Dict]:
        """FRED series/search API 사용"""
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            # API 키 없으면 기본 매핑만 사용
            return self._search_from_cache(query)
        
        url = "https://api.stlouisfed.org/fred/series/search"
        params = {
            "search_text": query,
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "order_by": "popularity",
            "sort_order": "desc"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "seriess" in data:
                    return data["seriess"]
        except:
            pass
        
        # 실패 시 캐시에서 검색
        return self._search_from_cache(query)
    
    def _search_from_cache(self, query: str) -> List[Dict]:
        """캐시된 매핑에서 검색"""
        query_lower = query.lower()
        results = []
        
        for key, series_id in self.common_series.items():
            if key in query_lower or query_lower in key:
                # 기본 정보 생성
                results.append({
                    "id": series_id,
                    "title": self._get_series_title(series_id),
                    "units": self._get_series_units(series_id),
                    "frequency": "Monthly" if series_id != "GDP" else "Quarterly"
                })
        
        return results
    
    def _get_series_title(self, series_id: str) -> str:
        """시리즈 ID에서 제목 생성"""
        titles = {
            "UNRATE": "Unemployment Rate",
            "GDP": "Gross Domestic Product",
            "GDPC1": "Real Gross Domestic Product",
            "CPIAUCSL": "Consumer Price Index for All Urban Consumers",
            "DFF": "Federal Funds Effective Rate",
            "DGS10": "10-Year Treasury Constant Maturity Rate",
            "SP500": "S&P 500",
            "DEXUSEU": "U.S. / Euro Foreign Exchange Rate"
        }
        return titles.get(series_id, series_id)
    
    def _get_series_units(self, series_id: str) -> str:
        """시리즈 단위 정보"""
        units = {
            "UNRATE": "Percent",
            "GDP": "Billions of Dollars",
            "GDPC1": "Billions of Chained 2017 Dollars",
            "CPIAUCSL": "Index 1982-1984=100",
            "DFF": "Percent",
            "DGS10": "Percent",
            "SP500": "Index",
            "DEXUSEU": "U.S. Dollars to One Euro"
        }
        return units.get(series_id, "")
    
    def _fetch_series_data(self, series_id: str, limit: int = 10) -> Optional[List[Dict]]:
        """시리즈 데이터 가져오기"""
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return None
        
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "sort_order": "desc"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if "observations" in data:
                    return data["observations"]
        except:
            pass
        
        return None
    
    def _format_observations(self, observations: List[Dict], units: str) -> str:
        """관측값 포맷팅"""
        if not observations:
            return "데이터 없음"
        
        lines = []
        for obs in observations[:10]:  # 최근 10개만
            date = obs.get("date", "")
            value = obs.get("value", "")
            
            # 값 포맷팅
            try:
                val = float(value)
                if "percent" in units.lower():
                    formatted_value = f"{val:.2f}%"
                elif "billions" in units.lower():
                    formatted_value = f"${val:,.1f}B"
                elif "index" in units.lower():
                    formatted_value = f"{val:,.2f}"
                else:
                    formatted_value = f"{val:,.2f}"
            except:
                formatted_value = value
            
            lines.append(f"  {date}: {formatted_value}")
        
        return "\n".join(lines)
    
    def _run(
        self,
        query: str,
        fetch_data: bool = True,
        limit: int = 10
    ) -> str:
        """검색 실행 - 구조화된 메타데이터와 데이터 함께 제공"""
        
        # 시리즈 검색
        search_results = self._search_series(query, limit=5)
        
        if not search_results:
            return f"❌ '{query}'에 대한 시계열을 찾을 수 없습니다."
        
        return self._format_structured_output(query, search_results, fetch_data, limit)
    
    def _format_structured_output(self, query: str, search_results: List[Dict], fetch_data: bool, limit: int) -> str:
        """구조화된 FRED 출력 형식"""
        
        result = []
        result.append(f"📊 FRED 경제 데이터 검색: '{query}'")
        result.append("━" * 60)
        result.append("📌 출처: 미국 연방준비은행(Federal Reserve Bank)")
        result.append(f"📊 발견된 시계열: {len(search_results)}개\n")
        
        for i, series in enumerate(search_results, 1):
            # 시리즈 메타데이터 추출
            metadata = self._extract_series_metadata(series)
            
            result.append(f"📈 [{i}] {metadata['title']}")
            result.append("─" * 40)
            
            # 모든 메타데이터 표시
            for key, value in metadata.items():
                if value and key not in ['title']:  # title은 헤더에 사용되므로 제외
                    result.append(f"  📋 {key}: {value}")
            
            # 데이터 가져오기 (첫 번째만 또는 모든 시리즈)
            if fetch_data and (i == 1):  # 첫 번째만 데이터 표시
                data_info = self._fetch_and_format_data(series.get("id", ""), limit)
                result.append("\n📊 시계열 데이터:")
                result.append(data_info)
            
            result.append("")
        
        return "\n".join(result)
    
    def _extract_series_metadata(self, series: Dict) -> Dict[str, str]:
        """시리즈에서 모든 메타데이터를 있는 그대로 추출"""
        
        # 모든 메타데이터를 있는 그대로 전달
        metadata = {}
        
        # API에서 제공하는 모든 필드를 그대로 추가
        for key, value in series.items():
            if value is not None and str(value).strip():
                metadata[key] = str(value)
        
        return metadata
    
    def _fetch_and_format_data(self, series_id: str, limit: int) -> str:
        """데이터를 가져와서 원본 형태로 포맷팅"""
        
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return "  ⚠️ FRED API 키가 없어 데이터를 가져올 수 없습니다."
        
        observations = self._fetch_series_data(series_id, limit)
        if not observations:
            return "  ⚠️ 데이터를 불러올 수 없습니다."
        
        result = []
        result.append(f"  📅 최근 {min(len(observations), limit)}개 데이터포인트:")
        
        for obs in observations[:limit]:
            # 관측값의 모든 메타데이터를 그대로 표시
            result.append(f"    📅 관측 데이터:")
            for key, value in obs.items():
                if value is not None and str(value).strip():
                    result.append(f"      {key}: {value}")
            result.append("")
        
        return "\n".join(result)