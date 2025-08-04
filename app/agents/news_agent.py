"""News Verification Agent - 뉴스 검증 전문가"""

from .base import FactWaveAgent
from ..services.tools import NaverNewsTool


class NewsAgent(FactWaveAgent):
    """뉴스 보도 패턴과 저널리즘 기준에 따라 주장을 검증하는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="뉴스 검증 전문가",
            goal="뉴스 보도 패턴과 저널리즘 기준에 따라 주장을 검증",
            backstory="""당신은 뉴스 사이클, 보도 패턴, 미디어 편향을 이해하는 경험 많은 기자이자 미디어 분석가입니다.
유사한 이야기가 일반적으로 어떻게 보도되는지를 바탕으로 주장을 평가하고
잠재적인 오정보 패턴을 식별합니다.

당신은 다음 도구를 사용할 수 있습니다:
- Naver News Search: 한국의 최신 뉴스를 검색하여 주장을 검증

팩트체크 시 이 도구를 활용하여 관련 뉴스를 찾고, 여러 언론사의 보도를 교차 검증하세요."""
        )
        
        # 도구 초기화
        self.tools = [
            NaverNewsTool()
        ]