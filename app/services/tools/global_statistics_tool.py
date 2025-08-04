"""
Global Statistics Tool - World Bank & OECD API Integration

국제 통계 데이터를 조회하는 통합 도구
- World Bank API: 개발 지표, GDP, 인구, 빈곤율 등
- OECD API: 경제 지표, 교육, 보건, 환경 등
- LLM이 자연어로 국제 통계를 조회할 수 있도록 설계
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import time


class GlobalStatisticsTool:
    """World Bank와 OECD API를 통합한 국제통계 조회 도구"""
    
    def __init__(self):
        self.wb_base_url = "https://api.worldbank.org/v2"
        self.oecd_base_url = "http://stats.oecd.org/SDMX-JSON/data"
        
        # World Bank 주요 지표 매핑
        self.wb_indicators = {
            # 경제 지표
            "gdp": "NY.GDP.MKTP.CD",  # GDP (current US$)
            "gdp_per_capita": "NY.GDP.PCAP.CD",  # GDP per capita (current US$)
            "gdp_growth": "NY.GDP.MKTP.KD.ZG",  # GDP growth (annual %)
            "gni_per_capita": "NY.GNP.PCAP.CD",  # GNI per capita (current US$)
            
            # 인구 지표
            "population": "SP.POP.TOTL",  # Population, total
            "population_growth": "SP.POP.GROW",  # Population growth (annual %)
            "life_expectancy": "SP.DYN.LE00.IN",  # Life expectancy at birth, total (years)
            "fertility_rate": "SP.DYN.TFRT.IN",  # Fertility rate, total (births per woman)
            
            # 사회 지표
            "poverty_rate": "SI.POV.DDAY",  # Poverty headcount ratio at $2.15 a day (2017 PPP)
            "unemployment": "SL.UEM.TOTL.ZS",  # Unemployment, total (% of total labor force)
            "literacy_rate": "SE.ADT.LITR.ZS",  # Literacy rate, adult total (% of people ages 15 and above)
            
            # 환경 지표
            "co2_emissions": "EN.ATM.CO2E.PC",  # CO2 emissions (metric tons per capita)
            "forest_area": "AG.LND.FRST.ZS",  # Forest area (% of land area)
            
            # 보건 지표
            "infant_mortality": "SP.DYN.IMRT.IN",  # Mortality rate, infant (per 1,000 live births)
            "health_expenditure": "SH.XPD.CHEX.GD.ZS",  # Current health expenditure (% of GDP)
        }
        
        # OECD 주요 지표 매핑
        self.oecd_indicators = {
            # 경제 지표
            "inflation": "MEI",  # Main Economic Indicators - Consumer prices
            "interest_rate": "MEI",  # Main Economic Indicators - Interest rates
            "employment": "LFS",  # Labour Force Statistics
            
            # 교육 지표
            "education": "EAG",  # Education at a Glance
            
            # 보건 지표
            "health": "HEALTH",  # Health Statistics
        }
        
        # 국가 코드 매핑 (ISO 3166-1 alpha-3)
        self.country_codes = {
            "korea": "KOR", "south_korea": "KOR", "한국": "KOR",
            "usa": "USA", "united_states": "USA", "미국": "USA",
            "china": "CHN", "중국": "CHN",
            "japan": "JPN", "일본": "JPN",
            "germany": "DEU", "독일": "DEU",
            "france": "FRA", "프랑스": "FRA",
            "uk": "GBR", "united_kingdom": "GBR", "영국": "GBR",
            "italy": "ITA", "이탈리아": "ITA",
            "canada": "CAN", "캐나다": "CAN",
            "australia": "AUS", "호주": "AUS",
        }
    
    def _normalize_country_code(self, country: str) -> str:
        """국가명을 ISO 3166-1 alpha-3 코드로 변환"""
        country_lower = country.lower().replace(" ", "_")
        return self.country_codes.get(country_lower, country.upper())
    
    def _make_wb_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """World Bank API 요청"""
        params.setdefault("format", "json")
        params.setdefault("per_page", "1000")
        
        url = f"{self.wb_base_url}/{endpoint}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # World Bank API는 첫 번째 요소가 메타데이터, 두 번째가 실제 데이터
            if len(data) >= 2 and data[1]:
                return data[1]
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"World Bank API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            return None
    
    def _make_oecd_request(self, dataset: str, dimensions: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """OECD API 요청"""
        if params is None:
            params = {}
        
        url = f"{self.oecd_base_url}/{dataset}/{dimensions}/all"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"OECD API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            return None
    
    def get_wb_indicator(self, indicator: str, countries: Union[str, List[str]], 
                        start_year: int = None, end_year: int = None) -> Optional[pd.DataFrame]:
        """
        World Bank 지표 데이터 조회
        
        Args:
            indicator: 지표 코드 또는 이름
            countries: 국가 코드 또는 국가명 (문자열 또는 리스트)
            start_year: 시작 연도
            end_year: 종료 연도
        """
        
        # 지표 코드 변환
        if indicator in self.wb_indicators:
            indicator_code = self.wb_indicators[indicator]
        else:
            indicator_code = indicator
        
        # 국가 코드 변환
        if isinstance(countries, str):
            countries = [countries]
        
        country_codes = [self._normalize_country_code(c) for c in countries]
        country_str = ";".join(country_codes)
        
        # 날짜 범위 설정 (기본값: 최근 10년)
        if not end_year:
            end_year = datetime.now().year - 1  # 전년도까지
        if not start_year:
            start_year = end_year - 9  # 10년간
        
        endpoint = f"country/{country_str}/indicator/{indicator_code}"
        params = {
            "date": f"{start_year}:{end_year}"
        }
        
        data = self._make_wb_request(endpoint, params)
        
        if not data:
            return None
        
        # DataFrame으로 변환
        df = pd.DataFrame(data)
        
        if df.empty:
            return None
        
        # 필요한 컬럼만 선택하고 정리 (nested dict 처리)
        processed_data = []
        for item in data:
            if item.get("value") is not None:
                processed_data.append({
                    "country": item["country"]["value"] if isinstance(item["country"], dict) else item["country"],
                    "indicator": item["indicator"]["value"] if isinstance(item["indicator"], dict) else item["indicator"],
                    "date": int(item["date"]) if item["date"] else None,
                    "value": float(item["value"]) if item["value"] else None
                })
        
        if not processed_data:
            return None
            
        df = pd.DataFrame(processed_data)
        
        # 정렬
        df = df.sort_values(["country", "date"]).reset_index(drop=True)
        
        return df
    
    def get_oecd_indicator(self, dataset: str, countries: Union[str, List[str]], 
                          subject: str = "", measure: str = "", frequency: str = "A",
                          start_period: str = None, end_period: str = None) -> Optional[pd.DataFrame]:
        """
        OECD 지표 데이터 조회
        
        Args:
            dataset: OECD 데이터셋 코드 (예: "MEI", "LFS")
            countries: 국가 코드 또는 국가명
            subject: 주제 코드
            measure: 측정 코드
            frequency: 주기 (A=연간, Q=분기, M=월간)
            start_period: 시작 기간
            end_period: 종료 기간
        """
        
        # 국가 코드 변환
        if isinstance(countries, str):
            countries = [countries]
        
        country_codes = [self._normalize_country_code(c) for c in countries]
        country_str = "+".join(country_codes)
        
        # 차원 문자열 구성: LOCATION.SUBJECT.MEASURE.FREQUENCY
        dimensions = f"{country_str}.{subject}.{measure}.{frequency}"
        
        # 기간 설정
        params = {}
        if start_period:
            params["startPeriod"] = start_period
        if end_period:
            params["endPeriod"] = end_period
        
        data = self._make_oecd_request(dataset, dimensions, params)
        
        if not data:
            return None
        
        # OECD 데이터 파싱 (SDMX-JSON 형식)
        try:
            dataset_data = data["dataSets"][0]
            structure = data["structure"]
            
            # 간단한 파싱 (실제로는 더 복잡한 구조)
            # 이 부분은 실제 OECD 응답 구조에 따라 수정 필요
            
            return pd.DataFrame()  # 임시 반환
            
        except (KeyError, IndexError) as e:
            print(f"OECD 데이터 파싱 오류: {e}")
            return None
    
    def compare_countries(self, indicator: str, countries: List[str], 
                         years: int = 5) -> Optional[Dict[str, Any]]:
        """
        여러 국가 간 지표 비교
        
        Args:
            indicator: 비교할 지표
            countries: 비교할 국가들
            years: 비교할 연도 수 (최근 N년)
        """
        
        end_year = datetime.now().year - 1
        start_year = end_year - years + 1
        
        # World Bank 데이터로 시도
        df = self.get_wb_indicator(indicator, countries, start_year, end_year)
        
        if df is None or df.empty:
            return {
                "success": False,
                "error": f"'{indicator}' 지표 데이터를 찾을 수 없습니다."
            }
        
        # 국가별 데이터 구성 (전체 기간)
        country_data = {}
        for _, row in df.iterrows():
            country_name = row["country"]
            if country_name not in country_data:
                country_data[country_name] = {
                    "indicator": row["indicator"],
                    "years": [],
                    "values": [],
                    "latest_value": None,
                    "latest_year": None
                }
            
            if row["value"] is not None:
                country_data[country_name]["years"].append(int(row["date"]))
                country_data[country_name]["values"].append(row["value"])
                
                # 최신 값 업데이트
                if (country_data[country_name]["latest_year"] is None or 
                    row["date"] > country_data[country_name]["latest_year"]):
                    country_data[country_name]["latest_value"] = row["value"]
                    country_data[country_name]["latest_year"] = int(row["date"])
        
        # 최신값 기준 순위 계산
        sorted_countries = sorted(
            [(name, data) for name, data in country_data.items() if data["latest_value"] is not None],
            key=lambda x: x[1]["latest_value"],
            reverse=True
        )
        
        return {
            "success": True,
            "indicator": indicator,
            "period": f"{start_year}-{end_year}",
            "countries": country_data,
            "ranking": [{"country": c[0], "value": c[1]["latest_value"], "year": c[1]["latest_year"]} 
                       for c in sorted_countries],
            "raw_data": df.to_dict('records')
        }
    
    def analyze_country_profile(self, country: str) -> Dict[str, Any]:
        """
        특정 국가의 주요 지표 프로필 분석
        
        Args:
            country: 분석할 국가명
        """
        
        # 주요 지표들
        key_indicators = ["gdp_per_capita", "population", "gdp_growth", 
                         "unemployment", "inflation", "life_expectancy"]
        
        results = {}
        
        for indicator in key_indicators:
            try:
                current_year = datetime.now().year - 1
                start_year = current_year - 4  # 최근 5년
                df = self.get_wb_indicator(indicator, [country], start_year, current_year)
                if df is not None and not df.empty:
                    latest = df.iloc[-1]
                    results[indicator] = {
                        "value": latest["value"],
                        "year": int(latest["date"]),
                        "indicator_name": latest["indicator"]
                    }
                time.sleep(0.1)  # API 호출 간격 조절
            except Exception as e:
                print(f"{indicator} 조회 실패: {e}")
                continue
        
        return {
            "success": True,
            "country": country,
            "indicators": results,
            "analysis_date": datetime.now().isoformat()
        }


# CrewAI Tool 래퍼
def create_global_statistics_tool():
    """CrewAI에서 사용할 Global Statistics 도구 생성"""
    
    tool = GlobalStatisticsTool()
    
    def global_statistics_analysis(query: str, countries: str = "korea", 
                                 indicator: str = "gdp_per_capita", years: int = 5,
                                 start_year: int = None, end_year: int = None) -> str:
        """
        국제 통계 데이터 분석 - LLM이 자연어로 통계를 조회할 수 있는 통합 도구
        
        World Bank 데이터를 활용한 국제 통계 분석
        
        Args:
            query: 분석 요청 (자연어 가능, 예: "한국과 일본의 GDP 비교", "미국 경제 프로필", "인구 증가율 트렌드")
            countries: 분석할 국가들 (쉼표로 구분, 예: "korea,japan,usa")
            indicator: 분석할 지표 (예: "gdp_per_capita", "population", "unemployment", "life_expectancy")
            years: 분석 기간 (최근 N년, 기본값: 5)
            start_year: 시작 연도 (선택사항)
            end_year: 종료 연도 (선택사항)
        
        Available indicators:
            - gdp, gdp_per_capita, gdp_growth, gni_per_capita
            - population, population_growth, life_expectancy, fertility_rate
            - poverty_rate, unemployment, literacy_rate
            - co2_emissions, forest_area
            - infant_mortality, health_expenditure
        
        Returns:
            str: 분석 결과 (JSON 형식으로 구조화된 데이터)
        """
        
        try:
            countries_list = [c.strip() for c in countries.split(",")]
            
            # 자연어 질의 처리
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["compare", "comparison", "비교", "vs"]):
                # 국가 간 비교 분석
                result = tool.compare_countries(indicator, countries_list, years)
                result["analysis_type"] = "country_comparison"
                
            elif any(word in query_lower for word in ["profile", "프로필", "overview", "개요"]):
                # 국가 프로필 분석
                if len(countries_list) == 1:
                    result = tool.analyze_country_profile(countries_list[0])
                    result["analysis_type"] = "country_profile"
                else:
                    result = {"success": False, "error": "프로필 분석은 한 국가만 선택해주세요."}
                    
            elif any(word in query_lower for word in ["trend", "트렌드", "변화", "변동"]):
                # 트렌드 분석 (시계열 데이터)
                if start_year and end_year:
                    df = tool.get_wb_indicator(indicator, countries_list, start_year, end_year)
                else:
                    df = tool.get_wb_indicator(indicator, countries_list, years=years)
                
                if df is not None and not df.empty:
                    result = {
                        "success": True,
                        "analysis_type": "trend_analysis",
                        "indicator": indicator,
                        "countries": countries_list,
                        "data": df.to_dict('records'),
                        "summary": f"{len(df)} data points across {df['country'].nunique()} countries"
                    }
                else:
                    result = {"success": False, "error": "트렌드 데이터를 찾을 수 없습니다."}
                    
            else:
                # 기본적으로 단일 지표 조회
                if start_year and end_year:
                    df = tool.get_wb_indicator(indicator, countries_list, start_year, end_year)
                else:
                    df = tool.get_wb_indicator(indicator, countries_list, years=years)
                
                if df is not None and not df.empty:
                    result = {
                        "success": True,
                        "analysis_type": "data_query",
                        "indicator": indicator,
                        "countries": countries_list,
                        "data": df.to_dict('records'),
                        "latest_values": df.groupby('country').last().to_dict('index')
                    }
                else:
                    result = {"success": False, "error": "데이터를 찾을 수 없습니다."}
                
            return json.dumps(result, ensure_ascii=False, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"분석 중 오류 발생: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    return global_statistics_analysis


if __name__ == "__main__":
    # 테스트 코드
    tool = GlobalStatisticsTool()
    
    print("=== Global Statistics Tool 테스트 ===")
    
    # 한국 GDP 데이터 테스트
    print("\n1. 한국 GDP 데이터 조회")
    df = tool.get_wb_indicator("gdp_per_capita", "korea", 2020, 2023)
    if df is not None:
        print(f"✅ 성공: {len(df)}개 데이터 조회")
        print(df.head())
    else:
        print("❌ 실패")
    
    # 국가 비교 테스트
    print("\n2. 국가 간 GDP 비교")
    result = tool.compare_countries("gdp_per_capita", ["korea", "japan", "usa"])
    if result["success"]:
        print("✅ 비교 분석 성공")
        for country, data in result["countries"].items():
            print(f"  {country}: ${data['value']:,.0f} ({data['year']})")
    else:
        print(f"❌ 실패: {result['error']}")