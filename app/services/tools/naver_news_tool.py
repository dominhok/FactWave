"""Naver News API Tool for News Verification"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests
import os
from datetime import datetime, timedelta
from rich.console import Console
import urllib.parse

console = Console()


class NaverNewsInput(BaseModel):
    """Input schema for Naver News search"""
    query: str = Field(..., description="뉴스 검색 키워드")
    sort: str = Field(default="sim", description="정렬 방식 (sim: 정확도순, date: 날짜순)")
    display: int = Field(default=10, description="검색 결과 출력 건수 (최대 100)")
    start: int = Field(default=1, description="검색 시작 위치")


class NaverNewsTool(BaseTool):
    """네이버 뉴스 검색 도구"""
    
    name: str = "Naver News Search"
    description: str = """
    네이버 뉴스 API를 통해 한국 뉴스를 검색합니다.
    최신 뉴스, 관련 뉴스, 특정 주제의 뉴스를 찾을 수 있습니다.
    팩트체크를 위한 다양한 언론사의 보도를 교차 검증할 수 있습니다.
    """
    args_schema: Type[BaseModel] = NaverNewsInput
    
    def _run(self, query: str, sort: str = "sim", display: int = 10, start: int = 1) -> str:
        """네이버 뉴스 API를 통해 뉴스 검색"""
        try:
            # API 인증 정보
            client_id = os.getenv("NAVER_CLIENT_ID")
            client_secret = os.getenv("NAVER_CLIENT_SECRET")
            
            if not client_id or not client_secret:
                return self._get_mock_data(query)
            
            # API 엔드포인트
            url = "https://openapi.naver.com/v1/search/news.json"
            
            # 헤더 설정
            headers = {
                "X-Naver-Client-Id": client_id,
                "X-Naver-Client-Secret": client_secret
            }
            
            # 파라미터 설정
            params = {
                "query": query,
                "sort": sort,
                "display": min(display, 100),  # 최대 100개
                "start": start
            }
            
            # API 요청
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_news_data(data, query)
            elif response.status_code == 401:
                return "네이버 API 인증 오류: Client ID 또는 Secret이 올바르지 않습니다."
            elif response.status_code == 429:
                return "네이버 API 일일 요청 한도 초과 (25,000회/일)"
            else:
                return f"네이버 뉴스 API 오류: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]네이버 뉴스 API 요청 오류: {str(e)}[/red]")
            return self._get_mock_data(query)
        except Exception as e:
            console.print(f"[red]네이버 뉴스 검색 오류: {str(e)}[/red]")
            return f"네이버 뉴스 검색 중 오류가 발생했습니다: {str(e)}"
    
    def _format_news_data(self, data: dict, query: str) -> str:
        """네이버 뉴스 API 응답 포맷팅"""
        total = data.get("total", 0)
        items = data.get("items", [])
        
        if not items:
            return f"📰 '{query}'에 대한 뉴스를 찾을 수 없습니다."
        
        result = f"📰 네이버 뉴스 검색: '{query}'\n"
        result += f"📊 총 {total:,}건 중 {len(items)}건 표시\n\n"
        
        for i, item in enumerate(items, 1):
            # HTML 태그 제거
            title = self._remove_html_tags(item.get("title", ""))
            description = self._remove_html_tags(item.get("description", ""))
            
            result += f"📌 뉴스 {i}: {title}\n"
            
            # 발행일 파싱
            pub_date = item.get("pubDate", "")
            if pub_date:
                try:
                    # RFC 822 형식 파싱
                    dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                    formatted_date = dt.strftime("%Y년 %m월 %d일 %H:%M")
                    result += f"📅 발행일: {formatted_date}\n"
                except:
                    result += f"📅 발행일: {pub_date}\n"
            
            # 요약
            if description:
                desc_preview = description[:150] + "..." if len(description) > 150 else description
                result += f"📝 요약: {desc_preview}\n"
            
            # 링크
            result += f"🔗 원문: {item.get('link', 'N/A')}\n"
            
            result += "-" * 60 + "\n\n"
        
        result += "💡 팁: 여러 언론사의 보도를 교차 검증하여 사실을 확인하세요."
        
        return result
    
    def _remove_html_tags(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean_text = re.sub('<.*?>', '', text)
        # HTML 엔티티 디코딩
        clean_text = clean_text.replace('&quot;', '"')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&nbsp;', ' ')
        return clean_text.strip()
    
    def _get_mock_data(self, query: str) -> str:
        """API 키가 없을 때 사용할 모의 데이터"""
        result = f"📰 네이버 뉴스 검색: '{query}' (모의 데이터)\n\n"
        
        # 예시 뉴스 데이터
        mock_news = [
            {
                "title": f"{query} 관련 최신 동향 분석",
                "date": "2024년 01월 15일",
                "source": "연합뉴스",
                "summary": f"{query}에 대한 전문가들의 분석에 따르면, 최근 동향은 매우 주목할 만하다..."
            },
            {
                "title": f"[팩트체크] {query} 관련 주장 검증",
                "date": "2024년 01월 14일", 
                "source": "한겨레",
                "summary": f"최근 SNS에서 확산된 {query} 관련 주장을 사실 확인한 결과..."
            },
            {
                "title": f"{query}, 새로운 연구 결과 발표",
                "date": "2024년 01월 13일",
                "source": "조선일보",
                "summary": f"국내 연구진이 {query}에 대한 새로운 연구 결과를 발표했다..."
            }
        ]
        
        for i, news in enumerate(mock_news, 1):
            result += f"📌 뉴스 {i}: {news['title']}\n"
            result += f"📅 발행일: {news['date']} | 📰 언론사: {news['source']}\n"
            result += f"📝 요약: {news['summary']}\n"
            result += "-" * 60 + "\n\n"
        
        result += "⚠️ 참고: 실제 API 키가 설정되지 않아 샘플 데이터를 표시합니다.\n"
        result += "네이버 개발자 센터에서 API 키를 발급받으세요: https://developers.naver.com/"
        
        return result