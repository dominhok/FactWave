"""Statistics Agent - 통계 및 데이터 전문가"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader
from ..services.tools import (
    KOSISSearchTool,
    WorldBankSearchTool,
    FREDSearchTool,
    OWIDRAGTool
)
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool


class StatisticsAgent(FactWaveAgent):
    """경제 및 사회 통계 데이터를 분석하는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('statistics')
        
        super().__init__(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory']
        )
        
        # 도구 초기화 - 모두 자연어 검색 가능
        self.tools = [
            TavilySearchTool(
                topic="general",
                search_depth="basic",
                max_results=5,
                days=365  # 통계 데이터는 1년까지
            ),
            KOSISSearchTool(),      # 한국 통계청 자연어 검색
            WorldBankSearchTool(),  # World Bank 자연어 검색
            FREDSearchTool(),       # FRED 자연어 검색
            OWIDRAGTool()           # Our World in Data RAG 검색
        ]