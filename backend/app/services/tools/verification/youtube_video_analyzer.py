"""YouTube Video Analyzer using Gemini API - 유튜브 영상 내용 분석 도구"""

import os
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from rich.console import Console
import re

console = Console()


class YouTubeVideoAnalyzer:
    """Gemini API를 사용한 YouTube 영상 내용 분석기"""
    
    def __init__(self):
        """Initialize Gemini API client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # google.genai Client 생성
        self.client = genai.Client(api_key=self.api_key)
        console.print("[green]Gemini API client initialized for YouTube video analysis[/green]")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 video ID 추출"""
        patterns = [
            r'(?:v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v=|watch\?.+&v=)([^#\&\?\/\s]{11})',
            r'(?:youtube\.com\/watch\?.*v=)([^#\&\?\/\s]{11})',
            r'(?:youtu\.be\/)([^#\&\?\/\s]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def analyze_video(self, youtube_url: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        YouTube 영상 분석 수행
        
        Args:
            youtube_url: YouTube 영상 URL
            analysis_type: 분석 유형 ('summary', 'transcript', 'factcheck', 'comprehensive')
        
        Returns:
            분석 결과 딕셔너리
        """
        try:
            console.print(f"[blue]Analyzing YouTube video: {youtube_url}[/blue]")
            
            # 분석 유형별 프롬프트 설정
            prompts = {
                "content_type": """이 YouTube 영상의 콘텐츠 유형과 목적을 분석해주세요. 한국어로 답변해주세요.
                
                팩트체킹 필요성 판단 기준:
                - 팩트체킹 불필요: 뮤직비디오, 음악 콘텐츠, 예능 프로그램만 해당
                - 팩트체킹 필요: 위 3가지를 제외한 모든 영상 (뉴스, 다큐멘터리, 교육, 브이로그, 게임 리뷰, 제품 리뷰, 정치, 경제, 과학, 역사 등 정보를 전달하는 모든 콘텐츠)
                
                다음 형식으로 정확히 답변해주세요:
                콘텐츠 유형: [뉴스/다큐멘터리/교육/예능/뮤직비디오/브이로그/게임/기타 중 하나]
                주요 목적: [정보전달/주장설득/오락/예술표현/개인기록/상업광고 중 하나]
                팩트체킹 필요성: [예/아니오]
                이유: [팩트체킹 필요성 판단 근거 1-2문장]
                """,
                
                "summary": """이 영상을 한국어로 요약해주세요. 다음 형식으로 답변해주세요:
                
                제목: [영상 제목]
                주요 내용: [3-5개 핵심 포인트]
                결론: [핵심 메시지 1-2문장]
                """,
                
                "transcript": """이 영상의 주요 발언이나 내레이션을 한국어로 추출해주세요.
                시간대와 함께 중요한 발언들을 나열해주세요.""",
                
                "factcheck": """이 영상에서 제시된 주장들을 분석해주세요. 한국어로 답변해주세요.
                
                다음 기준으로 주장들을 선별하여 나열해주세요:
                - 구체적인 수치나 통계를 인용하는 주장
                - 인과관계를 단정적으로 설명하는 주장
                - 역사적 사실이나 과학적 사실을 언급하는 주장
                - 특정 인물이나 기관의 발언을 인용하는 주장
                - 미래 예측이나 단정적 전망을 제시하는 주장
                - 일반화나 과장된 표현을 사용하는 주장
                
                다음 형식으로 답변해주세요:
                1. 주요 주장: [위 기준에 해당하는 핵심 주장들]
                2. 검증 필요 사항: [추가 확인이 필요한 구체적인 정보들]
                3. 의견 vs 사실: [주관적 의견과 객관적 사실 구분]
                """,
                
                "comprehensive": """이 YouTube 영상을 종합적으로 분석해주세요. 한국어로 답변해주세요.
                
                1. 영상 요약: [핵심 내용 3-5문장]
                2. 주요 주장: [영상에서 제시된 주요 사실적 주장들]
                3. 팩트체킹 필요 사항: [검증이 필요한 구체적인 정보들]
                4. 화자의 논조: [객관적/주관적, 중립적/편향적 등]
                5. 핵심 키워드: [주요 키워드 5-10개]
                """
            }
            
            prompt = prompts.get(analysis_type, prompts["comprehensive"])
            
            # Gemini API 호출 - 예시와 정확히 동일한 형식으로
            response = self.client.models.generate_content(
                model='models/gemini-2.0-flash-exp',
                contents=types.Content(
                    parts=[
                        types.Part(
                            file_data=types.FileData(file_uri=youtube_url)
                        ),
                        types.Part(text=prompt)
                    ]
                )
            )
            
            # 결과 처리
            result = {
                "url": youtube_url,
                "video_id": self.extract_video_id(youtube_url),
                "analysis_type": analysis_type,
                "content": response.text,
                "status": "success"
            }
            
            console.print("[green]✓ Video analysis completed successfully[/green]")
            return result
            
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]Error analyzing video: {error_msg}[/red]")
            
            # 에러 유형 파악
            if "API key" in error_msg:
                error_detail = "Gemini API key not configured properly"
            elif "quota" in error_msg.lower():
                error_detail = "API quota exceeded. Free tier: max 8 hours of video per day"
            elif "not found" in error_msg.lower():
                error_detail = "Video not found or is private"
            else:
                error_detail = error_msg
            
            return {
                "url": youtube_url,
                "analysis_type": analysis_type,
                "status": "error",
                "error": error_detail
            }
    
    async def check_content_type(self, youtube_url: str) -> Dict[str, Any]:
        """
        영상의 콘텐츠 유형을 확인하고 팩트체킹 필요성을 판단
        
        Returns:
            콘텐츠 유형 및 팩트체킹 필요성
        """
        result = await self.analyze_video(youtube_url, "content_type")
        
        if result["status"] == "success":
            content = result["content"]
            
            # 팩트체킹 필요성 파싱
            needs_factcheck = "팩트체킹 필요성: 예" in content or "팩트체킹 필요성: [예]" in content
            
            # 콘텐츠 유형 파싱
            content_type = "unknown"
            purpose = "unknown"
            
            for line in content.split('\n'):
                if "콘텐츠 유형:" in line:
                    content_type = line.split("콘텐츠 유형:")[-1].strip().strip('[]')
                elif "주요 목적:" in line:
                    purpose = line.split("주요 목적:")[-1].strip().strip('[]')
            
            result["needs_factcheck"] = needs_factcheck
            result["content_type"] = content_type
            result["purpose"] = purpose
            
            console.print(f"[cyan]콘텐츠 유형: {content_type}, 목적: {purpose}, 팩트체킹 필요: {needs_factcheck}[/cyan]")
        
        return result
    
    async def extract_claims_for_factcheck(self, youtube_url: str) -> Dict[str, Any]:
        """
        영상에서 팩트체킹이 필요한 주장들을 추출
        
        Returns:
            팩트체킹을 위한 구조화된 데이터
        """
        # 먼저 콘텐츠 유형 확인
        type_check = await self.check_content_type(youtube_url)
        
        if type_check["status"] == "success" and not type_check.get("needs_factcheck", True):
            # 팩트체킹이 필요 없는 콘텐츠
            return {
                "url": youtube_url,
                "status": "skip",
                "content_type": type_check.get("content_type", "unknown"),
                "purpose": type_check.get("purpose", "unknown"),
                "message": "이 영상은 팩트체킹이 필요하지 않은 콘텐츠입니다.",
                "content": type_check["content"],
                "needs_factcheck": False
            }
        
        # 팩트체킹이 필요한 경우 주장 추출
        result = await self.analyze_video(youtube_url, "factcheck")
        
        if result["status"] == "success":
            # 분석 결과에서 주장들을 구조화
            content = result["content"]
            
            # 주장 추출을 위한 추가 처리
            claims = []
            lines = content.split('\n')
            
            for line in lines:
                # 숫자나 불릿 포인트로 시작하는 주장들 추출
                if any(line.strip().startswith(marker) for marker in ['1.', '2.', '3.', '-', '•', '*']):
                    claim = line.strip().lstrip('0123456789.-•* ')
                    if claim and len(claim) > 10:  # 의미있는 길이의 주장만
                        claims.append(claim)
            
            result["extracted_claims"] = claims
            result["claims_count"] = len(claims)
            
            # 팩트체킹을 위한 요약문 생성
            if claims:
                result["factcheck_statement"] = " ".join(claims[:3])  # 상위 3개 주장 결합
            else:
                # 전체 내용에서 첫 문장 추출
                result["factcheck_statement"] = content.split('.')[0] if '.' in content else content[:200]
        
        return result


# 사용 예제
if __name__ == "__main__":
    import asyncio
    
    async def test_analyzer():
        # 환경 변수 설정 확인
        if not os.getenv('GOOGLE_API_KEY'):
            print("Please set GOOGLE_API_KEY environment variable")
            return
        
        analyzer = YouTubeVideoAnalyzer()
        
        # 테스트 URL (공개 영상)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # 영상 분석
        print("\n=== Comprehensive Analysis ===")
        result = await analyzer.analyze_video(test_url, "comprehensive")
        print(result["content"] if result["status"] == "success" else result["error"])
        
        # 팩트체킹용 주장 추출
        print("\n=== Fact-check Claims ===")
        claims_result = await analyzer.extract_claims_for_factcheck(test_url)
        if claims_result["status"] == "success":
            print(f"Extracted {claims_result['claims_count']} claims")
            print(f"Statement for fact-checking: {claims_result.get('factcheck_statement', 'N/A')}")
    
    # 실행
    asyncio.run(test_analyzer())