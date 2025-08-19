"""Super Agent - 팩트체크 총괄 코디네이터"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader


class SuperAgent(FactWaveAgent):
    """모든 에이전트의 분석을 종합하여 최종 판정을 내리는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('super')
        
        super().__init__(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory']
        )