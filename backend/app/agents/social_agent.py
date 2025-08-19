"""Social Intelligence Agent - 사회 맥락 분석가"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader
from ..services.tools import TwitterTool, YouTubeTool
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool


class SocialAgent(FactWaveAgent):
    """사회적, 문화적 맥락에서 주장을 평가하는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('social')
        
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
                days=90  # 소셜 미디어는 최근 3개월
            ),
            # YouTubeTool(),  # YouTube 영상 및 댓글 분석 (API 키 필요)
            TwitterTool()  # 소셜 미디어 분석
        ]