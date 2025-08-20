"""YouTube Community Tool - 유튜브 영상 검색 및 댓글 여론 분석"""

import os
from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from datetime import datetime
import re
from rich.console import Console

console = Console()

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    HttpError = Exception  # Fallback for when library is not installed
    console.print("[yellow]google-api-python-client not installed. Install with: pip install google-api-python-client[/yellow]")


class YouTubeSearchInput(BaseModel):
    """YouTube 검색 입력 스키마"""
    query: str = Field(..., description="검색할 키워드 또는 주제")
    max_videos: Optional[int] = Field(3, description="분석할 영상 수 (최대 5개)")
    max_comments: Optional[int] = Field(50, description="영상당 수집할 댓글 수 (최대 100개)")
    language: Optional[str] = Field("ko", description="선호 언어 코드 (ko, en 등)")


class YouTubeTool(BaseTool):
    """YouTube 커뮤니티 여론 수집 도구"""
    
    name: str = "YouTube Community Analysis"
    description: str = """
    YouTube에서 영상을 검색하고 댓글을 수집하여 여론을 분석합니다.
    자연어 검색으로 관련 영상을 찾고, 인기 댓글을 통해 대중의 의견을 파악합니다.
    팩트체크를 위한 영상 내용과 시청자 반응을 종합적으로 분석합니다.
    """
    args_schema: Type[BaseModel] = YouTubeSearchInput
    
    def __init__(self):
        super().__init__()
        self._youtube = None  # Private attribute to store YouTube service
    
    def _initialize_youtube(self):
        """YouTube API 초기화"""
        if not YOUTUBE_API_AVAILABLE:
            return None
        
        # Google API Key (YouTube Data API v3)
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            console.print("[yellow]GOOGLE_API_KEY not found in environment[/yellow]")
            return None
        
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            console.print("[green]YouTube API 초기화 성공[/green]")
            return youtube
        except Exception as e:
            console.print(f"[red]YouTube API 초기화 실패: {str(e)}[/red]")
            return None
    
    def _run(
        self,
        query: str,
        max_videos: Optional[int] = 3,
        max_comments: Optional[int] = 50,
        language: Optional[str] = "ko"
    ) -> str:
        """YouTube 검색 및 댓글 분석 수행"""
        
        if not YOUTUBE_API_AVAILABLE:
            return self._get_setup_instructions()
        
        # Initialize YouTube service if not already done
        if not self._youtube:
            self._youtube = self._initialize_youtube()
        
        if not self._youtube:
            return self._get_api_key_instructions()
        
        try:
            # 1. 영상 검색
            videos = self._search_videos(query, max_videos, language)
            if not videos:
                return f"❌ '{query}'에 대한 YouTube 영상을 찾을 수 없습니다."
            
            # 2. 각 영상에 대한 댓글 수집
            result = f"🎥 YouTube 분석: '{query}'\n"
            result += f"📊 총 {len(videos)}개 영상 분석\n"
            result += "=" * 50 + "\n\n"
            
            for idx, video in enumerate(videos, 1):
                result += self._analyze_video_with_comments(video, idx, max_comments)
                result += "\n" + "-" * 40 + "\n\n"
            
            result += self._generate_summary(query, videos)
            
            return result
            
        except HttpError as e:
            if e.resp.status == 403:
                return "❌ YouTube API 할당량 초과. 나중에 다시 시도하세요."
            else:
                console.print(f"[red]YouTube API 오류: {str(e)}[/red]")
                return f"❌ YouTube API 오류: {str(e)}"
        except Exception as e:
            console.print(f"[red]YouTube 검색 오류: {str(e)}[/red]")
            return f"❌ YouTube 검색 오류: {str(e)}"
    
    def _search_videos(self, query: str, max_videos: int, language: str) -> List[Dict[str, Any]]:
        """YouTube 영상 검색"""
        try:
            search_response = self._youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=min(max_videos, 5),
                relevanceLanguage=language,
                order='relevance'
            ).execute()
            
            # 영상 ID 수집
            video_ids = []
            video_snippets = {}
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_ids.append(video_id)
                video_snippets[video_id] = item['snippet']
            
            if not video_ids:
                return []
            
            # 배치로 영상 상세 정보 가져오기 (API 호출 최적화)
            video_details = self._youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)  # 한 번의 API 호출로 모든 영상 정보 가져오기
            ).execute()
            
            videos = []
            for video_info in video_details.get('items', []):
                video_id = video_info['id']
                videos.append({
                    'id': video_id,
                    'title': video_info['snippet']['title'],
                    'channel': video_info['snippet']['channelTitle'],
                    'published': video_info['snippet']['publishedAt'],
                    'description': video_info['snippet'].get('description', '')[:500],
                    'statistics': video_info.get('statistics', {}),
                    'duration': video_info['contentDetails'].get('duration', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
            
            return videos
            
        except Exception as e:
            console.print(f"[red]영상 검색 오류: {str(e)}[/red]")
            return []
    
    def _get_video_comments(self, video_id: str, max_comments: int) -> List[Dict[str, Any]]:
        """영상 댓글 수집 (좋아요 순으로 정렬)"""
        try:
            comments = []
            
            # 댓글 스레드 가져오기 (인기순)
            comment_response = self._youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=min(max_comments, 100),
                order='relevance',  # 관련성/인기순
                textFormat='plainText'
            ).execute()
            
            for item in comment_response.get('items', []):
                top_comment = item['snippet']['topLevelComment']['snippet']
                
                comment_data = {
                    'author': top_comment['authorDisplayName'],
                    'text': top_comment['textOriginal'],
                    'likes': top_comment.get('likeCount', 0),
                    'published': top_comment['publishedAt'],
                    'replies': item['snippet'].get('totalReplyCount', 0)
                }
                
                comments.append(comment_data)
                
                # 인기 답글도 포함 (있을 경우)
                if 'replies' in item and item['replies']['comments']:
                    for reply in item['replies']['comments'][:2]:  # 상위 2개 답글만
                        reply_snippet = reply['snippet']
                        if reply_snippet.get('likeCount', 0) > 10:  # 좋아요 10개 이상인 답글만
                            comments.append({
                                'author': reply_snippet['authorDisplayName'],
                                'text': "ㄴ " + reply_snippet['textOriginal'],
                                'likes': reply_snippet.get('likeCount', 0),
                                'published': reply_snippet['publishedAt'],
                                'replies': 0
                            })
            
            # 좋아요 순으로 정렬
            comments.sort(key=lambda x: x['likes'], reverse=True)
            
            return comments[:max_comments]
            
        except HttpError as e:
            if e.resp.status == 403:
                # 댓글이 비활성화된 경우 처리
                console.print(f"[yellow]영상 {video_id}: 댓글이 비활성화되었거나 접근 불가[/yellow]")
                return []
            else:
                console.print(f"[red]댓글 수집 오류: {str(e)}[/red]")
                return []
        except Exception as e:
            console.print(f"[red]댓글 수집 오류: {str(e)}[/red]")
            return []
    
    def _analyze_video_with_comments(self, video: Dict[str, Any], idx: int, max_comments: int) -> str:
        """영상 정보와 댓글 분석"""
        result = f"📹 [{idx}] {video['title']}\n"
        result += f"   채널: {video['channel']}\n"
        
        # 통계 정보
        stats = video['statistics']
        view_count = int(stats.get('viewCount', 0))
        like_count = int(stats.get('likeCount', 0))
        comment_count = int(stats.get('commentCount', 0))
        
        result += f"   조회수: {view_count:,} | 좋아요: {like_count:,} | 댓글: {comment_count:,}\n"
        
        # 영상 설명 (첫 200자)
        desc = video['description'][:200].replace('\n', ' ')
        if desc:
            result += f"   설명: {desc}...\n"
        
        result += f"   URL: {video['url']}\n\n"
        
        # 댓글 수집 및 분석
        comments = self._get_video_comments(video['id'], max_comments)
        
        if comments:
            result += f"   💬 주요 댓글 ({len(comments)}개 수집):\n\n"
            
            # 상위 10개 댓글만 표시
            for i, comment in enumerate(comments[:10], 1):
                # 댓글 텍스트 정리 (최대 200자)
                text = comment['text'].replace('\n', ' ')
                if len(text) > 200:
                    text = text[:197] + "..."
                
                result += f"   [{i}] {text}\n"
                result += f"       👍 {comment['likes']:,}"
                
                if comment['replies'] > 0:
                    result += f" | 답글 {comment['replies']}개"
                
                result += "\n\n"
            
            # 댓글 톤 요약
            result += self._analyze_comment_tone(comments)
        else:
            result += "   💬 댓글을 가져올 수 없거나 댓글이 없습니다.\n"
        
        return result
    
    def _analyze_comment_tone(self, comments: List[Dict[str, Any]]) -> str:
        """댓글 전반적인 톤 분석"""
        if not comments:
            return ""
        
        result = "\n   📊 댓글 여론 특징:\n"
        
        # 평균 좋아요 수
        avg_likes = sum(c['likes'] for c in comments) / len(comments)
        result += f"   • 평균 좋아요: {avg_likes:.1f}개\n"
        
        # 가장 인기 있는 댓글
        top_comment = comments[0] if comments else None
        if top_comment and top_comment['likes'] > 100:
            result += f"   • 최다 좋아요 ({top_comment['likes']:,}개) 댓글 주목\n"
        
        # 댓글 활발도
        total_replies = sum(c.get('replies', 0) for c in comments[:10])
        if total_replies > 50:
            result += f"   • 활발한 토론 진행 중 (답글 {total_replies}개)\n"
        
        # 댓글 텍스트 패턴 분석
        all_text = ' '.join(c['text'] for c in comments[:20])
        
        # 감정 표현 키워드
        positive_words = ['좋', '최고', '대단', '멋', '응원', '감사', '사랑', '재밌', '재미있']
        negative_words = ['싫', '최악', '별로', '아니', '실망', '화나', '짜증', '거짓', '가짜']
        question_marks = all_text.count('?')
        exclamation_marks = all_text.count('!')
        
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        if positive_count > negative_count * 2:
            result += "   • 전반적으로 긍정적인 반응\n"
        elif negative_count > positive_count * 2:
            result += "   • 비판적이거나 부정적인 의견 다수\n"
        elif question_marks > 10:
            result += "   • 의문과 질문이 많은 상황\n"
        elif exclamation_marks > 15:
            result += "   • 감정적이고 열정적인 반응\n"
        
        return result
    
    def _generate_summary(self, query: str, videos: List[Dict[str, Any]]) -> str:
        """전체 분석 요약"""
        result = "\n" + "=" * 50 + "\n"
        result += f"📌 '{query}' YouTube 여론 종합:\n\n"
        
        # 전체 통계
        total_views = sum(int(v['statistics'].get('viewCount', 0)) for v in videos)
        total_comments = sum(int(v['statistics'].get('commentCount', 0)) for v in videos)
        
        result += f"• 분석 영상 {len(videos)}개의 총 조회수: {total_views:,}\n"
        result += f"• 전체 댓글 수: {total_comments:,}\n"
        
        # 가장 인기 있는 영상
        most_viewed = max(videos, key=lambda v: int(v['statistics'].get('viewCount', 0)))
        result += f"• 최다 조회 영상: {most_viewed['title']}\n"
        
        result += "\n💡 LLM이 댓글 내용을 종합 분석하여 여론을 파악합니다.\n"
        
        return result
    
    def _get_setup_instructions(self) -> str:
        """API 설치 안내"""
        return """❌ google-api-python-client가 설치되지 않았습니다.

설치 방법:
pip install google-api-python-client

또는 UV 사용 시:
uv pip install google-api-python-client"""
    
    def _get_api_key_instructions(self) -> str:
        """API 키 설정 안내"""
        return """❌ YouTube Data API 키가 설정되지 않았습니다.

설정 방법:
1. Google Cloud Console에서 프로젝트 생성
   https://console.cloud.google.com/

2. YouTube Data API v3 활성화

3. API 키 생성 (Credentials 메뉴)

4. .env 파일에 추가:
   GOOGLE_API_KEY=your_api_key_here
   또는
   YOUTUBE_API_KEY=your_api_key_here

5. API 키 제한 설정 권장:
   - YouTube Data API v3 허용
   - Google Fact Check API 허용 (동일 키 사용 가능)
   - IP 주소 또는 HTTP 참조자 제한

⚠️ 무료 할당량: 일일 10,000 유닛
   - 검색: 100 유닛
   - 댓글 조회: 1 유닛"""