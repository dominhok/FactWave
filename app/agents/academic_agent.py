"""Academic Agent - 학술 연구 전문가"""

from .base import FactWaveAgent
from ..services.tools import (
    WikipediaSearchTool, 
    OpenAlexTool,  # SemanticScholar 대신 OpenAlex 사용 (rate limit 문제 해결)
    ArxivSearchTool
)


class AcademicAgent(FactWaveAgent):
    """학술적 지식과 과학적 추론을 사용하여 주장을 분석하는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="학술 연구 전문가",
            goal="학술 논문과 연구 결과를 기반으로 주장을 검증",
            backstory="""당신은 학술 논문과 연구 결과를 분석하는 전문가입니다.
학술 데이터베이스에서 관련 논문을 찾고, 연구 결과를 해석하며,
학계의 합의와 논쟁을 파악합니다.

당신은 다음 도구들을 사용할 수 있습니다:
- Wikipedia Search: 일반적인 배경 지식과 정의 검색
- OpenAlex Academic Search: 240M+ 학술 논문 검색 (rate limit 없음)
- ArXiv Search: CS, 물리, 수학 분야 최신 연구 논문 검색

팩트체크 시 다음 순서로 모든 도구를 활용하세요:
1. 먼저 Wikipedia로 기본 개념과 배경 지식을 확인하세요
2. OpenAlex로 관련 학술 논문을 검색하세요 (최소 3개 이상)
3. ArXiv로 최신 연구 동향을 확인하세요

중요: 각 도구의 결과를 종합하여 다각적인 분석을 제공하세요."""
        )
        
        # 도구 초기화
        self.tools = [
            WikipediaSearchTool(),
            OpenAlexTool(),  # SemanticScholar 대신 사용
            ArxivSearchTool()
        ]