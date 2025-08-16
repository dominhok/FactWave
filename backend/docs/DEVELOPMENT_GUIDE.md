# FactWave 개발 가이드

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [프론트엔드 개발 가이드](#프론트엔드-개발-가이드)
4. [백엔드 개발 가이드](#백엔드-개발-가이드)
5. [LLM 응답 처리](#llm-응답-처리)
6. [도구 통합 가이드](#도구-통합-가이드)
7. [프롬프트 관리](#프롬프트-관리)
8. [환경 설정](#환경-설정)
9. [디버깅 가이드](#디버깅-가이드)
10. [배포 가이드](#배포-가이드)

---

## 프로젝트 개요

FactWave는 AI 기반 다중 에이전트 팩트체킹 시스템입니다.

### 핵심 특징

- **3단계 팩트체킹 프로세스**: 독립 분석 → 토론 → 최종 종합
- **5개 전문 에이전트**: Academic, News, Social, Logic, Statistics
- **실시간 WebSocket 스트리밍**: 진행 상황 실시간 업데이트
- **구조화된 JSON 응답**: Upstage API structured output 활용
- **중앙화된 프롬프트 관리**: YAML 기반 프롬프트 엔지니어링

### 기술 스택

- **Backend**: Python 3.12+, FastAPI, CrewAI, LangChain
- **Frontend**: React 19.1.0, Vite, Chrome Extension
- **LLM**: Upstage Solar-pro2 (구조화된 출력)
- **Vector DB**: ChromaDB (OWID RAG)
- **WebSocket**: FastAPI WebSocket

---

## 아키텍처

### 시스템 아키텍처

```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   React Frontend│◄─────────────────┤  FastAPI Server │
│   (Port 5173)   │                  │   (Port 8000)   │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ StreamingCrew   │
                                    │ (Event Manager) │
                                    └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   FactWaveCrew  │
                                    │ (Core Workflow) │
                                    └─────────────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
              ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
              │    5 Agents     │   │   10+ Tools     │   │  Prompt Loader  │
              │ Academic, News, │   │ Wikipedia, Naver│   │   YAML Config   │
              │ Social, Logic,  │   │ KOSIS, OWID,    │   │                 │
              │   Statistics    │   │ Twitter, etc.   │   │                 │
              └─────────────────┘   └─────────────────┘   └─────────────────┘
                        │                     │                     │
                        └─────────────────────┼─────────────────────┘
                                              ▼
                                    ┌─────────────────┐
                                    │  Upstage LLM    │
                                    │   Solar-pro2    │
                                    │ (JSON Response) │
                                    └─────────────────┘
```

### 데이터 플로우

```
1. 사용자 입력 (팩트체킹 요청)
   ▼
2. WebSocket 연결 (session_id)
   ▼
3. StreamingFactWaveCrew 초기화
   ▼
4. Step 1: 5개 에이전트 병렬 실행
   ├── Academic Agent → Wikipedia, OpenAlex, ArXiv
   ├── News Agent → Google Fact Check, Naver News, NewsAPI
   ├── Social Agent → Twitter/X Search
   ├── Logic Agent → 논리적 분석 (도구 없음)
   └── Statistics Agent → KOSIS, World Bank, FRED, OWID
   ▼
5. Step 2: 순차적 토론 (이전 결과 참조)
   ▼
6. Step 3: Super Agent 최종 종합
   ▼
7. 구조화된 최종 결과 반환
```

---

## 프론트엔드 개발 가이드

### 프로젝트 구조

```
src/
├── App.jsx           # 메인 컴포넌트
├── App.css          # 스타일시트
├── main.jsx         # 엔트리 포인트
└── assets/          # 정적 리소스
```

### WebSocket 연결 설정

```javascript
// WebSocket 연결 상태
const [ws, setWs] = useState(null);
const [messages, setMessages] = useState([]);
const [isLoading, setIsLoading] = useState(false);

// WebSocket 연결
useEffect(() => {
  const sessionId = `session_${Date.now()}`;
  const websocket = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
  
  websocket.onopen = () => {
    console.log('WebSocket 연결됨');
    setWs(websocket);
  };
  
  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleWebSocketMessage(data);
  };
  
  websocket.onclose = () => {
    console.log('WebSocket 연결 종료');
    setWs(null);
  };
  
  return () => {
    websocket.close();
  };
}, []);
```

### 메시지 처리 로직

```javascript
const handleWebSocketMessage = (data) => {
  console.log('수신된 메시지:', data);
  
  const content = data.content || {};
  const agent = data.agent;
  const step = data.step;

  switch (data.type) {
    case 'task_completed':
      // JSON 응답 파싱
      const parsedResponse = parseAgentResponse(content.analysis || '{}');
      
      if (parsedResponse) {
        const message = {
          id: `${agent}_task_complete_${Date.now()}`,
          type: 'response',
          agentId: agent,
          agentName: agentConfig[agent]?.name || agent,
          avatar: agentConfig[agent]?.avatar || '🤖',
          step: step,
          status: 'completed',
          timestamp: new Date(),
          
          // JSON 구조화된 데이터
          verdict: parsedResponse.verdict || parsedResponse.final_verdict,
          keyFindings: parsedResponse.key_findings || [],
          evidenceSources: parsedResponse.evidence_sources || [],
          reasoning: parsedResponse.reasoning || '',
          
          // Step 2 데이터
          agreements: parsedResponse.agreements || [],
          disagreements: parsedResponse.disagreements || [],
          additionalPerspective: parsedResponse.additional_perspective || ''
        };
        setMessages(prev => [...prev, message]);
      }
      break;
      
    case 'final_result':
      // 최종 결과 처리
      const finalResponse = parseAgentResponse(content.summary || '{}');
      
      const finalMessage = {
        id: `final_${Date.now()}`,
        type: 'final_report',
        agentName: '최종 보고서',
        avatar: '📋',
        timestamp: new Date(),
        
        // 구조화된 최종 결과
        verdict: finalResponse?.final_verdict || content.final_verdict,
        summary: finalResponse?.summary || content.summary,
        reasoning: finalResponse?.verdict_reasoning || '',
        agentVerdicts: content.agent_verdicts || {},
        evidenceSummary: content.evidence_summary || [],
        statement: content.statement || '',
        confidence: content.confidence || 0.5
      };
      setMessages(prev => [...prev, finalMessage]);
      setIsLoading(false);
      break;
  }
};
```

### JSON 응답 파싱

```javascript
const parseAgentResponse = (responseText) => {
  try {
    // 먼저 전체 텍스트가 JSON인지 확인
    if (responseText.trim().startsWith('{') && responseText.trim().endsWith('}')) {
      return JSON.parse(responseText);
    }
    
    // JSON 블록 추출 (```json...``` 또는 {...})
    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    
    return null;
  } catch (error) {
    console.error('JSON 파싱 오류:', error);
    return null;
  }
};
```

### 에이전트 설정

```javascript
const agentConfig = {
  academic: {
    name: '학술 연구 전문가',
    avatar: '🎓',
    color: '#3b82f6'
  },
  news: {
    name: '뉴스 검증 전문가', 
    avatar: '📰',
    color: '#ef4444'
  },
  social: {
    name: '사회 맥락 분석가',
    avatar: '👥', 
    color: '#10b981'
  },
  logic: {
    name: '논리 및 추론 전문가',
    avatar: '🧠',
    color: '#8b5cf6'
  },
  statistics: {
    name: '통계 및 데이터 전문가',
    avatar: '📊',
    color: '#f59e0b'
  }
};
```

### 메시지 렌더링

```javascript
const renderMessage = (message) => {
  if (message.type === 'response') {
    return (
      <div key={message.id} className="response-card">
        <div className="response-header">
          <span className="avatar">{message.avatar}</span>
          <span className="agent-name">{message.agentName}</span>
          {message.verdict && (
            <span className={`verdict verdict-${message.verdict}`}>
              {message.verdict}
            </span>
          )}
          <span className="step-info">{message.step}</span>
        </div>
        
        <div className="response-content">
          {/* 핵심 발견사항 */}
          {message.keyFindings && message.keyFindings.length > 0 && (
            <div className="findings">
              <strong>핵심 발견:</strong>
              <ul>
                {message.keyFindings.map((finding, index) => (
                  <li key={index}>{finding}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* 근거 출처 */}
          {message.evidenceSources && message.evidenceSources.length > 0 && (
            <div className="sources">
              <strong>근거 출처:</strong>
              <ul>
                {message.evidenceSources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* 판정 근거 */}
          {message.reasoning && (
            <div className="reasoning">
              <strong>판정 근거:</strong>
              <p>{message.reasoning}</p>
            </div>
          )}
        </div>
      </div>
    );
  }
  
  if (message.type === 'final_report') {
    return (
      <div key={message.id} className="final-report">
        {/* 최종 보고서 렌더링 */}
      </div>
    );
  }
};
```

### CSS 스타일링

```css
/* 판정 결과 색상 코딩 */
.verdict-참 { background: #dcfce7; color: #16a34a; }
.verdict-대체로_참 { background: #ecfdf5; color: #059669; }
.verdict-부분적_참 { background: #fef3c7; color: #d97706; }
.verdict-불확실 { background: #f3f4f6; color: #6b7280; }
.verdict-정보부족 { background: #f3f4f6; color: #6b7280; }
.verdict-거짓 { background: #fee2e2; color: #dc2626; }

/* 신뢰도 표시 */
.confidence {
  background: #f0f9ff;
  color: #0369a1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

/* 에이전트별 판정 */
.agent-verdicts {
  margin: 8px 0;
  padding: 10px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid #64748b;
}
```

---

## 백엔드 개발 가이드

### 프로젝트 구조

```
app/
├── api/
│   └── server.py                    # FastAPI 서버
├── core/
│   ├── crew.py                     # 메인 팩트체킹 로직
│   └── streaming_crew.py           # WebSocket 스트리밍
├── agents/
│   ├── base.py                     # 기본 에이전트 클래스
│   ├── academic_agent.py           # 학술 연구 전문가
│   ├── news_agent.py              # 뉴스 검증 전문가
│   ├── social_agent.py            # 사회 맥락 분석가
│   ├── logic_agent.py             # 논리 및 추론 전문가
│   ├── statistics_agent.py        # 통계 및 데이터 전문가
│   └── super_agent.py             # 최종 종합 에이전트
├── services/
│   └── tools/                      # 연구 도구들
├── models/
│   └── responses.py               # Pydantic 응답 모델
├── utils/
│   ├── llm_config.py              # LLM 설정
│   ├── prompt_loader.py           # 프롬프트 로더
│   └── websocket_manager.py       # WebSocket 관리
└── config/
    └── prompts.yaml               # 중앙화된 프롬프트
```

### 새 에이전트 추가

1. **에이전트 클래스 생성**

```python
# app/agents/new_agent.py
from .base import FactWaveAgent
from ..services.tools import YourTool

class NewAgent(FactWaveAgent):
    def __init__(self):
        super().__init__(
            role="새 전문가",
            goal="전문 분야에서 주장을 검증",
            backstory="""
            전문가 설명...
            """
        )
        
        self.tools = [
            YourTool()
        ]
```

2. **프롬프트 추가**

```yaml
# app/config/prompts.yaml
step1:
  new_agent:
    template: |
      주장: {statement}
      
      새 전문가로서 이 주장을 분석하세요.
      
      다음 JSON 형식으로 응답하세요:
      {
        "agent_name": "new_agent",
        "verdict": "[판정]",
        "key_findings": ["발견사항"],
        "evidence_sources": ["출처"],
        "reasoning": "판정 근거"
      }
```

3. **에이전트 등록**

```python
# app/core/crew.py
from ..agents import NewAgent

class FactWaveCrew:
    def __init__(self):
        self.agents = {
            "new_agent": NewAgent(),
            # ... 기존 에이전트들
        }
```

### 새 도구 추가

1. **도구 클래스 생성**

```python
# app/services/tools/new_tool.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class NewToolInput(BaseModel):
    query: str = Field(..., description="검색 쿼리")

class NewTool(BaseTool):
    name: str = "New Tool"
    description: str = """
    새로운 도구 설명
    """
    args_schema: Type[BaseModel] = NewToolInput
    
    def _run(self, query: str) -> str:
        # 도구 로직 구현
        return "결과"
```

2. **도구 등록**

```python
# app/services/tools/__init__.py
from .new_tool import NewTool

__all__ = [
    # ... 기존 도구들
    "NewTool"
]
```

### WebSocket 이벤트 처리

```python
# app/core/streaming_crew.py
async def _handle_task_event(self, task_event):
    event_type = task_event.get("type")
    step = task_event.get("step", "unknown")
    agent = task_event.get("agent", "unknown")
    status = task_event.get("status")
    
    if event_type == "task_status":
        if status == "completed":
            output = task_event.get("output", "")
            analysis = self._extract_full_answer(output)
            
            await self.ws_manager.emit({
                "type": "task_completed",
                "step": step,
                "agent": agent,
                "content": {
                    "analysis": analysis,  # 전체 JSON 응답
                    "message": f"{self.fact_crew.agents[agent].role} 작업 완료"
                }
            })
```

---

## LLM 응답 처리

### Pydantic 모델 정의

```python
# app/models/responses.py
from pydantic import BaseModel, Field
from typing import List, Literal

class Step1Analysis(BaseModel):
    class Config:
        extra = "forbid"  # Upstage API 호환성
    
    agent_name: str = Field(description="에이전트 이름")
    verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족", 
        "논란중", "부분적_거짓", "대체로_거짓", "거짓", 
        "과장됨", "오해소지", "시대착오"
    ] = Field(description="판정 결과")
    key_findings: List[str] = Field(description="핵심 발견사항")
    evidence_sources: List[str] = Field(description="근거 출처")
    reasoning: str = Field(description="판정 근거")

class Step2Debate(BaseModel):
    class Config:
        extra = "forbid"
    
    agent_name: str = Field(description="에이전트 이름")
    agreements: List[str] = Field(description="동의하는 점들")
    disagreements: List[str] = Field(description="이견이나 보완점들")
    additional_perspective: str = Field(description="추가 관점")
    final_verdict: Literal[
        "참", "대체로_참", "부분적_참", "불확실", "정보부족",
        "논란중", "부분적_거짓", "대체로_거짓", "거짓",
        "과장됨", "오해소지", "시대착오"
    ] = Field(description="최종 판정")
```

### LLM 설정

```python
# app/utils/llm_config.py
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
import os

class StructuredLLM:
    @staticmethod
    def create_structured_llm(
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> ChatOpenAI:
        base_config = {
            "model": "openai/solar-pro2",
            "api_key": os.getenv("UPSTAGE_API_KEY"),
            "base_url": "https://api.upstage.ai/v1/solar",
            "temperature": temperature,
            "max_tokens": max_tokens or 1000,
        }
        
        # Upstage structured output 설정
        if response_model:
            schema = response_model.model_json_schema()
            base_config["extra_body"] = {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "strict": True,
                        "schema": schema
                    }
                }
            }
        
        return ChatOpenAI(**base_config)

# 단계별 LLM 함수
def get_step1_llm() -> ChatOpenAI:
    from ..models.responses import Step1Analysis
    return StructuredLLM.create_structured_llm(
        response_model=Step1Analysis,
        temperature=0.1
    )
```

---

## 도구 통합 가이드

### 기본 도구 인터페이스

```python
# app/services/tools/base_tool.py
from crewai.tools import BaseTool
from pydantic import BaseModel
from typing import Type
from abc import ABC, abstractmethod

class BaseFactWaveTool(BaseTool, ABC):
    """FactWave 도구들의 기본 클래스"""
    
    @abstractmethod
    def _run(self, **kwargs) -> str:
        """도구 실행 로직"""
        pass
    
    def _format_results(self, data: dict) -> str:
        """결과를 LLM 친화적 형태로 포맷"""
        # 공통 포맷팅 로직
        pass
    
    def _handle_error(self, error: Exception) -> str:
        """에러 처리"""
        return f"❌ {self.name} 오류: {str(error)}"
```

### API 기반 도구 예시

```python
# app/services/tools/example_api_tool.py
class APIToolInput(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(default=10, description="결과 개수")

class ExampleAPITool(BaseFactWaveTool):
    name: str = "Example API Tool"
    description: str = """
    API 기반 검색 도구 예시
    """
    args_schema: Type[BaseModel] = APIToolInput
    
    def _run(self, query: str, limit: int = 10) -> str:
        try:
            # API 호출
            api_key = os.getenv("API_KEY")
            if not api_key:
                return self._get_mock_data(query)
            
            response = requests.get(
                "https://api.example.com/search",
                params={"q": query, "limit": limit},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(data)
            else:
                return f"❌ API 오류: {response.status_code}"
                
        except Exception as e:
            return self._handle_error(e)
    
    def _get_mock_data(self, query: str) -> str:
        """API 키가 없을 때 모의 데이터"""
        return f"📝 모의 검색 결과 ('{query}'에 대한 샘플 데이터)"
```

---

## 프롬프트 관리

### YAML 프롬프트 구조

```yaml
# app/config/prompts.yaml
# 판정 옵션 정의
verdict_options:
  참: "사실로 확인됨"
  대체로_참: "대체로 사실이지만 일부 불확실"
  부분적_참: "부분적으로만 사실"
  불확실: "판단하기 어려움"
  정보부족: "충분한 정보가 없음"
  논란중: "전문가들 사이에서 논란"
  부분적_거짓: "부분적으로 거짓"
  대체로_거짓: "대체로 거짓이지만 일부 사실"
  거짓: "명백히 거짓"
  과장됨: "사실이지만 과장된 부분이 있음"
  오해소지: "오해의 소지가 있는 표현"
  시대착오: "과거에는 맞았으나 현재는 틀림"

# 에이전트별 가중치
agent_weights:
  academic: 0.25    # 25%
  news: 0.30        # 30%
  social: 0.10      # 10%
  logic: 0.15       # 15%
  statistics: 0.20  # 20%

# 단계별 프롬프트
step1:
  general:
    template: |
      주장: {statement}
      
      {role}로서 이 주장을 전문적으로 분석하세요.
      
      다음 JSON 형식으로 응답하세요:
      {
        "agent_name": "{agent_name}",
        "verdict": "[참/대체로_참/부분적_참/불확실/정보부족/논란중/부분적_거짓/대체로_거짓/거짓/과장됨/오해소지/시대착오]",
        "key_findings": ["핵심 발견사항 1", "핵심 발견사항 2", "핵심 발견사항 3"],
        "evidence_sources": ["출처1", "출처2", "출처3"],
        "reasoning": "판정 근거 및 상세한 분석 내용"
      }

  logic:
    template: |
      주장: {statement}
      
      논리 및 추론 전문가로서 이 주장을 분석하세요.
      
      다음 JSON 형식으로 응답하세요:
      {
        "agent_name": "logic",
        "verdict": "[참/대체로_참/부분적_참/불확실/정보부족/논란중/부분적_거짓/대체로_거짓/거짓/과장됨/오해소지/시대착오]",
        "key_findings": ["전제와 결론 분석", "논리적 구조 검토", "발견된 오류나 문제점"],
        "evidence_sources": ["논리적 분석"],
        "reasoning": "판정 근거와 논리적 검토 과정"
      }

step2:
  template: |
    주장: {statement}
    
    {role}로서 다른 전문가들의 Step 1 분석을 검토하고 토론하세요.
    
    다음 JSON 형식으로 응답하세요:
    {
      "agent_name": "{agent_name}",
      "agreements": ["동의하는 점 1", "동의하는 점 2"],
      "disagreements": ["이견이나 보완점 1", "이견이나 보완점 2"],
      "additional_perspective": "내 전문성으로 추가하는 관점과 새로운 인사이트",
      "final_verdict": "[참/대체로_참/부분적_참/불확실/정보부족/논란중/부분적_거짓/대체로_거짓/거짓/과장됨/오해소지/시대착오]"
    }

step3:
  template: |
    주장: {statement}
    
    팩트체크 총괄 코디네이터로서 모든 전문가들의 분석과 토론을 종합하여 최종 판정을 내리세요.
    
    다음 JSON 형식으로 응답하세요:
    {
      "final_verdict": "[참/대체로_참/부분적_참/불확실/정보부족/논란중/부분적_거짓/대체로_거짓/거짓/과장됨/오해소지/시대착오]",
      "confidence_matrix": {
        "academic": 0.85,
        "news": 0.90,
        "social": 0.70,
        "logic": 0.50,
        "statistics": 0.50
      },
      "weighted_confidence": 0.78,
      "key_agreements": ["전문가들이 합의한 주요 사실 1", "전문가들이 합의한 주요 사실 2"],
      "key_disagreements": ["전문가들 간 의견이 갈린 부분 1", "전문가들 간 의견이 갈린 부분 2"],
      "summary": "종합 판정 요약과 핵심 근거",
      "verdict_reasoning": "최종 판정에 대한 상세한 근거"
    }
```

### 프롬프트 로더

```python
# app/utils/prompt_loader.py
import yaml
from pathlib import Path
from typing import Dict, Any

class PromptLoader:
    def __init__(self, config_path: str = "app/config/prompts.yaml"):
        self.config_path = Path(config_path)
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """YAML 프롬프트 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"프롬프트 로드 오류: {e}")
            return {}
    
    def get_step1_prompt(self, agent_type: str, statement: str, role: str = None, agent_name: str = None) -> str:
        """Step 1 프롬프트 생성"""
        if agent_type == 'logic':
            template = self.prompts['step1']['logic']['template']
            return template.format(statement=statement)
        else:
            template = self.prompts['step1']['general']['template']
            return template.format(
                statement=statement, 
                role=role, 
                agent_name=agent_name or agent_type
            )
    
    def get_step2_prompt(self, agent_type: str, statement: str, role: str = None, agent_name: str = None) -> str:
        """Step 2 프롬프트 생성"""
        template = self.prompts['step2']['template']
        return template.format(
            statement=statement,
            role=role,
            agent_name=agent_name or agent_type
        )
    
    def get_step3_prompt(self, statement: str) -> str:
        """Step 3 프롬프트 생성"""
        template = self.prompts['step3']['template']
        return template.format(statement=statement)
    
    def get_verdict_options(self) -> Dict[str, str]:
        """판정 옵션 반환"""
        return self.prompts.get('verdict_options', {})
    
    def get_agent_weights(self) -> Dict[str, float]:
        """에이전트 가중치 반환"""
        return self.prompts.get('agent_weights', {})
```

---

## 환경 설정

### 필수 환경 변수

```bash
# .env
# LLM 설정
UPSTAGE_API_KEY=up_xxx  # Upstage Solar API 키 (필수)

# 뉴스 검증
NAVER_CLIENT_ID=xxx     # 네이버 개발자 센터 (필수)
NAVER_CLIENT_SECRET=xxx

# 통계 데이터 (선택사항)
NEWSAPI_KEY=xxx         # NewsAPI
GOOGLE_FACT_CHECK_KEY=xxx # Google Fact Check Tools API
FRED_API_KEY=xxx        # Federal Reserve Economic Data
KOSIS_API_KEY=xxx       # 한국 통계청
YOUTUBE_API_KEY=xxx     # YouTube Data API

# 소셜 미디어 (선택사항) 
TWITTER_BEARER_TOKEN=xxx # Twitter API v2
```

### 개발 환경 설정

```bash
# Python 환경 (3.12+ 권장) - 백엔드 디렉터리에서 실행
cd backend  # 루트에서 백엔드로 이동
uv pip install -e .

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키들 추가

# 백엔드 서버 실행 (backend 디렉터리에서)
uv run python -m app.api.server

# 프론트엔드 개발 서버 실행 (별도 터미널, frontend_minho 디렉터리에서)
cd ../frontend_minho && npm install  # 최초 1회
cd ../frontend_minho && npm run dev

# 개별 도구 테스트 (backend 디렉터리에서)
uv run python test_integrated.py tools wikipedia
uv run python test_integrated.py tools naver_news

# 전체 시스템 테스트 (backend 디렉터리에서)
uv run python test_integrated.py crew "테스트 문장"
```

### 프로덕션 환경 설정

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["python", "-m", "app.api.server"]
```

---

## 디버깅 가이드

### 로그 레벨 설정

```python
import logging

# 개발 환경
logging.basicConfig(level=logging.DEBUG)

# 프로덕션 환경
logging.basicConfig(level=logging.INFO)

# 특정 모듈 로그
logger = logging.getLogger(__name__)
```

### 일반적인 문제들

#### 1. WebSocket 연결 오류

```bash
# 서버가 실행 중인지 확인
lsof -ti:8000

# 방화벽 확인
curl -I http://localhost:8000

# CORS 문제인 경우 서버 설정 확인
```

#### 2. LLM API 오류

```python
# API 키 확인
import os
print(os.getenv("UPSTAGE_API_KEY"))

# API 연결 테스트
from app.utils.llm_config import get_step1_llm
llm = get_step1_llm()
response = llm.invoke("테스트 메시지")
```

#### 3. JSON 파싱 오류

```javascript
// 브라우저 콘솔에서 확인
console.log('Raw response:', responseText);

// JSON 유효성 검사
try {
  const parsed = JSON.parse(responseText);
  console.log('Parsed:', parsed);
} catch (e) {
  console.error('Parse error:', e);
}
```

#### 4. 도구 오류

```python
# 개별 도구 테스트
from app.services.tools import WikipediaSearchTool
tool = WikipediaSearchTool()
result = tool._run("테스트 쿼리")
print(result)
```

### 프론트엔드 디버깅

```javascript
// WebSocket 연결 상태 확인
console.log('WebSocket state:', ws.readyState);
// 0: CONNECTING, 1: OPEN, 2: CLOSING, 3: CLOSED

// 메시지 디버깅
const handleWebSocketMessage = (data) => {
  console.log('수신된 메시지:', data);
  console.log('메시지 타입:', data.type);
  console.log('콘텐츠:', data.content);
  
  // JSON 파싱 디버깅
  if (data.type === 'task_completed') {
    console.log('Raw analysis:', data.content.analysis);
    const parsed = parseAgentResponse(data.content.analysis);
    console.log('Parsed analysis:', parsed);
  }
};
```

---

## 배포 가이드

### Docker 배포

```bash
# 이미지 빌드
docker build -t factwave:latest .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env factwave:latest

# Docker Compose
docker-compose up -d
```

### 클라우드 배포

#### AWS ECS

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  factwave:
    image: factwave:latest
    ports:
      - "8000:8000"
    environment:
      - UPSTAGE_API_KEY=${UPSTAGE_API_KEY}
      - NAVER_CLIENT_ID=${NAVER_CLIENT_ID}
      - NAVER_CLIENT_SECRET=${NAVER_CLIENT_SECRET}
    restart: unless-stopped
```

#### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/factwave', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/factwave']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'factwave',
      '--image', 'gcr.io/$PROJECT_ID/factwave',
      '--region', 'asia-northeast1',
      '--platform', 'managed'
    ]
```

### 모니터링

```python
# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# 메트릭스 수집
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 성능 최적화

### 백엔드 최적화

```python
# 비동기 처리
async def parallel_agent_execution():
    tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.run())
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# 캐싱
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_tool_result(tool_name: str, query: str):
    # 도구 결과 캐싱
    pass
```

### 프론트엔드 최적화

```javascript
// 메시지 가상화 (많은 메시지 처리)
import { FixedSizeList as List } from 'react-window';

const MessageList = ({ messages }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      {renderMessage(messages[index])}
    </div>
  );

  return (
    <List
      height={600}
      itemCount={messages.length}
      itemSize={100}
    >
      {Row}
    </List>
  );
};

// 메모이제이션
const MemoizedMessage = React.memo(({ message }) => {
  return renderMessage(message);
});
```

---

## 보안 가이드

### API 키 보안

```python
# 환경 변수 검증
def validate_api_keys():
    required_keys = ["UPSTAGE_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing API keys: {missing_keys}")

# API 키 마스킹
def mask_api_key(key: str) -> str:
    if len(key) > 8:
        return key[:4] + "*" * (len(key) - 8) + key[-4:]
    return "*" * len(key)
```

### 입력 검증

```python
from pydantic import BaseModel, validator

class FactCheckRequest(BaseModel):
    statement: str
    
    @validator('statement')
    def validate_statement(cls, v):
        if len(v) > 1000:
            raise ValueError('Statement too long')
        if not v.strip():
            raise ValueError('Statement cannot be empty')
        return v.strip()
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/fact-check")
@limiter.limit("5/minute")
async def fact_check(request: Request, statement: str):
    # 팩트체킹 로직
    pass
```

---

## 라이센스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

---

## 기여 가이드

1. Fork 프로젝트
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

---

## 연락처

- 프로젝트 링크: [https://github.com/your-username/factwave](https://github.com/your-username/factwave)
- 이슈 트래커: [https://github.com/your-username/factwave/issues](https://github.com/your-username/factwave/issues)