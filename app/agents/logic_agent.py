"""Logic Verification Agent - 논리 및 추론 전문가"""

from .base import FactWaveAgent


class LogicAgent(FactWaveAgent):
    """주장의 논리적 일관성과 구조를 분석하는 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="논리 및 추론 전문가",
            goal="주장의 논리적 일관성과 구조를 분석",
            backstory="""당신은 형식 논리, 논증 이론, 비판적 사고에 훈련된 논리 전문가입니다.
논리적 오류를 식별하고, 인과 관계를 검토하며,
주장의 내적 일관성을 평가합니다."""
        )