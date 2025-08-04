# API Requirements and Tool Documentation

## 현재 구현된 도구들

### 1. Academic Agent Tools

#### Wikipedia Search Tool 🌐
- **API 키 필요**: ❌ 불필요
- **Rate Limit**: 5000 requests/hour
- **공식 문서**: https://www.mediawiki.org/wiki/API:Main_page
- **상태**: ✅ 구현 완료

#### Semantic Scholar Tool 🎓
- **API 키 필요**: ❌ 불필요 
- **Rate Limit**: 100 requests/minute
- **공식 문서**: https://api.semanticscholar.org/
- **상태**: ✅ 구현 완료

#### ArXiv Search Tool 📄
- **API 키 필요**: ❌ 불필요
- **Rate Limit**: 3 requests/second (권장)
- **공식 문서**: https://arxiv.org/help/api/
- **상태**: ✅ 구현 완료

#### KOSIS Statistics Tool 📊
- **API 키 필요**: ✅ 필요 (현재 모의 데이터 사용)
- **신청 방법**: https://kosis.kr/openapi/index/index.jsp
- **Rate Limit**: 일일 요청 제한 있음
- **상태**: ✅ 구현 완료 (모의 데이터)

#### World Bank Data Tool 🌍
- **API 키 필요**: ❌ 불필요
- **Rate Limit**: 매우 관대함
- **공식 문서**: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- **상태**: ✅ 구현 완료

## 추가 구현 가능한 도구들

### News Verification Agent Tools

#### 1. Naver News API 📰
- **API 키 필요**: ✅ 필요
- **신청**: https://developers.naver.com/apps/
- **Rate Limit**: 25,000 requests/day
- **용도**: 한국 뉴스 검색 및 검증
- **환경변수**: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`

#### 2. Google Fact Check Tools API 🔍
- **API 키 필요**: ✅ 필요
- **신청**: Google Cloud Console
- **Rate Limit**: 10,000 requests/day (무료)
- **용도**: 팩트체크 주장 검색
- **환경변수**: `GOOGLE_API_KEY`

#### 3. NewsAPI.org 🌐
- **API 키 필요**: ✅ 필요
- **신청**: https://newsapi.org/register
- **Rate Limit**: 1,000 requests/day (무료)
- **용도**: 국제 뉴스 검색
- **환경변수**: `NEWS_API_KEY`

### Social Intelligence Agent Tools

#### 1. YouTube Data API 📺
- **API 키 필요**: ✅ 필요
- **신청**: Google Cloud Console
- **Rate Limit**: 10,000 units/day
- **용도**: 비디오 댓글, 트렌드 분석
- **환경변수**: `YOUTUBE_API_KEY`

#### 2. Reddit API 🤖
- **API 키 필요**: ✅ 필요 (OAuth)
- **신청**: https://www.reddit.com/prefs/apps
- **Rate Limit**: 60 requests/minute
- **용도**: 커뮤니티 여론 분석
- **환경변수**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`

### 추가 통계 도구들

#### 1. FRED (Federal Reserve Economic Data) 📈
- **API 키 필요**: ✅ 필요
- **신청**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Rate Limit**: 120 requests/minute
- **용도**: 미국 경제 지표
- **환경변수**: `FRED_API_KEY`

#### 2. OpenWeatherMap API 🌤️
- **API 키 필요**: ✅ 필요
- **신청**: https://openweathermap.org/api
- **Rate Limit**: 60 calls/minute (무료)
- **용도**: 날씨 관련 팩트체크
- **환경변수**: `OPENWEATHER_API_KEY`

#### 3. COVID-19 API 🦠
- **API 키 필요**: ❌ 불필요
- **API**: https://covid19api.com/
- **Rate Limit**: 관대함
- **용도**: COVID-19 통계 검증

## 환경변수 설정 예시

```bash
# .env 파일

# 현재 사용 중
UPSTAGE_API_KEY=your_upstage_key

# 추가 필요 (옵션)
KOSIS_API_KEY=your_kosis_key
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
GOOGLE_API_KEY=your_google_key
NEWS_API_KEY=your_newsapi_key
YOUTUBE_API_KEY=your_youtube_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret
FRED_API_KEY=your_fred_key
OPENWEATHER_API_KEY=your_openweather_key
```

## 우선순위 추천

1. **높음**: Naver News API - 한국 뉴스 팩트체크에 필수
2. **높음**: Google Fact Check Tools - 기존 팩트체크 데이터 활용
3. **중간**: YouTube Data API - 소셜 미디어 트렌드 분석
4. **중간**: FRED API - 경제 지표 검증
5. **낮음**: Reddit API, OpenWeatherMap - 특수 목적

## 구현 가이드

각 도구는 다음 패턴을 따라 구현:

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import requests
import os

class ToolNameInput(BaseModel):
    """Input schema for tool"""
    query: str = Field(..., description="검색 쿼리")
    # 추가 파라미터

class ToolNameTool(BaseTool):
    """도구 설명"""
    
    name: str = "Tool Name"
    description: str = """도구 설명"""
    args_schema: Type[BaseModel] = ToolNameInput
    
    def _run(self, query: str, **kwargs) -> str:
        """도구 실행 로직"""
        api_key = os.getenv("API_KEY_NAME")
        if not api_key:
            return "API 키가 설정되지 않았습니다."
        
        # API 호출 및 처리
        # ...
        
        return formatted_result
```