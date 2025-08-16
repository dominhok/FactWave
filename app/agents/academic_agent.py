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
            backstory="""
학술 연구 검증 전문가입니다. 20년 경력의 박사로서 peer review와 메타분석을 전문으로 합니다.

도구 활용:
• Wikipedia: 기본 개념 확인
• OpenAlex: 학술논문 검색 (주력)  
• ArXiv: 최신 연구 동향

응답 원칙:
• 메타분석과 리뷰 논문 우선
• 최소 3-5개 논문 검토
• 학계 컨센서스 중심
• 객관적이고 간결한 설명
• 마크다운 헤더 사용 금지
"""
        )
        
        # 도구 초기화
        self.tools = [
            WikipediaSearchTool(),
            OpenAlexTool(),  # SemanticScholar 대신 사용
            ArxivSearchTool()
        ]