"""LLM configuration with structured outputs support"""

from typing import Type, Optional, Dict, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
import json


class StructuredLLM:
    """Wrapper for LLM with structured output support"""
    
    @staticmethod
    def create_structured_llm(
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> ChatOpenAI:
        """Create Upstage LLM with structured output support
        
        Args:
            response_model: Pydantic model for structured response
            temperature: LLM temperature 
            max_tokens: Maximum tokens
        """
        # Base configuration for Upstage Solar API
        base_config = {
            "model": "openai/solar-pro2",
            "api_key": os.getenv("UPSTAGE_API_KEY"),
            "base_url": "https://api.upstage.ai/v1/solar",
            "temperature": temperature,
            "max_tokens": max_tokens or 1000,
        }
        
        # Add structured output configuration if model provided
        if response_model:
            schema = response_model.model_json_schema()
            
            # Upstage API structured output format
            base_config["extra_body"] = {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "strict": True,
                        "schema": schema
                    }
                }
            }
        
        return ChatOpenAI(**base_config)
    
    @staticmethod
    def get_default_llm() -> ChatOpenAI:
        """Get default LLM without structured output"""
        return ChatOpenAI(
            model="openai/solar-pro2",
            api_key=os.getenv("UPSTAGE_API_KEY"),
            base_url="https://api.upstage.ai/v1/solar",
            temperature=0.1,
            max_tokens=1000
        )


def get_step1_llm() -> ChatOpenAI:
    """LLM for Step 1 analysis with structured output"""
    from ..models.responses import Step1Analysis
    return StructuredLLM.create_structured_llm(
        response_model=Step1Analysis,
        temperature=0.1
    )


def get_step2_llm() -> ChatOpenAI:
    """LLM for Step 2 debate with structured output"""
    from ..models.responses import Step2Debate
    return StructuredLLM.create_structured_llm(
        response_model=Step2Debate,
        temperature=0.2
    )


def get_step3_llm() -> ChatOpenAI:
    """LLM for Step 3 synthesis with structured output"""
    from ..models.responses import Step3Synthesis
    return StructuredLLM.create_structured_llm(
        response_model=Step3Synthesis,
        temperature=0.1
    )


# Fallback for backward compatibility
def get_legacy_llm() -> str:
    """Legacy LLM string for existing agents"""
    return "openai/solar-pro2"