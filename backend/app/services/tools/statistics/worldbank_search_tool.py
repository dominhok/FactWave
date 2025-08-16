"""World Bank Search Tool - 자연어로 WDI 지표 검색"""

import json
import os
from typing import Type, List, Dict, Optional, Tuple
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests
from pathlib import Path
from datetime import datetime


class WorldBankSearchInput(BaseModel):
    query: str = Field(..., description="검색어 (예: unemployment, GDP, poverty)")
    country: str = Field("KR", description="국가 코드 (예: KR, US, CN)")
    fetch_data: bool = Field(True, description="데이터도 함께 가져올지 여부")
    years: int = Field(5, description="최근 몇 년 데이터를 가져올지")


class WorldBankSearchTool(BaseTool):
    """World Bank 자연어 검색 도구 - WDI 지표를 자연어로 검색"""

    name: str = "WorldBank_Natural_Search"
    description: str = (
        "World Bank WDI 지표를 자연어로 검색하고 데이터를 가져옵니다. "
        "예: 'unemployment', 'GDP growth', 'poverty rate', 'life expectancy' 등"
    )
    args_schema: Type[BaseModel] = WorldBankSearchInput
    indicator_mapping: Dict[str, str] = {}  # Pydantic 필드로 선언

    def __init__(self):
        super().__init__()
        self._load_indicator_mapping()
        
    def _load_indicator_mapping(self):
        """WDI 지표 매핑 로드"""
        # llm4data의 wdi2name.json 파일 찾기
        try:
            import llm4data
            llm4data_path = Path(llm4data.__file__).parent
            mapping_file = llm4data_path / "wdi2name.json"
            
            if mapping_file.exists():
                with open(mapping_file, 'r') as f:
                    self.indicator_mapping = json.load(f)
                print(f"✅ {len(self.indicator_mapping)} WDI 지표 매핑 로드 완료")
            else:
                # 폴백: 기본 매핑 사용
                self.indicator_mapping = self._get_default_mapping()
        except:
            # 폴백: 기본 매핑 사용
            self.indicator_mapping = self._get_default_mapping()
    
    def _get_default_mapping(self) -> Dict[str, str]:
        """기본 지표 매핑 (llm4data 없을 때 사용)"""
        return {
            "SL.UEM.TOTL.ZS": "Unemployment, total (% of total labor force) (modeled ILO estimate)",
            "SL.UEM.TOTL.NE.ZS": "Unemployment, total (% of total labor force) (national estimate)",
            "NY.GDP.MKTP.CD": "GDP (current US$)",
            "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
            "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
            "SP.POP.TOTL": "Population, total",
            "SP.DYN.LE00.IN": "Life expectancy at birth, total (years)",
            "SI.POV.DDAY": "Poverty headcount ratio at $1.90 a day (2011 PPP) (% of population)",
            "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
            "SE.PRM.ENRR": "School enrollment, primary (% gross)",
            "SH.XPD.CHEX.PC.CD": "Current health expenditure per capita (current US$)",
            "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)",
            "IT.NET.USER.ZS": "Individuals using the Internet (% of population)"
        }
    
    def _search_indicators(self, query: str, limit: int = 5) -> List[Tuple[str, str, float]]:
        """자연어로 지표 검색"""
        query_lower = query.lower()
        results = []
        
        # 단순 키워드 매칭 + 점수 계산
        for code, name in self.indicator_mapping.items():
            name_lower = name.lower()
            score = 0
            
            # 전체 쿼리가 이름에 포함되면 높은 점수
            if query_lower in name_lower:
                score = 100
            else:
                # 각 단어가 포함되면 점수 추가
                words = query_lower.split()
                for word in words:
                    if word in name_lower:
                        score += 50 / len(words)
            
            if score > 0:
                results.append((code, name, score))
        
        # 점수순 정렬
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]
    
    def _fetch_indicator_data(self, indicator_code: str, country: str, years: int) -> Optional[Dict]:
        """지표 데이터 가져오기"""
        current_year = datetime.now().year
        start_year = current_year - years
        
        url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
        params = {
            "format": "json",
            "date": f"{start_year}:{current_year}",
            "per_page": 100
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 1 and data[1]:
                    return data[1]
        except:
            pass
        
        return None
    
    def _format_data(self, data: List[Dict], indicator_name: str) -> str:
        """데이터와 모든 메타데이터를 있는 그대로 전달"""
        if not data:
            return "  ⚠️ 데이터가 없습니다."
        
        # 유효한 데이터만 필터링하고 연도순 정렬
        valid_data = [d for d in data if d.get("value") is not None]
        valid_data.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        if not valid_data:
            return "  ⚠️ 유효한 데이터가 없습니다."
        
        result = []
        result.append(f"  📅 최근 {min(len(valid_data), 5)}개 데이터포인트:")
        
        # 최대 5개 데이터포인트의 모든 메타데이터 표시
        for item in valid_data[:5]:
            result.append(f"    📊 데이터 항목:")
            for key, value in item.items():
                if value is not None and str(value).strip():
                    # 중첩된 객체 처리
                    if isinstance(value, dict):
                        result.append(f"      {key}:")
                        for sub_key, sub_value in value.items():
                            if sub_value is not None:
                                result.append(f"        {sub_key}: {sub_value}")
                    else:
                        result.append(f"      {key}: {value}")
            result.append("")
        
        return "\n".join(result)
    
    def _run(
        self,
        query: str,
        country: str = "KR",
        fetch_data: bool = True,
        years: int = 5
    ) -> str:
        """검색 실행 - 구조화된 메타데이터와 데이터 함께 제공"""
        
        # 지표 검색
        search_results = self._search_indicators(query, limit=5)
        
        if not search_results:
            return f"❌ '{query}'에 대한 지표를 찾을 수 없습니다."
        
        return self._format_structured_output(query, search_results, country, fetch_data, years)
    
    def _format_structured_output(self, query: str, search_results: List, country: str, fetch_data: bool, years: int) -> str:
        """구조화된 World Bank 출력 형식"""
        
        result = []
        result.append(f"📊 World Bank WDI 검색 결과: '{query}'")
        result.append("━" * 60)
        result.append("📌 출처: 세계은행(World Bank) - World Development Indicators")
        result.append(f"📊 발견된 지표: {len(search_results)}개\n")
        
        for i, (code, name, score) in enumerate(search_results, 1):
            # 지표 메타데이터 표시
            result.append(f"📈 [{i}] {name}")
            result.append("─" * 40)
            result.append(f"  📋 지표코드: {code}")
            result.append(f"  📋 관련도: {score:.0f}%")
            result.append(f"  📋 대상국가: {country}")
            
            # 데이터 가져오기 (첫 번째만 또는 모든 지표)
            if fetch_data and (i == 1):  # 첫 번째만 데이터 표시
                data_info = self._fetch_and_format_data(code, country, years, name)
                result.append("\n📊 지표 데이터:")
                result.append(data_info)
            
            result.append("")
        
        return "\n".join(result)
    
    def _fetch_and_format_data(self, indicator_code: str, country: str, years: int, indicator_name: str) -> str:
        """데이터를 가져와서 원본 형태로 포맷팅"""
        
        data = self._fetch_indicator_data(indicator_code, country, years)
        if not data:
            return "  ⚠️ 데이터를 불러올 수 없습니다."
        
        return self._format_data(data, indicator_name)