# FactWave Backend Migration Guide

## 📋 Overview
이 문서는 FactWave 백엔드를 Upstage Solar-pro2에서 OpenAI GPT-4o-mini로 마이그레이션하고, CrewAI의 Structured Output을 적용하며, 모든 프롬프트를 YAML에서 중앙 관리하도록 변경한 과정을 상세히 기록합니다.

## 🎯 Migration Goals
1. **LLM Provider 변경**: Upstage Solar-pro2 → OpenAI GPT-4o-mini
2. **Structured Output 적용**: JSON 파싱 오류 감소를 위한 Pydantic 모델 기반 구조화
3. **프롬프트 중앙화**: 모든 에이전트 설정을 YAML 파일에서 관리
4. **Confidence 필드 제거**: LLM 일관성 문제 해결

## 📁 변경된 파일 구조

```
backend/
├── app/
│   ├── agents/           # 에이전트 정의 (YAML에서 설정 로드)
│   ├── config/
│   │   └── prompts.yaml  # 모든 프롬프트와 에이전트 설정 중앙화
│   ├── core/
│   │   ├── crew.py       # Structured Output 적용
│   │   └── streaming_crew.py  # Confidence 제거
│   ├── models/
│   │   └── responses.py  # Pydantic 응답 모델
│   └── utils/
│       ├── llm_config.py # CrewAI LLM 설정
│       └── prompt_loader.py  # YAML 프롬프트 로더
```

## 🔄 Migration Steps

### Step 1: LLM Provider 변경

#### 1.1 의존성 업데이트
```python
# 이전 (잘못된 접근)
from langchain_openai import ChatOpenAI

# 이후 (올바른 CrewAI 방식)
from crewai import LLM
```

#### 1.2 LLM 설정 파일 생성 (`app/utils/llm_config.py`)
```python
from crewai import LLM
from typing import Type, Optional
from pydantic import BaseModel

class StructuredLLM:
    """CrewAI LLM with structured output support"""
    
    @staticmethod
    def create_structured_llm(
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0,
        max_tokens: Optional[int] = None
    ) -> LLM:
        base_config = {
            "model": "gpt-4o-mini",  # OpenAI 모델
            "temperature": temperature,
            "max_tokens": max_tokens or 3000,
        }
        
        # Pydantic 모델을 직접 response_format에 전달
        if response_model:
            base_config["response_format"] = response_model
        
        return LLM(**base_config)
```

#### 1.3 환경 변수 설정
`.env` 파일에 OpenAI API 키 추가:
```
OPENAI_API_KEY=sk-proj-xxxxx
```

### Step 2: Structured Output 구현

#### 2.1 Pydantic 응답 모델 정의 (`app/models/responses.py`)
```python
from typing import List, Literal
from pydantic import BaseModel, Field

class Step1Analysis(BaseModel):
    """Step 1: 초기 분석 응답 구조"""
    agent_name: str = Field(description="에이전트 이름")
    verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족", 
        "논란중", "부분적_거짓", "대체로_거짓", "거짓", "과장됨", 
        "오해소지", "시대착오"
    ] = Field(description="판정 결과")
    key_findings: List[str] = Field(description="핵심 발견사항")
    evidence_sources: List[str] = Field(description="근거 출처")
    reasoning: str = Field(description="판정 근거")

class Step2Debate(BaseModel):
    """Step 2: 토론 응답 구조"""
    agent_name: str = Field(description="에이전트 이름")
    agreements: List[str] = Field(description="동의하는 점")
    disagreements: List[str] = Field(description="이견이나 보완점")
    additional_perspective: str = Field(description="추가 관점")
    final_verdict: Literal[...] = Field(description="최종 판정")

class Step3Synthesis(BaseModel):
    """Step 3: 최종 종합 응답 구조"""
    final_verdict: Literal[...] = Field(description="최종 판정")
    key_agreements: List[str] = Field(description="주요 합의점")
    key_disagreements: List[str] = Field(description="주요 불일치점")
    verdict_reasoning: str = Field(description="최종 판정 근거")
    summary: str = Field(description="종합 요약")
```

#### 2.2 Task에 Structured Output 적용 (`app/core/crew.py`)
```python
from ..models.responses import Step1Analysis, Step2Debate, Step3Synthesis

def create_step1_tasks(self, statement: str) -> List[Task]:
    tasks = []
    for agent_name, agent_instance in self.agents.items():
        if agent_name != "super":
            task = Task(
                description=description,
                agent=agent_instance.get_agent("step1"),
                expected_output="판정, 근거, 신뢰도를 포함한 구조화된 분석",
                callback=task_callback_func,
                output_json=Step1Analysis  # ✅ Structured Output 적용
            )
            tasks.append(task)
    return tasks
```

### Step 3: 프롬프트 중앙화

#### 3.1 YAML 설정 파일 생성 (`app/config/prompts.yaml`)
```yaml
# 에이전트 기본 설정
agents:
  academic:
    role: "학술 연구 전문가"
    goal: "학술 논문과 연구 결과를 기반으로 주장을 검증"
    backstory: |
      학술 연구 검증 전문가입니다. 20년 경력의 박사로서...
      
      도구 활용:
      • Wikipedia: 기본 개념 확인
      • OpenAlex: 학술논문 검색 (주력)
      • ArXiv: 최신 연구 동향
      
      응답 원칙:
      • 메타분석과 리뷰 논문 우선
      • 최소 3-5개 논문 검토
      • 학계 컨센서스 중심
  
  news:
    role: "뉴스 검증 전문가"
    goal: "언론 보도와 미디어 자료를 기반으로 주장을 검증"
    backstory: |
      뉴스 검증 전문가입니다...

# Step별 프롬프트 템플릿
step1:
  general:
    template: |
      주장: {statement}
      
      {role}로서 이 주장을 전문적으로 분석하세요.
      
      다음 JSON 형식으로 응답하세요:
      {{
        "agent_name": "{agent_name}",
        "verdict": "[선택지 중 하나]",
        "key_findings": ["핵심 발견사항들"],
        "evidence_sources": ["출처들"],
        "reasoning": "판정 근거"
      }}

step2:
  template: |
    주장: {statement}
    
    다른 전문가들의 분석을 검토하고 토론하세요...

step3:
  template: |
    모든 분석을 종합하여 최종 판정을 내리세요...
```

#### 3.2 PromptLoader 클래스 구현 (`app/utils/prompt_loader.py`)
```python
import yaml
from pathlib import Path
from typing import Dict, Any

class PromptLoader:
    """YAML 파일에서 프롬프트를 로드하고 관리"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "prompts.yaml"
        self.config_path = Path(config_path)
        self.prompts = self._load_prompts()
    
    def get_agent_config(self, agent_name: str) -> Dict[str, str]:
        """특정 에이전트의 설정 반환"""
        agents = self.prompts.get('agents', {})
        if agent_name not in agents:
            raise KeyError(f"Agent '{agent_name}' not found")
        return agents[agent_name]
    
    def get_step1_prompt(self, agent_type: str, statement: str, 
                        role: str = None, agent_name: str = None) -> str:
        """Step 1 프롬프트 생성"""
        template = self.prompts['step1'][agent_type]['template']
        return template.format(
            statement=statement, 
            role=role, 
            agent_name=agent_name
        )
```

#### 3.3 에이전트 파일 수정 (예: `app/agents/academic_agent.py`)
```python
from .base import FactWaveAgent
from ..utils.prompt_loader import PromptLoader
from ..services.tools import WikipediaSearchTool, OpenAlexTool, ArxivSearchTool

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
            WikipediaSearchTool(),
            OpenAlexTool(),
            ArxivSearchTool()
        ]
```

### Step 4: Confidence 필드 제거

#### 4.1 Streaming Crew 수정 (`app/core/streaming_crew.py`)
```python
# 이전 (confidence 포함)
await self.ws_manager.emit({
    "type": "task_completed",
    "content": {
        "analysis": analysis,
        "verdict": verdict,
        "confidence": confidence,  # ❌ 제거
    }
})

# 이후 (confidence 제거)
await self.ws_manager.emit({
    "type": "task_completed",
    "content": {
        "analysis": analysis,
        "verdict": verdict,  # ✅ verdict만 전송
    }
})
```

#### 4.2 관련 메서드 제거
- `_extract_confidence()` 메서드 제거
- `_calculate_confidence_from_verdict()` 메서드 제거
- `_calculate_weighted_confidence()` 메서드 제거

## 🧪 테스트 및 검증

### 테스트 스크립트 (`test_structured_output.py`)
```python
from app.core.crew import FactWaveCrew
from app.models.responses import Step1Analysis

def test_structured_output():
    test_statement = "한국의 최저임금은 2024년 기준 시간당 9,860원이다"
    crew = FactWaveCrew()
    tasks = crew.create_step1_tasks(test_statement)
    
    for task in tasks:
        # output_json이 설정되었는지 확인
        assert hasattr(task, 'output_json')
        assert task.output_json == Step1Analysis
        print(f"✅ Task configured with structured output")

if __name__ == "__main__":
    test_structured_output()
```

## 🚀 실행 방법

### 1. 백엔드 서버 실행
```bash
cd backend
uv run python -m app.api.server
```

### 2. WebSocket 테스트
```bash
cd backend
uv run python test_websocket_client.py "검증할 문장"
```

### 3. 프론트엔드 실행
```bash
cd frontend_wonjun
npm run dev
```

## 📊 개선 효과

### Before
- **LLM**: Upstage Solar-pro2 (한국어 특화)
- **응답 형식**: 비구조화된 텍스트
- **프롬프트 관리**: 각 에이전트 파일에 하드코딩
- **JSON 파싱**: 정규식과 문자열 파싱 의존
- **Confidence**: LLM이 생성하는 불안정한 값

### After
- **LLM**: OpenAI GPT-4o-mini (범용, 비용 효율적)
- **응답 형식**: Pydantic 모델 기반 구조화
- **프롬프트 관리**: YAML 파일에서 중앙 관리
- **JSON 파싱**: CrewAI가 자동으로 처리
- **Confidence**: 제거 (verdict만으로 충분)

## 🔍 핵심 인사이트

### 1. CrewAI의 올바른 사용법
- `langchain_openai.ChatOpenAI` ❌
- `crewai.LLM` ✅
- Pydantic 모델을 직접 `response_format`에 전달

### 2. Structured Output의 장점
- JSON 파싱 오류 대폭 감소
- 프론트엔드에서 안정적인 데이터 처리
- 타입 안정성과 자동 검증

### 3. 프롬프트 중앙화의 이점
- 에이전트 설정 변경 시 코드 수정 불필요
- 프롬프트 A/B 테스트 용이
- 다국어 지원 확장 가능

## 📝 추가 고려사항

### 향후 개선 가능 영역
1. **Multi-model 지원**: 다양한 LLM Provider 지원
2. **프롬프트 버전 관리**: Git으로 프롬프트 변경 이력 추적
3. **동적 프롬프트 로딩**: 서버 재시작 없이 프롬프트 업데이트
4. **응답 캐싱**: 동일한 질문에 대한 캐시 구현

### 모니터링 포인트
- API 비용 추적 (OpenAI Dashboard)
- 응답 시간 측정
- Structured Output 성공률
- 에러 로그 분석

## 📚 참고 자료
- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [CrewAI Structured Output Guide](https://docs.crewai.com/concepts/structured-outputs)

---

*Last Updated: 2025-08-18*
*Author: Claude Code Assistant*