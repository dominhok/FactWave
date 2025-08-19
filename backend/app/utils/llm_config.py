"""LLM configuration with structured outputs support"""

from typing import Type, Optional, Dict, Any
from pydantic import BaseModel
from crewai import LLM
import os
import json


class StructuredLLM:
    """CrewAI LLM with structured output support"""
    
    @staticmethod
    def create_structured_llm(
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> LLM:
        """Create OpenAI GPT-4.1-mini with structured output support
        
        Args:
            response_model: Pydantic model for structured response
            temperature: LLM temperature 
            max_tokens: Maximum tokens
        
        Returns:
            Configured LLM instance
        """
        # Base configuration for OpenAI GPT-4.1-mini
        base_config = {
            "model": "gpt-4.1-mini",
            "temperature": temperature,
            "max_tokens": max_tokens or 1000,
        }
        
        # Pydantic 모델을 직접 response_format에 전달
        if response_model:
            base_config["response_format"] = response_model
        
        return LLM(**base_config)
    
    @staticmethod
    def get_default_llm() -> LLM:
        """Get default LLM without structured output"""
        return LLM(
            model="gpt-4.1-mini",
            temperature=0.1,
            max_tokens=1000
        )


def get_step1_llm() -> LLM:
    """LLM for Step 1 analysis - tool calling enabled"""
    # Structured output 제거하여 tool calling 활성화
    return LLM(
        model="gpt-4.1-mini",
        temperature=0.1,
        max_tokens=2000  # 도구 호출을 위해 토큰 증가
    )


def get_step2_llm() -> LLM:
    """LLM for Step 2 debate with structured output"""
    from ..models.responses import Step2Debate
    return StructuredLLM.create_structured_llm(
        response_model=Step2Debate,
        temperature=0.2
    )


def get_step3_llm() -> LLM:
    """LLM for Step 3 synthesis with structured output"""
    from ..models.responses import Step3Synthesis
    return StructuredLLM.create_structured_llm(
        response_model=Step3Synthesis,
        temperature=0.1
    )


# Fallback for backward compatibility
def get_legacy_llm() -> str:
    """Legacy LLM string for existing agents"""
    return "gpt-4.1-mini"