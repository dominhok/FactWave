"""Structured response models for FactWave agents"""

from typing import List, Literal
from pydantic import BaseModel, Field


class Step1Analysis(BaseModel):
    """Step 1: 초기 분석 응답 구조"""
    
    class Config:
        extra = "forbid"  # additionalProperties = false
    
    agent_name: str = Field(description="에이전트 이름")
    verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족", 
        "논란중", "부분적_거짓", "대체로_거짓", "거짓", "과장됨", 
        "오해소지", "시대착오"
    ] = Field(description="판정 결과")
    
    key_findings: List[str] = Field(description="핵심 발견사항")
    evidence_sources: List[str] = Field(description="근거 출처")
    reasoning: str = Field(description="판정 근거")


class Step2Debate(BaseModel):
    """Step 2: 토론 응답 구조"""
    
    class Config:
        extra = "forbid"  # additionalProperties = false
    
    agent_name: str = Field(description="에이전트 이름")
    agreements: List[str] = Field(description="다른 전문가와 동의하는 점")
    disagreements: List[str] = Field(description="이견이나 보완점")
    additional_perspective: str = Field(description="내 전문성으로 추가하는 관점")
    final_verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족",
        "논란중", "부분적_거짓", "대체로_거짓", "거짓", "과장됨",
        "오해소지", "시대착오"
    ] = Field(description="토론 후 최종 판정")


class Step3Synthesis(BaseModel):
    """Step 3: 최종 종합 응답 구조"""
    
    class Config:
        extra = "forbid"  # additionalProperties = false
    
    final_verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족",
        "논란중", "부분적_거짓", "대체로_거짓", "거짓", "과장됨", 
        "오해소지", "시대착오"
    ] = Field(description="최종 판정")
    
    key_agreements: List[str] = Field(description="주요 합의점")
    key_disagreements: List[str] = Field(description="주요 불일치점") 
    verdict_reasoning: str = Field(description="최종 판정 근거")
    summary: str = Field(description="종합 요약")


# Export models for use in agents
__all__ = [
    "Step1Analysis",
    "Step2Debate", 
    "Step3Synthesis"
]