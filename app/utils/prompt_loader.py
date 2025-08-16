"""프롬프트 YAML 로더"""

import yaml
from pathlib import Path
from typing import Dict, Any

class PromptLoader:
    """YAML 파일에서 프롬프트를 로드하고 관리"""
    
    def __init__(self, config_path: str = None):
        """
        Args:
            config_path: YAML 설정 파일 경로
        """
        if config_path is None:
            # 기본 경로 설정
            config_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
        
        self.config_path = Path(config_path)
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """YAML 파일에서 프롬프트 로드"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"프롬프트 설정 파일을 찾을 수 없습니다: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_verdict_options(self) -> Dict[str, str]:
        """판정 옵션 반환"""
        return self.prompts.get('verdict_options', {})
    
    def get_agent_weights(self) -> Dict[str, float]:
        """에이전트 가중치 반환"""
        return self.prompts.get('agent_weights', {})
    
    def get_step1_prompt(self, agent_type: str, statement: str, role: str = None, agent_name: str = None) -> str:
        """Step 1 프롬프트 생성
        
        Args:
            agent_type: 에이전트 타입 (logic, general 등)
            statement: 검증할 주장
            role: 에이전트 역할
            agent_name: 에이전트 이름
        """
        if agent_type == 'logic':
            template = self.prompts['step1']['logic']['template']
            return template.format(statement=statement)
        else:
            template = self.prompts['step1']['general']['template']
            return template.format(statement=statement, role=role, agent_name=agent_name or agent_type)
    
    def get_step2_prompt(self, statement: str, role: str, agent_name: str = None) -> str:
        """Step 2 토론 프롬프트 생성"""
        template = self.prompts['step2']['template']
        return template.format(statement=statement, role=role, agent_name=agent_name or "agent")
    
    def get_step3_prompt(self, statement: str, weights: Dict[str, float] = None) -> str:
        """Step 3 최종 종합 프롬프트 생성"""
        template = self.prompts['step3']['template']
        
        # 가중치 정보 추가
        if weights:
            weight_info = "\n".join([f"- {k}: {v}" for k, v in weights.items()])
            template = template.replace("{weights}", weight_info)
        
        return template.format(statement=statement)
    
    def get_output_format(self) -> Dict[str, Any]:
        """출력 형식 가이드라인 반환"""
        return self.prompts.get('output_format', {})
    
    def get_response_style(self) -> Dict[str, Any]:
        """응답 스타일 설정 반환"""
        return self.prompts.get('response_style', {})
    
    def format_verdict_options_string(self) -> str:
        """판정 옵션을 문자열로 포맷"""
        options = self.get_verdict_options()
        return "\n".join([f"- {k}: {v}" for k, v in options.items()])
    
    def reload(self):
        """프롬프트 설정 다시 로드 (핫 리로드용)"""
        self.prompts = self._load_prompts()
        
    def update_prompt(self, path: str, value: Any):
        """특정 프롬프트 업데이트 (동적 수정용)
        
        Args:
            path: 점 표기법 경로 (예: "step1.logic.template")
            value: 새로운 값
        """
        keys = path.split('.')
        target = self.prompts
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
        
        # 파일에 저장
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.prompts, f, allow_unicode=True, default_flow_style=False)