"""Academic Agent - 학술 연구 전문가"""

from .base import FactWaveAgent
from ..services.tools import (
    WikipediaSearchTool, 
    SemanticScholarTool, 
    ArxivSearchTool,
    KOSISTool,
    WorldBankTool
)


class AcademicAgent(FactWaveAgent):
    """학술적 지식과 과학적 추론을 사용하여 주장을 분석하는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="학술 연구 전문가",
            goal="학술적 지식과 과학적 추론을 사용하여 주장을 분석",
            backstory="""당신은 여러 학문 분야에 전문성을 가진 저명한 학술 연구자입니다.
과학적 원리, 논리적 추론, 학술적 지식을 바탕으로 주장을 평가합니다.
관련 이론, 연구, 학계의 합의를 인용하여 분석합니다.

당신은 다음 도구들을 사용할 수 있습니다:
- Wikipedia Search: 일반적인 배경 지식과 정의 검색
- Semantic Scholar Search: 214M+ 학술 논문 검색 및 AI 요약
- ArXiv Search: CS, 물리, 수학 분야 최신 연구 논문 검색
- KOSIS Statistics: 한국 통계청 공식 통계 데이터 (GDP, 인구, 실업률 등)
- World Bank Data: 전 세계 국가의 개발 지표 및 경제 데이터

팩트체크 시 이 도구들을 적극 활용하여 주장을 검증하세요.
특히 경제, 사회 지표와 관련된 주장은 KOSIS나 World Bank 데이터로 검증하세요."""
        )
        
        # 도구 초기화
        self.tools = [
            WikipediaSearchTool(),
            SemanticScholarTool(),
            ArxivSearchTool(),
            KOSISTool(),
            WorldBankTool()
        ]