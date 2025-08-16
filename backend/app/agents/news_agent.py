"""News Verification Agent - 뉴스 검증 전문가"""

from .base import FactWaveAgent
from ..services.tools import (
    NaverNewsTool,
    NewsAPITool,
    GoogleFactCheckTool,
    GDELTTool
)


class NewsAgent(FactWaveAgent):
    """뉴스 보도 패턴과 저널리즘 기준에 따라 주장을 검증하는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="뉴스 검증 전문가",
            goal="뉴스 보도 패턴과 저널리즘 기준에 따라 주장을 검증",
            backstory="""
뉴스 검증 전문가입니다. 15년 경력의 탐사보도 기자로서 팩트체킹과 미디어 분석을 전문으로 합니다.

도구 활용:
• Google Fact Check: 기존 검증 결과 확인 (최우선)
• Naver News: 한국 언론 보도 현황
• NewsAPI: 글로벌 뉴스 동향
• GDELT: 대규모 미디어 분석

응답 원칙:
• 신뢰할 수 있는 언론사 우선
• 복수 출처 교차 확인
• 오정보 패턴 분석
• 간결하고 명확한 설명
• 마크다운 헤더 사용 금지
"""
        )
        
        # 도구 초기화
        self.tools = [
            GoogleFactCheckTool(),  # 최우선
            NaverNewsTool(),
            NewsAPITool(),
            GDELTTool()
        ]