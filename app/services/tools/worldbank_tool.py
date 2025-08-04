"""World Bank Data API Tool"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar, Dict
import requests
from rich.console import Console

console = Console()


class WorldBankInput(BaseModel):
    """Input schema for World Bank data search"""
    indicator: str = Field(..., description="지표 코드 또는 키워드 (예: GDP, NY.GDP.MKTP.CD)")
    country: str = Field(default="KR", description="국가 코드 (기본값: KR=한국)")
    start_year: Optional[int] = Field(default=2019, description="시작 연도")
    end_year: Optional[int] = Field(default=2023, description="종료 연도")


class WorldBankTool(BaseTool):
    """World Bank 데이터 검색 도구"""
    
    name: str = "World Bank Data Search"
    description: str = """
    World Bank의 공식 데이터를 검색합니다.
    GDP, GNI, 인구, 교육, 보건 등 전 세계 국가의 다양한 개발 지표를 제공합니다.
    국가 간 비교와 시계열 분석이 가능합니다.
    API 키 불필요 - 무료로 사용 가능합니다.
    """
    args_schema: Type[BaseModel] = WorldBankInput
    
    # 자주 사용되는 지표 매핑
    INDICATOR_MAP: ClassVar[Dict[str, str]] = {
        "GDP": "NY.GDP.MKTP.CD",  # GDP (current US$)
        "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
        "GDP_PER_CAPITA": "NY.GDP.PCAP.CD",  # GDP per capita (current US$)
        "POPULATION": "SP.POP.TOTL",  # Population, total
        "LIFE_EXPECTANCY": "SP.DYN.LE00.IN",  # Life expectancy at birth
        "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",  # Unemployment, total (% of total labor force)
        "INFLATION": "FP.CPI.TOTL.ZG",  # Inflation, consumer prices (annual %)
        "LITERACY": "SE.ADT.LITR.ZS",  # Literacy rate, adult total (% of people ages 15 and above)
        "INTERNET_USERS": "IT.NET.USER.ZS",  # Individuals using the Internet (% of population)
        "CO2_EMISSIONS": "EN.ATM.CO2E.PC"  # CO2 emissions (metric tons per capita)
    }
    
    def _run(self, indicator: str, country: str = "KR", 
             start_year: Optional[int] = 2019, end_year: Optional[int] = 2023) -> str:
        """World Bank API를 통해 데이터 검색"""
        try:
            # 지표 코드 매핑
            indicator_code = self.INDICATOR_MAP.get(indicator.upper(), indicator)
            
            # World Bank API 엔드포인트 (API 키 불필요)
            base_url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
            
            params = {
                "format": "json",
                "date": f"{start_year}:{end_year}",
                "per_page": 100
            }
            
            headers = {
                "User-Agent": "FactWave/1.0"
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # World Bank API는 두 요소의 리스트를 반환 [메타데이터, 데이터]
                if len(data) > 1 and data[1]:
                    return self._format_worldbank_data(data[1], indicator, country)
                else:
                    return f"'{indicator}'에 대한 데이터를 찾을 수 없습니다."
            else:
                return f"World Bank API 오류: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]World Bank API 요청 오류: {str(e)}[/red]")
            return f"World Bank API 요청 중 오류가 발생했습니다: {str(e)}"
        except Exception as e:
            console.print(f"[red]World Bank 검색 오류: {str(e)}[/red]")
            return f"World Bank 검색 중 오류가 발생했습니다: {str(e)}"
    
    def _format_worldbank_data(self, data: list, indicator: str, country: str) -> str:
        """World Bank API 응답 포맷팅"""
        if not data:
            return "데이터가 없습니다."
        
        # 첫 번째 데이터 항목에서 메타 정보 추출
        first_item = data[0]
        indicator_name = first_item.get("indicator", {}).get("value", indicator)
        country_name = first_item.get("country", {}).get("value", country)
        
        result = f"🌍 World Bank 데이터: {indicator_name}\n"
        result += f"🏳️ 국가: {country_name}\n"
        result += f"📊 지표 코드: {first_item.get('indicator', {}).get('id', 'N/A')}\n\n"
        
        result += "📈 시계열 데이터:\n"
        
        # 연도별로 정렬 (최신 데이터부터)
        sorted_data = sorted([d for d in data if d.get("value") is not None], 
                           key=lambda x: x.get("date", ""), reverse=True)
        
        if not sorted_data:
            result += "  • 이용 가능한 데이터가 없습니다.\n"
        else:
            for item in sorted_data:
                year = item.get("date", "N/A")
                value = item.get("value")
                
                if value is not None:
                    # 숫자 포맷팅
                    if isinstance(value, (int, float)):
                        if value > 1000000000:  # 10억 이상
                            formatted_value = f"{value/1000000000:,.1f}B"
                        elif value > 1000000:  # 100만 이상
                            formatted_value = f"{value/1000000:,.1f}M"
                        elif value > 1000:  # 1000 이상
                            formatted_value = f"{value:,.0f}"
                        else:
                            formatted_value = f"{value:,.2f}"
                    else:
                        formatted_value = str(value)
                    
                    result += f"  • {year}년: {formatted_value}\n"
        
        result += f"\n🔗 출처: World Bank Open Data"
        result += f"\n📝 최종 업데이트: {sorted_data[0].get('date', 'N/A')}년" if sorted_data else ""
        
        # 지표 설명 추가
        result += "\n\n💡 주요 지표 코드:"
        result += "\n  • GDP: NY.GDP.MKTP.CD"
        result += "\n  • GDP 성장률: NY.GDP.MKTP.KD.ZG"
        result += "\n  • 1인당 GDP: NY.GDP.PCAP.CD"
        result += "\n  • 인구: SP.POP.TOTL"
        result += "\n  • 실업률: SL.UEM.TOTL.ZS"
        
        return result