"""News Verification Agent - 뉴스 검증 전문가"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader
from ..services.tools import (
    NaverNewsTool,
    NewsAPITool,
    GoogleFactCheckTool
)
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool


class NewsAgent(FactWaveAgent):
    """뉴스 보도 패턴과 저널리즘 기준에 따라 주장을 검증하는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('news')
        
        super().__init__(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory']
        )
        
        # 도구 초기화
        self.tools = [
            TavilySearchTool(
                topic="news",
                search_depth="basic",
                max_results=10,
                include_answer=True,
                days=365*10  # 뉴스는 최근 10년까지 검색
            ),
            GoogleFactCheckTool(),  # 팩트체크 전용
            NaverNewsTool(),
            NewsAPITool()
        ]