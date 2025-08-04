"""Base agent class with common functionality"""

from crewai import Agent
from typing import Dict, Any, List, Optional


class FactWaveAgent:
    """Base class for all FactWave agents"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools: List[Any] = []  # 도구 목록
        self.agent = None  # 나중에 생성
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent instance"""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,  # 도구 전달
            verbose=True,
            allow_delegation=False,
            llm="openai/solar-pro2"
        )
    
    def get_agent(self) -> Agent:
        """Return the CrewAI agent instance"""
        # Lazy initialization - 도구가 설정된 후에 에이전트 생성
        if self.agent is None:
            self.agent = self._create_agent()
        return self.agent