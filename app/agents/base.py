"""Base agent class with common functionality"""

from crewai import Agent
from typing import Dict, Any, List, Optional
from ..utils.llm_config import StructuredLLM


class FactWaveAgent:
    """Base class for all FactWave agents"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools: List[Any] = []  # 도구 목록
        self.agent = None  # 나중에 생성
    
    def _create_agent(self, step: str = "step1") -> Agent:
        """Create the CrewAI agent instance with step-specific LLM"""
        # Step에 따라 적절한 LLM 선택
        if step == "step1":
            from ..utils.llm_config import get_step1_llm
            llm = get_step1_llm()
        elif step == "step2":
            from ..utils.llm_config import get_step2_llm
            llm = get_step2_llm()
        elif step == "step3":
            from ..utils.llm_config import get_step3_llm
            llm = get_step3_llm()
        else:
            llm = StructuredLLM.get_default_llm()
            
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,  # 도구 전달
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def get_agent(self, step: str = "step1") -> Agent:
        """Return the CrewAI agent instance"""
        # Step이 바뀌면 새로운 agent 생성 (LLM이 달라지므로)
        self.agent = self._create_agent(step)
        return self.agent