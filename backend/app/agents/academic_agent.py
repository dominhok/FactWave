"""Academic Agent - 학술 연구 전문가"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader
from ..services.tools import (
    WikipediaSearchTool, 
    OpenAlexTool,  # SemanticScholar 대신 OpenAlex 사용 (rate limit 문제 해결)
    ArxivSearchTool
)
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool


class AcademicAgent(FactWaveAgent):
    """학술적 지식과 과학적 추론을 사용하여 주장을 분석하는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('academic')
        
        super().__init__(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory']
        )
        
        # 도구 초기화
        self.tools = [
            TavilySearchTool(
                topic="general",
                search_depth="basic",
                max_results=10,
                days=365*10  # 학술 자료는 5년까지 검색
            ),
            WikipediaSearchTool(),
            OpenAlexTool(),  # SemanticScholar 대신 사용
            ArxivSearchTool()
        ]