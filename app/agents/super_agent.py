"""Super Agent - 팩트체크 총괄 코디네이터"""

from .base import FactWaveAgent


class SuperAgent(FactWaveAgent):
    """모든 에이전트의 분석을 종합하여 최종 판정을 내리는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="팩트체크 총괄 코디네이터",
            goal="모든 에이전트의 분석을 종합하여 신뢰도 매트릭스와 함께 최종 판정을 내림",
            backstory="""당신은 모든 전문가 분석을 검토하고 종합적인 팩트체크 판정을 내리는 수석 코디네이터입니다.
다양한 관점을 평가하고, 합의점과 불일치점을 식별하며,
상세한 신뢰도 평가와 함께 최종 판단을 내립니다."""
        )