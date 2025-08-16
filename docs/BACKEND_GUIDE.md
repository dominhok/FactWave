# FactWave 백엔드 개발 가이드

## 목차

1. [아키텍처 개요](#아키텍처-개요)
2. [CrewAI 시스템](#crewai-시스템)
3. [에이전트 개발](#에이전트-개발)
4. [도구 개발](#도구-개발)
5. [LLM 통합](#llm-통합)
6. [WebSocket 스트리밍](#websocket-스트리밍)
7. [프롬프트 엔지니어링](#프롬프트-엔지니어링)
8. [데이터베이스 및 RAG](#데이터베이스-및-rag)
9. [API 개발](#api-개발)
10. [테스팅 전략](#테스팅-전략)
11. [성능 최적화](#성능-최적화)
12. [모니터링 및 로깅](#모니터링-및-로깅)

---

## 아키텍처 개요

### 시스템 구성 요소

```
┌─────────────────┐
│   FastAPI       │ ← HTTP/WebSocket 엔드포인트
│   Server        │
└─────────┬───────┘
          │
┌─────────▼───────┐
│ StreamingCrew   │ ← WebSocket 이벤트 관리
│ (Event Manager) │
└─────────┬───────┘
          │
┌─────────▼───────┐
│   FactWaveCrew  │ ← 3단계 워크플로우 조정
│ (Core Workflow) │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼───┐   ┌───▼───┐
│ 5개   │   │ 10+   │
│에이전트│   │ 도구  │
└───┬───┘   └───┬───┘
    │           │
    └─────┬─────┘
          │
    ┌─────▼─────┐
    │  LLM API  │ ← Upstage Solar-pro2
    │(Structured)│
    └───────────┘
```

### 디렉토리 구조

```
app/
├── api/
│   ├── __init__.py
│   └── server.py                    # FastAPI 서버
├── core/
│   ├── __init__.py
│   ├── crew.py                     # 메인 팩트체킹 워크플로우
│   └── streaming_crew.py           # WebSocket 스트리밍 래퍼
├── agents/
│   ├── __init__.py
│   ├── base.py                     # 기본 에이전트 클래스
│   ├── academic_agent.py           # 학술 연구 전문가
│   ├── news_agent.py              # 뉴스 검증 전문가
│   ├── social_agent.py            # 사회 맥락 분석가
│   ├── logic_agent.py             # 논리 및 추론 전문가
│   ├── statistics_agent.py        # 통계 및 데이터 전문가
│   └── super_agent.py             # 최종 종합 에이전트
├── services/
│   └── tools/                      # 연구 도구들
│       ├── __init__.py
│       ├── base_tool.py           # 도구 기본 클래스
│       ├── academic/              # 학술 도구들
│       ├── news/                  # 뉴스 도구들
│       ├── statistics/            # 통계 도구들
│       └── community/             # 커뮤니티 도구들
├── models/
│   ├── __init__.py
│   └── responses.py               # Pydantic 응답 모델
├── utils/
│   ├── __init__.py
│   ├── llm_config.py              # LLM 설정 및 구조화
│   ├── prompt_loader.py           # 프롬프트 로더
│   └── websocket_manager.py       # WebSocket 관리
├── config/
│   ├── __init__.py
│   └── prompts.yaml               # 중앙화된 프롬프트
└── tests/                         # 테스트 파일들
```

---

## CrewAI 시스템

### CrewAI 기본 개념

CrewAI는 다중 에이전트 시스템을 구축하기 위한 프레임워크입니다.

```python
# 기본 구성 요소
from crewai import Agent, Task, Crew, Process

# 에이전트 생성
agent = Agent(
    role="전문가 역할",
    goal="수행할 목표",
    backstory="배경 설명",
    tools=[tool1, tool2],  # 사용할 도구들
    llm=llm_instance      # LLM 인스턴스
)

# 태스크 생성
task = Task(
    description="태스크 설명",
    agent=agent,
    expected_output="예상되는 출력 형태",
    callback=callback_function  # 완료 시 호출될 함수
)

# 크루 생성
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential  # 또는 Process.hierarchical
)

# 실행
result = crew.kickoff()
```

### FactWave 특화 CrewAI 구조

```python
# app/core/crew.py
class FactWaveCrew:
    """3단계 팩트체킹 프로세스를 관리하는 메인 클래스"""
    
    def __init__(self, task_callback=None):
        # 프롬프트 로더 초기화
        self.prompt_loader = PromptLoader()
        
        # 에이전트 초기화
        self.agents = {
            "academic": AcademicAgent(),
            "news": NewsAgent(),
            "social": SocialAgent(),
            "logic": LogicAgent(),
            "statistics": StatisticsAgent(),
            "super": SuperAgent()
        }
        
        # 콜백 설정
        self.task_callback = task_callback
        
        # 결과 저장
        self.step1_results = {}
        self.step2_results = {}
        self.step3_result = None
    
    def fact_check(self, statement: str) -> dict:
        """메인 팩트체킹 프로세스"""
        try:
            # Step 1: 독립적 분석
            step1_results = self._execute_step1(statement)
            
            # Step 2: 토론 및 검토
            step2_results = self._execute_step2(statement)
            
            # Step 3: 최종 종합
            step3_result = self._execute_step3(statement)
            
            return self._structure_final_result(statement, step3_result)
            
        except Exception as e:
            logger.error(f"FactCheck error: {e}")
            raise
    
    def _execute_step1(self, statement: str) -> dict:
        """Step 1: 5개 에이전트 병렬 실행"""
        tasks = []
        
        for agent_name, agent_instance in [
            ("academic", self.agents["academic"]),
            ("news", self.agents["news"]),
            ("social", self.agents["social"]),
            ("logic", self.agents["logic"]),
            ("statistics", self.agents["statistics"])
        ]:
            # 태스크 생성
            task = self._create_step1_task(agent_name, agent_instance, statement)
            tasks.append(task)
        
        # 병렬 실행을 위해 개별 Crew로 실행
        results = {}
        for i, (agent_name, agent_instance) in enumerate([
            ("academic", self.agents["academic"]),
            ("news", self.agents["news"]),
            ("social", self.agents["social"]),
            ("logic", self.agents["logic"]),
            ("statistics", self.agents["statistics"])
        ]):
            individual_crew = Crew(
                agents=[agent_instance.get_agent("step1")],
                tasks=[tasks[i]],
                process=Process.sequential,
                verbose=True
            )
            
            result = individual_crew.kickoff()
            results[agent_name] = result
        
        return results
    
    def _create_step1_task(self, agent_name: str, agent_instance, statement: str) -> Task:
        """Step 1 태스크 생성"""
        # 프롬프트 생성
        if agent_name == "logic":
            description = self.prompt_loader.get_step1_prompt(
                'logic', statement
            )
        else:
            description = self.prompt_loader.get_step1_prompt(
                'general', statement, agent_instance.role, agent_name
            )
        
        # 콜백 설정
        if self.task_callback:
            task_callback_func = self._make_task_callback(agent_name, "step1")
        else:
            task_callback_func = None
        
        return Task(
            description=description,
            agent=agent_instance.get_agent("step1"),
            expected_output="구조화된 JSON 형태의 분석 결과",
            callback=task_callback_func
        )
```

### Task Callback 시스템

```python
def _make_task_callback(self, agent_name: str, step: str):
    """태스크 완료 시 호출될 콜백 함수 생성"""
    def callback(task_output):
        try:
            # 결과 저장
            output_str = str(task_output)
            
            if step == "step1":
                self.step1_results[agent_name] = output_str
            elif step == "step2":
                self.step2_results[agent_name] = output_str
            elif step == "step3":
                self.step3_result = output_str
            
            # 외부 콜백 호출 (WebSocket 스트리밍용)
            if self.task_callback:
                self.task_callback({
                    "type": "task_status",
                    "step": step,
                    "agent": agent_name,
                    "status": "completed",
                    "output": output_str,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    return callback
```

---

## 에이전트 개발

### 기본 에이전트 클래스

```python
# app/agents/base.py
from crewai import Agent
from typing import List, Any
from ..utils.llm_config import StructuredLLM

class FactWaveAgent:
    """모든 FactWave 에이전트의 기본 클래스"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools: List[Any] = []
        self.agent = None
    
    def _create_agent(self, step: str = "step1") -> Agent:
        """단계별 LLM을 사용하는 에이전트 생성"""
        # 단계에 따라 적절한 LLM 선택
        if step == "step1":
            from ..utils.llm_config import get_step1_llm
            llm = get_step1_llm()
        elif step == "step2":
            from ..utils.llm_config import get_step2_llm
            llm = get_step2_llm()
        elif step == "step3":
            from ..utils.llm_config import get_step3_llm
            llm = get_step3_llm()
        else:
            llm = StructuredLLM.get_default_llm()
        
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    
    def get_agent(self, step: str = "step1") -> Agent:
        """단계에 맞는 에이전트 인스턴스 반환"""
        # 단계가 바뀌면 새로운 agent 생성 (LLM이 달라지므로)
        self.agent = self._create_agent(step)
        return self.agent
    
    def add_tool(self, tool):
        """도구 추가"""
        self.tools.append(tool)
    
    def remove_tool(self, tool_name: str):
        """도구 제거"""
        self.tools = [tool for tool in self.tools if tool.name != tool_name]
```

### 전문 에이전트 구현 예시

```python
# app/agents/academic_agent.py
class AcademicAgent(FactWaveAgent):
    """학술 연구 전문가 에이전트"""
    
    def __init__(self):
        super().__init__(
            role="학술 연구 전문가",
            goal="학술 논문과 연구 결과를 기반으로 주장을 검증",
            backstory=self._get_backstory()
        )
        
        # 전문 도구 초기화
        self.tools = [
            WikipediaSearchTool(),
            OpenAlexTool(),
            ArxivSearchTool()
        ]
    
    def _get_backstory(self) -> str:
        """상세한 배경 설명"""
        return """
학술 연구 검증 전문가입니다. 20년 경력의 박사로서 peer review와 메타분석을 전문으로 합니다.

도구 활용 전략:
• Wikipedia: 기본 개념과 일반적 정보 확인
• OpenAlex: 학술논문 검색 및 인용 분석 (주력 도구)
• ArXiv: 최신 연구 동향 및 preprint 확인

분석 원칙:
• 메타분석과 체계적 리뷰 논문 우선 활용
• 최소 3-5개의 독립적 연구 검토
• 학계 컨센서스와 논란 사항 구분
• 연구 방법론과 표본 크기 고려
• 이해충돌과 연구비 지원 기관 확인

응답 스타일:
• 객관적이고 균형잡힌 분석
• 과학적 불확실성 명시
• 추가 연구 필요성 언급
• 비전문가도 이해할 수 있는 설명
"""
    
    def validate_research_quality(self, paper_info: dict) -> float:
        """연구 품질 점수 계산 (0.0-1.0)"""
        score = 0.0
        
        # 저널 영향력 (Impact Factor)
        if paper_info.get('impact_factor', 0) > 5:
            score += 0.3
        elif paper_info.get('impact_factor', 0) > 2:
            score += 0.2
        
        # 인용 수
        citations = paper_info.get('citations', 0)
        if citations > 100:
            score += 0.3
        elif citations > 10:
            score += 0.2
        
        # 연구 유형
        study_type = paper_info.get('study_type', '').lower()
        if 'meta-analysis' in study_type or 'systematic review' in study_type:
            score += 0.4
        elif 'randomized controlled trial' in study_type:
            score += 0.3
        
        return min(score, 1.0)
```

### 에이전트 협업 패턴

```python
# 에이전트 간 정보 공유
class AgentCommunication:
    """에이전트 간 통신 및 정보 공유"""
    
    def __init__(self):
        self.shared_context = {}
        self.agent_findings = {}
    
    def share_finding(self, agent_name: str, finding: dict):
        """다른 에이전트와 발견사항 공유"""
        if agent_name not in self.agent_findings:
            self.agent_findings[agent_name] = []
        
        self.agent_findings[agent_name].append({
            'timestamp': datetime.now(),
            'finding': finding,
            'confidence': finding.get('confidence', 0.5)
        })
    
    def get_related_findings(self, current_agent: str, topic: str) -> List[dict]:
        """관련된 다른 에이전트의 발견사항 검색"""
        related = []
        
        for agent_name, findings in self.agent_findings.items():
            if agent_name == current_agent:
                continue
                
            for finding in findings:
                if self._is_related(finding['finding'], topic):
                    related.append({
                        'agent': agent_name,
                        'finding': finding['finding'],
                        'confidence': finding['confidence']
                    })
        
        return sorted(related, key=lambda x: x['confidence'], reverse=True)
    
    def _is_related(self, finding: dict, topic: str) -> bool:
        """발견사항이 주제와 관련있는지 확인"""
        finding_text = str(finding).lower()
        topic_keywords = topic.lower().split()
        
        return any(keyword in finding_text for keyword in topic_keywords)
```

---

## 도구 개발

### 기본 도구 클래스

```python
# app/services/tools/base_tool.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseFactWaveTool(BaseTool, ABC):
    """FactWave 도구들의 기본 클래스"""
    
    # 도구 메타데이터
    category: str = "general"
    reliability_score: float = 0.8
    rate_limit: Optional[int] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._call_count = 0
        self._last_call_time = None
    
    @abstractmethod
    def _run(self, **kwargs) -> str:
        """도구 실행 로직 (반드시 구현)"""
        pass
    
    def _pre_run_checks(self) -> bool:
        """실행 전 검사"""
        # Rate limiting 체크
        if self.rate_limit and self._check_rate_limit():
            return False
        
        # API 키 확인
        if hasattr(self, '_check_api_key') and not self._check_api_key():
            return False
        
        return True
    
    def _check_rate_limit(self) -> bool:
        """Rate limit 체크"""
        current_time = time.time()
        
        if self._last_call_time:
            time_diff = current_time - self._last_call_time
            if time_diff < 60 / self.rate_limit:  # 분당 제한
                logger.warning(f"{self.name}: Rate limit exceeded")
                return True
        
        self._last_call_time = current_time
        self._call_count += 1
        return False
    
    def _format_results(self, data: Dict[str, Any]) -> str:
        """결과를 LLM 친화적 형태로 포맷"""
        if not data:
            return f"❌ {self.name}: 검색 결과가 없습니다."
        
        formatted = f"📊 {self.name} 검색 결과:\n\n"
        
        # 메타데이터 추가
        if 'total_results' in data:
            formatted += f"총 {data['total_results']}개 결과 중 주요 내용:\n\n"
        
        # 결과 포맷팅
        if 'results' in data:
            for i, result in enumerate(data['results'][:5], 1):
                formatted += f"{i}. {self._format_single_result(result)}\n\n"
        
        # 신뢰도 정보
        formatted += f"📈 신뢰도: {self.reliability_score}/1.0\n"
        formatted += f"🔗 카테고리: {self.category}\n"
        
        return formatted
    
    def _format_single_result(self, result: Dict[str, Any]) -> str:
        """개별 결과 포맷팅"""
        formatted = ""
        
        if 'title' in result:
            formatted += f"**{result['title']}**\n"
        
        if 'summary' in result:
            formatted += f"{result['summary'][:200]}...\n"
        
        if 'source' in result:
            formatted += f"출처: {result['source']}\n"
        
        if 'date' in result:
            formatted += f"날짜: {result['date']}\n"
        
        return formatted
    
    def _handle_error(self, error: Exception) -> str:
        """통합 에러 처리"""
        error_msg = str(error)
        logger.error(f"{self.name} error: {error_msg}")
        
        # 사용자 친화적 에러 메시지
        if "timeout" in error_msg.lower():
            return f"⏱️ {self.name}: 요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        elif "api key" in error_msg.lower():
            return f"🔑 {self.name}: API 인증 오류입니다. 설정을 확인해주세요."
        elif "rate limit" in error_msg.lower():
            return f"🚦 {self.name}: 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
        else:
            return f"❌ {self.name}: 오류가 발생했습니다 - {error_msg}"
    
    def get_tool_info(self) -> Dict[str, Any]:
        """도구 정보 반환"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "reliability_score": self.reliability_score,
            "call_count": self._call_count,
            "rate_limit": self.rate_limit
        }
```

### API 기반 도구 구현

```python
# app/services/tools/news/naver_news_tool.py
import requests
import os
from datetime import datetime
from typing import Optional

class NaverNewsInput(BaseModel):
    query: str = Field(..., description="뉴스 검색 키워드")
    sort: str = Field(default="sim", description="정렬 방식 (sim: 정확도순, date: 날짜순)")
    display: int = Field(default=30, description="검색 결과 출력 건수 (최대 100)")

class NaverNewsTool(BaseFactWaveTool):
    name: str = "Naver News Search"
    description: str = """
    네이버 뉴스 API를 통해 한국 뉴스를 검색합니다.
    최신 뉴스, 관련 뉴스, 특정 주제의 뉴스를 찾을 수 있습니다.
    팩트체크를 위한 다양한 언론사의 보도를 교차 검증할 수 있습니다.
    """
    args_schema: Type[BaseModel] = NaverNewsInput
    category: str = "news"
    reliability_score: float = 0.85
    rate_limit: int = 30  # 분당 30회
    
    def _check_api_key(self) -> bool:
        """API 키 확인"""
        return bool(os.getenv("NAVER_CLIENT_ID") and os.getenv("NAVER_CLIENT_SECRET"))
    
    def _run(self, query: str, sort: str = "sim", display: int = 30) -> str:
        try:
            # Pre-run 검사
            if not self._pre_run_checks():
                return self._handle_error(Exception("Pre-run checks failed"))
            
            # API 호출
            results = self._search_naver_news(query, sort, display)
            
            # 결과 포맷팅
            return self._format_results(results)
            
        except Exception as e:
            return self._handle_error(e)
    
    def _search_naver_news(self, query: str, sort: str, display: int) -> Dict[str, Any]:
        """네이버 뉴스 API 호출"""
        client_id = os.getenv("NAVER_CLIENT_ID")
        client_secret = os.getenv("NAVER_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return self._get_mock_data(query)
        
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        }
        params = {
            "query": query,
            "display": min(display, 100),
            "start": 1,
            "sort": sort
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 응답 데이터 정리
        processed_results = []
        for item in data.get('items', []):
            processed_results.append({
                'title': self._clean_html(item.get('title', '')),
                'summary': self._clean_html(item.get('description', '')),
                'source': item.get('originallink', item.get('link', '')),
                'date': self._parse_date(item.get('pubDate', '')),
                'publisher': self._extract_publisher(item.get('originallink', ''))
            })
        
        return {
            'total_results': data.get('total', 0),
            'results': processed_results,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.sub('<.*?>', '', text)
        return clean.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    def _parse_date(self, date_str: str) -> str:
        """날짜 파싱"""
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return date_str
    
    def _extract_publisher(self, url: str) -> str:
        """URL에서 언론사명 추출"""
        publishers = {
            'chosun.com': '조선일보',
            'donga.com': '동아일보',
            'joongang.co.kr': '중앙일보',
            'hankyoreh.com': '한겨레',
            'hani.co.kr': '한겨레',
            'yonhapnews.co.kr': '연합뉴스',
            'yna.co.kr': '연합뉴스',
            'sbs.co.kr': 'SBS',
            'kbs.co.kr': 'KBS',
            'mbc.co.kr': 'MBC'
        }
        
        for domain, name in publishers.items():
            if domain in url:
                return name
        
        return "기타"
    
    def _get_mock_data(self, query: str) -> Dict[str, Any]:
        """API 키가 없을 때 모의 데이터"""
        return {
            'total_results': 3,
            'results': [
                {
                    'title': f'"{query}" 관련 모의 뉴스 1',
                    'summary': f'{query}에 대한 주요 내용을 다룬 기사입니다.',
                    'source': 'https://example.com/news1',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'publisher': '모의언론사'
                },
                {
                    'title': f'"{query}" 관련 모의 뉴스 2',
                    'summary': f'{query}의 배경과 영향을 분석한 기사입니다.',
                    'source': 'https://example.com/news2',
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'publisher': '모의일보'
                }
            ],
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'note': '🧪 모의 데이터 (API 키를 설정하면 실제 데이터를 이용할 수 있습니다)'
        }
```

### 도구 테스트 프레임워크

```python
# app/services/tools/testing/tool_tester.py
import unittest
from typing import Dict, Any
import time

class ToolTester:
    """도구 테스트를 위한 프레임워크"""
    
    def __init__(self, tool_instance):
        self.tool = tool_instance
        self.test_results = []
    
    def run_basic_tests(self) -> Dict[str, Any]:
        """기본 테스트 실행"""
        results = {
            'tool_name': self.tool.name,
            'tests': {},
            'overall_score': 0.0,
            'timestamp': time.time()
        }
        
        # 1. 초기화 테스트
        results['tests']['initialization'] = self._test_initialization()
        
        # 2. 입력 검증 테스트
        results['tests']['input_validation'] = self._test_input_validation()
        
        # 3. 실행 테스트
        results['tests']['execution'] = self._test_execution()
        
        # 4. 에러 처리 테스트
        results['tests']['error_handling'] = self._test_error_handling()
        
        # 5. 출력 형식 테스트
        results['tests']['output_format'] = self._test_output_format()
        
        # 전체 점수 계산
        scores = [test['score'] for test in results['tests'].values()]
        results['overall_score'] = sum(scores) / len(scores)
        
        return results
    
    def _test_initialization(self) -> Dict[str, Any]:
        """초기화 테스트"""
        try:
            # 필수 속성 확인
            required_attrs = ['name', 'description', 'args_schema']
            missing_attrs = [attr for attr in required_attrs if not hasattr(self.tool, attr)]
            
            if missing_attrs:
                return {
                    'passed': False,
                    'score': 0.0,
                    'message': f'Missing attributes: {missing_attrs}'
                }
            
            return {
                'passed': True,
                'score': 1.0,
                'message': 'All required attributes present'
            }
        except Exception as e:
            return {
                'passed': False,
                'score': 0.0,
                'message': f'Initialization error: {str(e)}'
            }
    
    def _test_execution(self) -> Dict[str, Any]:
        """실행 테스트"""
        try:
            # 테스트 쿼리로 실행
            test_query = "test query"
            result = self.tool._run(test_query)
            
            if isinstance(result, str) and len(result) > 0:
                return {
                    'passed': True,
                    'score': 1.0,
                    'message': 'Tool executed successfully',
                    'output_length': len(result)
                }
            else:
                return {
                    'passed': False,
                    'score': 0.5,
                    'message': 'Tool returned empty or invalid result'
                }
        except Exception as e:
            return {
                'passed': False,
                'score': 0.0,
                'message': f'Execution error: {str(e)}'
            }
```

---

## LLM 통합

### Upstage Structured Output 설정

```python
# app/utils/llm_config.py
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Type, Optional, Dict, Any
import os
import json

class StructuredLLM:
    """Upstage API를 이용한 구조화된 LLM 응답"""
    
    @staticmethod
    def create_structured_llm(
        response_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> ChatOpenAI:
        """구조화된 출력을 지원하는 LLM 생성"""
        
        base_config = {
            "model": "openai/solar-pro2",  # litellm 호환 형식
            "api_key": os.getenv("UPSTAGE_API_KEY"),
            "base_url": "https://api.upstage.ai/v1/solar",
            "temperature": temperature,
            "max_tokens": max_tokens or 1000,
        }
        
        # Upstage structured output 설정
        if response_model:
            schema = response_model.model_json_schema()
            
            # Upstage API 호환 스키마 처리
            processed_schema = StructuredLLM._process_schema_for_upstage(schema)
            
            base_config["extra_body"] = {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "strict": True,
                        "schema": processed_schema
                    }
                }
            }
        
        return ChatOpenAI(**base_config)
    
    @staticmethod
    def _process_schema_for_upstage(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Upstage API를 위한 스키마 전처리"""
        # additionalProperties = false 설정
        if "properties" in schema:
            schema["additionalProperties"] = False
        
        # required 필드 보장
        if "required" not in schema and "properties" in schema:
            schema["required"] = list(schema["properties"].keys())
        
        # 중첩 객체 처리
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_schema.get("type") == "object":
                    schema["properties"][prop_name] = StructuredLLM._process_schema_for_upstage(prop_schema)
        
        return schema
    
    @staticmethod
    def validate_api_key() -> bool:
        """API 키 유효성 검사"""
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            return False
        
        try:
            # 간단한 테스트 호출
            test_llm = ChatOpenAI(
                model="openai/solar-pro2",
                api_key=api_key,
                base_url="https://api.upstage.ai/v1/solar",
                max_tokens=10
            )
            
            response = test_llm.invoke("Hello")
            return bool(response.content)
            
        except Exception:
            return False

# 단계별 LLM 생성 함수들
def get_step1_llm() -> ChatOpenAI:
    """Step 1 분석용 LLM (구조화된 응답)"""
    from ..models.responses import Step1Analysis
    return StructuredLLM.create_structured_llm(
        response_model=Step1Analysis,
        temperature=0.1,
        max_tokens=1500
    )

def get_step2_llm() -> ChatOpenAI:
    """Step 2 토론용 LLM (구조화된 응답)"""
    from ..models.responses import Step2Debate
    return StructuredLLM.create_structured_llm(
        response_model=Step2Debate,
        temperature=0.2,
        max_tokens=1200
    )

def get_step3_llm() -> ChatOpenAI:
    """Step 3 종합용 LLM (구조화된 응답)"""
    from ..models.responses import Step3Synthesis
    return StructuredLLM.create_structured_llm(
        response_model=Step3Synthesis,
        temperature=0.1,
        max_tokens=2000
    )

def get_unstructured_llm() -> ChatOpenAI:
    """비구조화 출력용 LLM"""
    return StructuredLLM.create_structured_llm(
        response_model=None,
        temperature=0.3,
        max_tokens=1000
    )
```

### LLM 응답 처리 및 검증

```python
# app/utils/llm_validator.py
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError

class LLMResponseValidator:
    """LLM 응답 검증 및 후처리"""
    
    @staticmethod
    def validate_and_parse(
        response_text: str, 
        expected_model: Type[BaseModel]
    ) -> Optional[Dict[str, Any]]:
        """LLM 응답을 검증하고 파싱"""
        
        # 1. JSON 추출
        json_data = LLMResponseValidator._extract_json(response_text)
        if not json_data:
            return None
        
        # 2. Pydantic 모델로 검증
        try:
            validated_data = expected_model.model_validate(json_data)
            return validated_data.model_dump()
        except ValidationError as e:
            print(f"Validation error: {e}")
            return None
    
    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """텍스트에서 JSON 추출"""
        text = text.strip()
        
        # 1. 전체 텍스트가 JSON인지 확인
        if text.startswith('{') and text.endswith('}'):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        
        # 2. ```json 블록 찾기
        import re
        json_blocks = re.findall(r'```json\s*\n(.*?)\n```', text, re.DOTALL)
        for block in json_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue
        
        # 3. 중괄호로 둘러싸인 부분 찾기
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return None
    
    @staticmethod
    def clean_response(response_text: str) -> str:
        """응답 텍스트 정리"""
        # 불필요한 접두사/접미사 제거
        prefixes_to_remove = [
            "다음은 분석 결과입니다:",
            "JSON 형식으로 응답드리겠습니다:",
            "분석 결과는 다음과 같습니다:"
        ]
        
        cleaned = response_text.strip()
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        
        return cleaned
    
    @staticmethod
    def fallback_parsing(response_text: str) -> Dict[str, Any]:
        """파싱 실패 시 대안 방법"""
        result = {
            "agent_name": "unknown",
            "verdict": "정보부족",
            "key_findings": [],
            "evidence_sources": [],
            "reasoning": response_text[:500] + "..." if len(response_text) > 500 else response_text
        }
        
        # 간단한 키워드 추출
        import re
        
        # 판정 키워드 찾기
        verdicts = ["참", "거짓", "대체로_참", "대체로_거짓", "부분적_참", "불확실", "정보부족"]
        for verdict in verdicts:
            if verdict in response_text:
                result["verdict"] = verdict
                break
        
        # 근거 키워드 찾기
        reasoning_patterns = [
            r"근거[:\s]*(.+?)(?:\n|$)",
            r"판정[:\s]*(.+?)(?:\n|$)",
            r"결론[:\s]*(.+?)(?:\n|$)"
        ]
        
        for pattern in reasoning_patterns:
            match = re.search(pattern, response_text)
            if match:
                result["reasoning"] = match.group(1).strip()
                break
        
        return result
```

### LLM 성능 모니터링

```python
# app/utils/llm_monitor.py
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LLMCall:
    """LLM 호출 기록"""
    timestamp: datetime
    step: str
    agent: str
    prompt_length: int
    response_length: int
    duration: float
    success: bool
    error_message: Optional[str] = None

class LLMMonitor:
    """LLM 호출 모니터링"""
    
    def __init__(self):
        self.calls: List[LLMCall] = []
        self._total_tokens_used = 0
        self._total_cost = 0.0
    
    def start_call(self, step: str, agent: str, prompt: str) -> str:
        """LLM 호출 시작"""
        call_id = f"{step}_{agent}_{int(time.time())}"
        
        self._current_call = {
            'id': call_id,
            'step': step,
            'agent': agent,
            'prompt': prompt,
            'start_time': time.time(),
            'timestamp': datetime.now()
        }
        
        return call_id
    
    def end_call(self, call_id: str, response: str, success: bool = True, error: str = None):
        """LLM 호출 종료"""
        if not hasattr(self, '_current_call'):
            return
        
        duration = time.time() - self._current_call['start_time']
        
        call_record = LLMCall(
            timestamp=self._current_call['timestamp'],
            step=self._current_call['step'],
            agent=self._current_call['agent'],
            prompt_length=len(self._current_call['prompt']),
            response_length=len(response) if response else 0,
            duration=duration,
            success=success,
            error_message=error
        )
        
        self.calls.append(call_record)
        
        # 토큰 및 비용 추정
        self._estimate_usage(call_record)
    
    def _estimate_usage(self, call: LLMCall):
        """토큰 사용량 및 비용 추정"""
        # 간단한 토큰 추정 (1 token ≈ 4 characters)
        input_tokens = call.prompt_length // 4
        output_tokens = call.response_length // 4
        total_tokens = input_tokens + output_tokens
        
        self._total_tokens_used += total_tokens
        
        # Upstage Solar-pro2 가격 추정 (예시)
        cost_per_1k_tokens = 0.002  # $0.002 per 1K tokens
        call_cost = (total_tokens / 1000) * cost_per_1k_tokens
        self._total_cost += call_cost
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        if not self.calls:
            return {"message": "No LLM calls recorded"}
        
        successful_calls = [call for call in self.calls if call.success]
        failed_calls = [call for call in self.calls if not call.success]
        
        return {
            "total_calls": len(self.calls),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "success_rate": len(successful_calls) / len(self.calls) * 100,
            "average_duration": sum(call.duration for call in self.calls) / len(self.calls),
            "total_tokens_estimated": self._total_tokens_used,
            "estimated_cost": self._total_cost,
            "calls_by_step": self._group_by_step(),
            "calls_by_agent": self._group_by_agent()
        }
    
    def _group_by_step(self) -> Dict[str, int]:
        """단계별 호출 수"""
        step_counts = {}
        for call in self.calls:
            step_counts[call.step] = step_counts.get(call.step, 0) + 1
        return step_counts
    
    def _group_by_agent(self) -> Dict[str, int]:
        """에이전트별 호출 수"""
        agent_counts = {}
        for call in self.calls:
            agent_counts[call.agent] = agent_counts.get(call.agent, 0) + 1
        return agent_counts
```

---

## WebSocket 스트리밍

### WebSocket 관리자

```python
# app/utils/websocket_manager.py
import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket 연결 및 메시지 관리"""
    
    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.connections: Dict[str, Any] = {}
        self.message_queue = asyncio.Queue()
    
    async def connect(self, websocket, session_id: str):
        """WebSocket 연결 등록"""
        self.connections[session_id] = {
            'websocket': websocket,
            'connected_at': datetime.now(),
            'message_count': 0
        }
        
        # 연결 확인 메시지
        await self.emit({
            "type": "connection_established",
            "content": {
                "session_id": session_id,
                "message": "WebSocket 연결이 설정되었습니다",
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }, session_id)
        
        logger.info(f"WebSocket connected: {session_id}")
    
    async def disconnect(self, session_id: str):
        """WebSocket 연결 해제"""
        if session_id in self.connections:
            del self.connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def emit(self, message: Dict[str, Any], session_id: Optional[str] = None):
        """메시지 전송"""
        try:
            # 타임스탬프 추가
            message.setdefault("timestamp", datetime.now().isoformat())
            
            if session_id and session_id in self.connections:
                # 특정 세션으로 전송
                websocket = self.connections[session_id]['websocket']
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
                self.connections[session_id]['message_count'] += 1
            else:
                # 모든 연결된 세션으로 브로드캐스트
                disconnected_sessions = []
                for sid, connection in self.connections.items():
                    try:
                        await connection['websocket'].send_text(
                            json.dumps(message, ensure_ascii=False)
                        )
                        connection['message_count'] += 1
                    except Exception as e:
                        logger.error(f"Failed to send message to {sid}: {e}")
                        disconnected_sessions.append(sid)
                
                # 연결이 끊어진 세션 정리
                for sid in disconnected_sessions:
                    await self.disconnect(sid)
            
            # 외부 콜백 호출
            if self.callback:
                await self._safe_callback(message)
                
        except Exception as e:
            logger.error(f"Error emitting message: {e}")
    
    async def emit_error(self, error_message: str, details: Optional[Dict[str, Any]] = None):
        """에러 메시지 전송"""
        error_msg = {
            "type": "error",
            "content": {
                "error": error_message,
                "details": details or {},
                "timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await self.emit(error_msg)
    
    async def _safe_callback(self, message: Dict[str, Any]):
        """안전한 콜백 호출"""
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(message)
            else:
                self.callback(message)
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """연결 통계 반환"""
        return {
            "total_connections": len(self.connections),
            "connections": {
                session_id: {
                    "connected_at": conn["connected_at"].isoformat(),
                    "message_count": conn["message_count"]
                }
                for session_id, conn in self.connections.items()
            }
        }

class StreamingCallback:
    """CrewAI 콜백을 WebSocket으로 변환하는 어댑터"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.ws_manager = websocket_manager
    
    async def on_agent_start(self, agent_name: str, step: str):
        """에이전트 시작 알림"""
        await self.ws_manager.emit({
            "type": "agent_start",
            "step": step,
            "agent": agent_name,
            "content": {
                "message": f"{agent_name} 작업 시작",
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def on_agent_complete(self, agent_name: str, step: str, result: str):
        """에이전트 완료 알림"""
        await self.ws_manager.emit({
            "type": "agent_complete", 
            "step": step,
            "agent": agent_name,
            "content": {
                "message": f"{agent_name} 작업 완료",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def on_step_start(self, step: str, description: str):
        """단계 시작 알림"""
        await self.ws_manager.emit({
            "type": "step_start",
            "step": step,
            "content": {
                "name": f"Step {step[-1]}: {description}",
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def on_step_complete(self, step: str, summary: str):
        """단계 완료 알림"""
        await self.ws_manager.emit({
            "type": "step_complete",
            "step": step,
            "content": {
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
        })
```

### 스트리밍 크루 구현

```python
# app/core/streaming_crew.py (핵심 부분)
class StreamingFactWaveCrew:
    """WebSocket 스트리밍을 지원하는 팩트체킹 크루"""
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        # WebSocket 관리자 설정
        self.ws_manager = WebSocketManager(callback=websocket_callback)
        self.streaming_callback = StreamingCallback(self.ws_manager)
        
        # Task 콜백 생성 (CrewAI와 호환)
        def task_callback(task_event):
            try:
                # 비동기 처리를 위한 래핑
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._handle_task_event(task_event))
                else:
                    loop.run_until_complete(self._handle_task_event(task_event))
            except RuntimeError:
                # 새 스레드에서 실행
                import threading
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(self._handle_task_event(task_event))
                    new_loop.close()
                
                thread = threading.Thread(target=run_async)
                thread.start()
        
        # 실제 FactWaveCrew 인스턴스 (task_callback 전달)
        self.fact_crew = FactWaveCrew(task_callback=task_callback)
    
    async def fact_check_streaming(self, statement: str) -> Dict[str, Any]:
        """스트리밍 팩트체킹 실행"""
        try:
            # 시작 알림
            await self.ws_manager.emit({
                "type": "fact_check_started",
                "content": {
                    "statement": statement,
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            # 비동기로 팩트체킹 실행
            result = await self._run_fact_check_async(statement)
            
            # 최종 결과 전송
            await self.ws_manager.emit({
                "type": "final_result",
                "content": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Streaming fact-check error: {e}")
            await self.ws_manager.emit_error(str(e), {"statement": statement})
            raise
    
    async def _run_fact_check_async(self, statement: str) -> Dict[str, Any]:
        """비동기 팩트체킹 실행"""
        import concurrent.futures
        
        # 스레드 풀에서 동기 팩트체킹 실행
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.fact_crew.fact_check, statement)
            result = await asyncio.wrap_future(future)
        
        return result
    
    async def _handle_task_event(self, task_event):
        """CrewAI 태스크 이벤트를 WebSocket으로 변환"""
        try:
            event_type = task_event.get("type")
            step = task_event.get("step", "unknown")
            agent = task_event.get("agent", "unknown")
            status = task_event.get("status")
            
            if event_type == "task_status":
                if status == "started":
                    await self.ws_manager.emit({
                        "type": "task_started",
                        "step": step,
                        "agent": agent,
                        "content": {
                            "message": f"{self.fact_crew.agents[agent].role} 작업 시작",
                            "task_id": str(task_event.get("task_id", ""))[:8],
                            "role": self.fact_crew.agents[agent].role
                        }
                    })
                    
                elif status == "completed":
                    output = task_event.get("output", "")
                    analysis = self._extract_full_answer(output) if output else "완료"
                    
                    await self.ws_manager.emit({
                        "type": "task_completed",
                        "step": step,
                        "agent": agent,
                        "content": {
                            "message": f"{self.fact_crew.agents[agent].role} 작업 완료",
                            "analysis": analysis,  # 전체 JSON 응답
                            "role": self.fact_crew.agents[agent].role
                        }
                    })
        
        except Exception as e:
            logger.error(f"Task event handling error: {e}")
            await self.ws_manager.emit_error(str(e), {"task_event": task_event})
```

---

## API 개발

### FastAPI 서버 구현

```python
# app/api/server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any
from datetime import datetime

from ..core.streaming_crew import StreamingFactWaveCrew
from ..utils.websocket_manager import WebSocketManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FactWave API",
    description="AI 기반 실시간 팩트체킹 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 상태
active_sessions: Dict[str, StreamingFactWaveCrew] = {}

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    logger.info("FactWave API 서버 시작")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리"""
    logger.info("FactWave API 서버 종료")
    # 활성 세션 정리
    for session_id in list(active_sessions.keys()):
        del active_sessions[session_id]

@app.get("/")
async def root():
    """기본 엔드포인트"""
    return {
        "message": "FactWave API Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions)
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(active_sessions),
        "server_info": {
            "python_version": "3.12+",
            "framework": "FastAPI",
            "llm_provider": "Upstage Solar-pro2"
        }
    }

@app.get("/api/sessions")
async def get_active_sessions():
    """활성 세션 목록"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": list(active_sessions.keys())
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 엔드포인트"""
    await websocket.accept()
    
    try:
        # 스트리밍 크루 생성
        streaming_crew = StreamingFactWaveCrew()
        active_sessions[session_id] = streaming_crew
        
        # WebSocket 연결 등록
        await streaming_crew.ws_manager.connect(websocket, session_id)
        
        # 메시지 처리 루프
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_json()
            
            if data.get("action") == "start_fact_check":
                statement = data.get("statement")
                if not statement:
                    await streaming_crew.ws_manager.emit_error(
                        "검증할 문장이 제공되지 않았습니다",
                        {"received_data": data}
                    )
                    continue
                
                logger.info(f"팩트체킹 시작: {statement[:50]}...")
                
                try:
                    # 스트리밍 팩트체킹 실행
                    result = await streaming_crew.fact_check_streaming(statement)
                    logger.info(f"팩트체킹 완료: {session_id}")
                    
                except Exception as e:
                    logger.error(f"팩트체킹 오류: {e}")
                    await streaming_crew.ws_manager.emit_error(
                        f"팩트체킹 중 오류가 발생했습니다: {str(e)}",
                        {"statement": statement, "error_type": type(e).__name__}
                    )
            
            elif data.get("action") == "ping":
                # Ping-pong for connection health
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            
            else:
                logger.warning(f"Unknown action: {data.get('action')}")
                await streaming_crew.ws_manager.emit_error(
                    f"알 수 없는 액션: {data.get('action')}",
                    {"received_data": data}
                )
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket 연결 끊어짐: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
    finally:
        # 세션 정리
        if session_id in active_sessions:
            await active_sessions[session_id].ws_manager.disconnect(session_id)
            del active_sessions[session_id]
        logger.info(f"세션 정리 완료: {session_id}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/api/tools/status")
async def get_tools_status():
    """도구 상태 확인"""
    from ..services.tools import (
        WikipediaSearchTool, NaverNewsTool, KOSISSearchTool,
        WorldBankSearchTool, FREDSearchTool, TwitterTool
    )
    
    tools_status = {}
    
    # 각 도구의 상태 확인
    test_tools = [
        ("Wikipedia", WikipediaSearchTool()),
        ("Naver News", NaverNewsTool()),
        ("KOSIS", KOSISSearchTool()),
        ("World Bank", WorldBankSearchTool()),
        ("FRED", FREDSearchTool()),
        ("Twitter", TwitterTool())
    ]
    
    for tool_name, tool_instance in test_tools:
        try:
            # 간단한 테스트 실행
            result = tool_instance._run("test")
            tools_status[tool_name] = {
                "status": "available",
                "has_api_key": hasattr(tool_instance, '_check_api_key') and tool_instance._check_api_key(),
                "category": getattr(tool_instance, 'category', 'unknown'),
                "reliability": getattr(tool_instance, 'reliability_score', 0.5)
            }
        except Exception as e:
            tools_status[tool_name] = {
                "status": "error",
                "error": str(e),
                "has_api_key": False
            }
    
    return {
        "tools": tools_status,
        "summary": {
            "total_tools": len(test_tools),
            "available_tools": len([t for t in tools_status.values() if t["status"] == "available"]),
            "tools_with_api_keys": len([t for t in tools_status.values() if t.get("has_api_key")])
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### REST API 엔드포인트 (추가)

```python
# REST API 추가 엔드포인트들
@app.post("/api/fact-check")
async def fact_check_sync(request: Dict[str, Any]):
    """동기식 팩트체킹 (WebSocket 없이)"""
    try:
        statement = request.get("statement")
        if not statement:
            raise HTTPException(status_code=400, detail="Statement is required")
        
        # 임시 세션으로 팩트체킹 실행
        temp_crew = FactWaveCrew()
        result = temp_crew.fact_check(statement)
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Sync fact-check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def get_agents_info():
    """에이전트 정보 조회"""
    from ..agents import (
        AcademicAgent, NewsAgent, SocialAgent,
        LogicAgent, StatisticsAgent, SuperAgent
    )
    
    agents_info = {}
    agent_classes = [
        ("academic", AcademicAgent),
        ("news", NewsAgent),
        ("social", SocialAgent),
        ("logic", LogicAgent),
        ("statistics", StatisticsAgent),
        ("super", SuperAgent)
    ]
    
    for agent_id, agent_class in agent_classes:
        agent_instance = agent_class()
        agents_info[agent_id] = {
            "role": agent_instance.role,
            "goal": agent_instance.goal,
            "tools": [tool.name for tool in agent_instance.tools] if hasattr(agent_instance, 'tools') else [],
            "backstory_length": len(agent_instance.backstory),
            "category": getattr(agent_instance, 'category', 'general')
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info)
    }

@app.post("/api/tools/{tool_name}/test")
async def test_tool(tool_name: str, request: Dict[str, Any]):
    """개별 도구 테스트"""
    try:
        # 도구 동적 임포트
        from ..services.tools import (
            WikipediaSearchTool, NaverNewsTool, KOSISSearchTool
        )
        
        tool_mapping = {
            "wikipedia": WikipediaSearchTool,
            "naver_news": NaverNewsTool,
            "kosis": KOSISSearchTool
        }
        
        if tool_name not in tool_mapping:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        tool_class = tool_mapping[tool_name]
        tool_instance = tool_class()
        
        # 테스트 쿼리 실행
        query = request.get("query", "test")
        result = tool_instance._run(query)
        
        return {
            "tool": tool_name,
            "query": query,
            "result": result,
            "tool_info": tool_instance.get_tool_info() if hasattr(tool_instance, 'get_tool_info') else {},
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Tool test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

이제 FactWave 백엔드 시스템의 모든 주요 컴포넌트를 다룬 종합적인 개발 가이드가 완성되었습니다! 

**생성된 문서들:**
1. `API_SPECIFICATION.md` - WebSocket API 명세서
2. `DEVELOPMENT_GUIDE.md` - 전체 개발 가이드 
3. `FRONTEND_GUIDE.md` - 프론트엔드 전용 가이드
4. `BACKEND_GUIDE.md` - 백엔드 전용 가이드

이제 개발자들이 FactWave 시스템을 완전히 이해하고 확장할 수 있는 포괄적인 문서화가 완료되었어! 🎉