"""Logic Verification Agent - 논리 및 추론 전문가"""

from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader


class LogicAgent(FactWaveAgent):
    """주장의 논리적 일관성과 구조를 분석하는 에이전트"""
    
    def __init__(self):
        # YAML에서 설정 로드
        prompt_loader = PromptLoader()
        agent_config = prompt_loader.get_agent_config('logic')
        
        super().__init__(
            role=agent_config['role'],
            goal=agent_config['goal'],
            backstory=agent_config['backstory']
        )
        
        # 논리 전문가는 도구를 사용하지 않음
        self.tools = []