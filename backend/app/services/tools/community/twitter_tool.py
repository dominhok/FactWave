"""Twitter/X Community Tool using twscrape - 트위터 여론 수집"""

import os
import asyncio
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from datetime import datetime, timezone
from rich.console import Console

console = Console()

# twscrape import는 설치 후 사용
try:
    from twscrape import API, gather
    TWSCRAPE_AVAILABLE = True
except ImportError:
    TWSCRAPE_AVAILABLE = False
    console.print("[yellow]twscrape not installed. Install with: pip install twscrape[/yellow]")


class TwitterSearchInput(BaseModel):
    """Twitter/X 검색 입력 스키마"""
    query: str = Field(..., description="검색 키워드 또는 해시태그")
    limit: Optional[int] = Field(30, description="검색 결과 수 (최대 100)")
    language: Optional[str] = Field("ko", description="언어 코드 (ko, en, ja 등)")
    include_replies: Optional[bool] = Field(False, description="답글 포함 여부")


class TwitterTool(BaseTool):
    """Twitter/X 커뮤니티 여론 수집 도구"""
    
    name: str = "Twitter/X Community Search"
    description: str = """
    Twitter/X에서 실시간 여론과 트렌드를 수집합니다.
    해시태그, 키워드를 통해 대중의 실시간 반응과 의견을 파악할 수 있습니다.
    팩트체크를 위한 소셜 미디어 여론과 실시간 반응을 분석합니다.
    주의: 계정 인증이 필요하며, API 제한이 있을 수 있습니다.
    """
    args_schema: Type[BaseModel] = TwitterSearchInput
    
    def __init__(self):
        super().__init__()
        self._api = None  # Use private attribute to avoid conflicts
        self._initialize_api()
    
    def _initialize_api(self):
        """twscrape API 초기화 - 기존 accounts.db 사용"""
        if not TWSCRAPE_AVAILABLE:
            return
        
        try:
            # accounts.db가 이미 설정되어 있으면 그대로 사용
            self._api = API()  # 기본적으로 accounts.db 파일 사용
            console.print("[green]Twitter API 초기화 완료 (accounts.db 사용)[/green]")
        except Exception as e:
            console.print(f"[red]Twitter API 초기화 오류: {str(e)}[/red]")
    
    def _run(
        self,
        query: str,
        limit: Optional[int] = 30,
        language: Optional[str] = "ko",
        include_replies: Optional[bool] = False
    ) -> str:
        """Twitter/X 검색 수행"""
        
        if not TWSCRAPE_AVAILABLE:
            return self._get_setup_instructions()
        
        if not self._api:
            return self._get_mock_data(query)
        
        try:
            # 동기적으로 비동기 함수 실행
            tweets = asyncio.run(self._search_tweets(query, limit, language, include_replies))
            return self._format_twitter_data(tweets, query)
            
        except Exception as e:
            console.print(f"[red]Twitter 검색 오류: {str(e)}[/red]")
            return self._get_mock_data(query)
    
    async def _search_tweets(self, query: str, limit: int, language: str, include_replies: bool) -> List:
        """비동기 트윗 검색"""
        tweets = []
        
        # 언어 필터 추가
        search_query = f"{query} lang:{language}"
        if not include_replies:
            search_query += " -filter:replies"
        
        # 검색 수행
        async for tweet in self._api.search(search_query, limit=min(limit, 100)):
            tweets.append(tweet)
            if len(tweets) >= limit:
                break
        
        return tweets
    
    def _format_twitter_data(self, tweets: List, query: str) -> str:
        """Twitter 검색 결과 포맷팅"""
        if not tweets:
            return f"🔍 '{query}'에 대한 트윗을 찾을 수 없습니다."
        
        result = f"🐦 Twitter/X 검색: '{query}'\n"
        result += f"📊 총 {len(tweets)}개 트윗 분석\n\n"
        
        # 전체 통계
        total_likes = sum(tweet.likeCount for tweet in tweets)
        total_retweets = sum(tweet.retweetCount for tweet in tweets)
        total_replies = sum(tweet.replyCount for tweet in tweets)
        
        result += f"📈 커뮤니티 반응 요약:\n"
        result += f"  • 총 좋아요: {total_likes:,}\n"
        result += f"  • 총 리트윗: {total_retweets:,}\n"
        result += f"  • 총 답글: {total_replies:,}\n"
        result += f"  • 평균 참여율: {(total_likes + total_retweets + total_replies) / len(tweets):.1f}\n\n"
        
        # 주요 트윗
        for i, tweet in enumerate(tweets, 1):
            result += f"📌 [{i}/{len(tweets)}] @{tweet.user.username}\n"
            
            # 인증 마크
            # 사용자 정보 (속성 이름이 다를 수 있음)
            if hasattr(tweet.user, 'verified') and tweet.user.verified:
                result += "  ✅ 인증됨\n"
            elif hasattr(tweet.user, 'followersCount') and tweet.user.followersCount > 10000:
                result += f"  (팔로워 {tweet.user.followersCount:,})\n"
            else:
                result += "\n"
            
            # 트윗 내용
            content = tweet.rawContent[:280] if len(tweet.rawContent) > 280 else tweet.rawContent
            result += f"  💬 {content}\n"
            
            # 참여도
            result += f"  ❤️ {tweet.likeCount:,} | 🔁 {tweet.retweetCount:,} | 💬 {tweet.replyCount:,}\n"
            
            # 시간 정보
            created_at = tweet.date
            now = datetime.now(timezone.utc)
            hours_ago = (now - created_at).total_seconds() / 3600
            
            if hours_ago < 1:
                minutes_ago = int(hours_ago * 60)
                result += f"  ⏰ {minutes_ago}분 전\n"
            elif hours_ago < 24:
                result += f"  ⏰ {int(hours_ago)}시간 전\n"
            else:
                days_ago = int(hours_ago / 24)
                result += f"  📅 {days_ago}일 전\n"
            
            # 링크
            result += f"  🔗 https://twitter.com/{tweet.user.username}/status/{tweet.id}\n"
            
            result += "\n"
        
        # 트렌드 분석
        result += self._analyze_trends(tweets)
        
        result += f"\n💡 팁: 소셜 미디어 여론은 빠르게 변하므로 시간대별 추이를 확인하세요."
        
        return result
    
    def _analyze_trends(self, tweets) -> str:
        """트렌드 및 감정 분석"""
        result = "\n🎭 트렌드 분석:\n"
        
        # 참여도 기준 분석
        high_engagement = [t for t in tweets if (t.likeCount + t.retweetCount) > 100]
        
        if len(high_engagement) > len(tweets) * 0.3:
            result += "  • 높은 관심도 주제 🔥\n"
        else:
            result += "  • 일반적 관심도 📊\n"
        
        # 시간대 분석
        recent_tweets = [t for t in tweets if (datetime.now(timezone.utc) - t.date).total_seconds() < 3600]
        if len(recent_tweets) > len(tweets) * 0.5:
            result += "  • 현재 활발히 논의 중 ⚡\n"
        else:
            result += "  • 지속적인 논의 주제 📝\n"
        
        # 해시태그 추출 (상위 5개)
        hashtags = {}
        for tweet in tweets:
            for tag in tweet.hashtags or []:
                hashtags[tag] = hashtags.get(tag, 0) + 1
        
        if hashtags:
            sorted_tags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:5]
            result += "  • 주요 해시태그: "
            result += ", ".join([f"#{tag[0]}" for tag in sorted_tags])
            result += "\n"
        
        return result
    
    def _get_setup_instructions(self) -> str:
        """twscrape 설치 안내"""
        return """❌ twscrape가 설치되지 않았습니다.
        
설치 방법:
1. pip install twscrape

2. Twitter 계정 준비 (여러 개 권장)
   - 각 계정에 이메일 연결 필요
   - 2FA 비활성화 권장

3. .env 파일에 계정 정보 추가:
   TWITTER_ACCOUNTS=username:password:email:email_password;username2:password2:email2:email_password2

4. 첫 실행 시 계정 로그인 필요 (자동 처리됨)

⚠️ 주의사항:
- Twitter/X의 스크래핑 정책 변경으로 계정이 제한될 수 있음
- 여러 계정 사용으로 리스크 분산 권장
- 과도한 요청 자제"""
    
    def _get_mock_data(self, query: str) -> str:
        """API 설정이 없을 때 반환할 메시지"""
        return f"""❌ Twitter/X API가 설정되지 않았습니다.

현재 Twitter/X 접근 옵션:
1. twscrape 설치 및 계정 설정 (위 설명 참조)
2. 공식 Twitter API v2 (유료, $100/월부터)
3. 다른 소셜 플랫폼 활용 (Reddit, Mastodon 등)

검색하려던 키워드: '{query}'

💡 대안: 네이버 뉴스나 YouTube 댓글로 한국 여론을 파악할 수 있습니다."""