# FactWave PRD

## 1. 제품 개요

### 1.1 목적
사용자가 입력한 문장이나 주장에 대해 여러 AI 에이전트가 협업하여 팩트체크를 수행하는 시스템

### 1.2 핵심 가치
- **정확성**: 다중 에이전트의 토론을 통한 신뢰도 높은 팩트체크
- **투명성**: 판단 과정과 근거를 명확히 제시
- **효율성**: 빠른 응답 시간으로 실시간 팩트체크 지원

## 2. 기술 스택

### 2.1 Backend
- **FastAPI**: REST API 서버
- **CrewAI**: 다중 에이전트 협업 프레임워크
- **Python 3.9+**: 주 개발 언어

### 2.2 AI/ML
- **Upstage solar-pro2** 또는 **Claude**: 언어 모델
- **검색 API**: 실시간 정보 수집 (Google Search API, Bing API 등)

## 3. 시스템 아키텍처

### 3.1 에이전트 구성
```
사용자 쿼리 → FastAPI → CrewAI Crew → 3단계 토론 → 슈퍼 에이전트 → 결과 반환

5개 전문 에이전트:
1. Academic Agent: 학술 논문, 정부 통계, 공식 기관 데이터 전문
2. Social Intelligence Agent: 소셜미디어, 커뮤니티, 여론 트렌드 분석
3. News Verification Agent: 뉴스 소스 교차검증, 미디어 바이어스 고려
4. Logic Verification Agent: 논리적 일관성, 인과관계 검증

+ Super Agent: 최종 합의 도출 및 신뢰도 매트릭스 생성
```

### 3.2 실시간 응답 프로세스 (스트리밍 방식)
**실시간 스트리밍 응답**
- 사용자가 즉시 진행상황과 중간결과를 확인 가능
- WebSocket 또는 Server-Sent Events(SSE) 활용
- 각 에이전트 결과를 실시간으로 전송

**단계별 응답 시간**
- **즉시 응답 (0초)**: "팩트체크를 시작합니다..."
- **5초 내**: Academic, News 에이전트 1차 결과
- **10초 내**: Social, Historical 에이전트 결과  
- **15초 내**: Logic, Bias 에이전트 결과
- **20초 내**: 최종 종합 판단

**병렬 처리 최적화**
- 6개 에이전트 완전 병렬 실행 (순차 대기 없음)
- 캐시 히트 시 1-2초 내 즉시 응답
- 타임아웃: 에이전트당 10초, 전체 최대 25초

## 4. 핵심 기능 명세

### 4.1 MVP 기능

#### 4.1.1 실시간 팩트체크 API (WebSocket)
```python
# WebSocket 연결
ws://localhost:8000/ws/factcheck

# 요청 메시지
{
    "type": "start_factcheck",
    "data": {
        "statement": "팩트체크할 문장",
        "language": "ko",
        "priority": "speed"  # speed, accuracy, comprehensive
    }
}

# 실시간 응답 스트림
{
    "type": "status",
    "timestamp": "2025-07-25T10:00:00Z",
    "message": "팩트체크를 시작합니다...",
    "progress": 0
}

{
    "type": "agent_result",
    "agent": "academic",
    "timestamp": "2025-07-25T10:00:03Z",
    "progress": 20,
    "data": {
        "verdict": "LIKELY_TRUE",
        "confidence": 0.85,
        "sources": [{"title": "통계청 발표", "url": "..."}],
        "summary": "공식 통계에 따르면..."
    }
}

{
    "type": "agent_result", 
    "agent": "news",
    "timestamp": "2025-07-25T10:00:05Z",
    "progress": 40,
    "data": {...}
}

# 최종 결과
{
    "type": "final_result",
    "timestamp": "2025-07-25T10:00:18Z",
    "progress": 100,
    "data": {
        "overall_verdict": "TRUE",
        "confidence_matrix": {...},
        "processing_time": 18.2
    }
}
```

#### 4.1.2 REST API (빠른 응답 모드)
```python
POST /api/v1/factcheck/quick
{
    "statement": "팩트체크할 문장",
    "timeout": 10  # 최대 대기시간 (초)
}

Response (10초 내):
{
    "statement": "원본 문장",
    "quick_verdict": "LIKELY_TRU E",
    "confidence": 0.78,
    "completed_agents": ["academic", "news", "logic"],
    "pending_agents": ["social", "historical", "bias"],
    "partial_summary": "현재까지의 분석 결과...",
    "full_result_url": "/api/v1/results/{task_id}"  # 전체 결과는 별도 조회
}
```

#### 4.1.2 헬스체크 API
```python
GET /health
Response: {"status": "healthy", "timestamp": "..."}
```

### 4.2 전문 에이전트 상세 역할

#### Academic Agent
- **목표**: 학술적 신뢰성 높은 정보 수집 및 검증
- **주요 API**:
  - Semantic Scholar API (214M 논문, SPECTER2 임베딩)
  - OpenAlex API (209M 논문 메타데이터)
  - ArXiv API (CS/물리/수학)
  - PubMed API (의학/생명과학)
  - Wikipedia API (배경정보, 5K req/hour)
  - 정부 공식 통계
  - 공공데이터 API 등등
- **처리 로직**: Redis 1시간 캐싱, 중복 제거 알고리즘
- **출력**: 논문 인용, 공식 통계, 연구 결과
- **가중치**: 높음 (0.3)

#### Social Intelligence Agent  
- **목표**: 사회적 맥락과 대중 인식 분석
- **주요 API**:
  - YouTube Data API (10K units/일 무료)
  - Discord API (무료, 실시간)
  - Telegram API (무료, 실시간)
  - Reddit API ($24/월부터, 선택적)
  - X/Twitter API ($200/월, 선택적)
- **한국 커뮤니티**: Playwright 크롤링 (네이버카페, 디시인사이드 등)
- **출력**: 여론 동향, 사회적 합의 수준, 논란 포인트
- **가중치**: 중간 (0.15)

#### News Verification Agent
- **목표**: 언론 보도의 정확성과 편향성 검증
- **주요 API**:
  - 네이버 뉴스 API (25K/일 무료)
  - 빅카인즈 API (한국언론진흥재단)
  - NewsAPI.org (개발용 무료)
  - Guardian API (완전 무료)
  - Google Fact Check Tools API (적극 사용해보기)
- **처리**: RSS 피드 + 웹 크롤링 병행
- **출력**: 보도 일치도, 미디어 바이어스 점수, 정정보도 여부
- **가중치**: 높음 (0.35)

#### Logic Verification Agent
- **목표**: 논리적 일관성과 인과관계 검증
- **데이터 소스**: 논리 구조 분석, 추론 체계
- **도구**: 논리 검증 알고리즘, 인과관계 분석
- **출력**: 논리적 모순 지적, 추론 오류 탐지, 인과관계 검증
- **가중치**: 높음 (0.2)

#### Super Agent
- **목표**: 전체 에이전트 의견 종합 및 최종 판단
- **기능**: 
  - 신뢰도 매트릭스 생성
  - 불확실성 지표 계산

## 6. 기술적 구현 상세

### 6.1 검색 시스템 설계 (2025년 7월 기준)

**Academic Agent APIs**
- **Semantic Scholar API**: 214백만 논문, SPECTER2 임베딩, TL;DR 자동요약 (무료)
- **OpenAlex API**: 209백만 논문 메타데이터 (무료)
- **ArXiv API**: CS/물리/수학 논문 전문 (무료)
- **PubMed API**: 의학/생명과학 논문 (무료)
- **Crossref API**: DOI 기반 메타데이터 (무료)
- **Wikipedia API**: 배경정보, 시간당 5,000회 요청 (무료)

**News Verification Agent APIs**
- **네이버 뉴스 API**: 일 25,000회 무료
- **빅카인즈 API**: 한국언론진흥재단 뉴스 아카이브
- **NewsAPI.org**: 개발용 무료, 글로벌 뉴스
- **Guardian API**: 완전 무료
- **Google Fact Check Tools API**: PolitiFact, FactCheck.org, Snopes 연동

**Social Intelligence Agent APIs**
- **한국 커뮤니티**: API 없음, Playwright 크롤링 필요

**정부/공공 APIs**
- **공공데이터포털 API**: 정부 공식 데이터
- **통계청 KOSIS API**: 공식 통계
- **한국은행 경제통계 API**: 경제 지표

**캐싱 전략**
- **Redis 기반 검색 결과 캐싱**
  - Academic 데이터: TTL 1시간 (논문은 변하지 않음)
  - News 데이터: TTL 30분 (실시간성 중요)
  - Social 데이터: TTL 15분 (빠른 변화)
- **API 사용량 관리**
  - 네이버 뉴스: 25,000회/일 → 약 17회/분
  - YouTube: 10,000 units/일 → 약 7 units/분
  - Semantic Scholar: Rate limit 준수
- **중복 검색 방지**: 동일 키워드 24시간 캐시

### 6.3 실시간 성능 최적화
- **목표 응답시간**: 
  - 첫 번째 결과: 3-5초 이내
  - 전체 완료: 25초 이내
  - 캐시 히트: 1-2초 즉시 응답
- **동시 요청 처리**: 50개 요청/분
- **병렬 처리**: 6개 에이전트 완전 병렬 실행
- **WebSocket 연결**: 최대 1000개 동시 연결

### 6.4 사용자 경험 최적화
**즉시 피드백**
- 쿼리 접수 즉시 "분석 시작" 메시지
- 3초 내 첫 번째 에이전트 결과 표시
- 진행률 바와 실시간 상태 업데이트

**Early Warning 시스템**
- 명백히 거짓인 경우 5초 내 경고
- 정보 부족 시 즉시 알림
- 논란이 많은 주제 사전 안내

**캐싱 전략**
- 인기 주제/최근 검색어 사전 캐싱
- 유사 문장 패턴 매칭으로 빠른 응답
- 실시간 트렌딩 토픽 모니터링

### 6.4 확장성 고려
**도메인 특화 모드**
- 의료: PubMed 중심, 임상시험 데이터 강화
- 정치: 정부 공식 발표, 선거 관련 DB 우선
- 과학: arXiv, Nature/Science 등 저널 중심
- 경제: 금융 데이터, 기업 보고서 중심

**다국어 지원**
- 언어별 전용 검색 API 설정
- 번역 API 연동 (Google Translate, Papago)
- 문화적 맥락 고려한 편향성 분석

## 7. 실시간 응답 플로우 예시

```
입력: "2024년 한국의 출산율이 0.7명이다"

=== 즉시 응답 (0초) ===
WebSocket → "팩트체크를 시작합니다. 4개 에이전트가 분석 중..." (슈퍼에이전트는 전달자 역할할)
Progress: 0%

=== 3초 후 (첫 번째 결과) ===
Academic Agent 완료:
- "통계청 KOSIS API 조회 완료"
- "2024년 3분기 기준 0.72명 → LIKELY_TRUE (신뢰도 95%)"
Progress: 20%

=== 5초 후 ===
News Agent 완료:
- "주요 언론 5곳 동일 수치 보도 확인"
- "언론 일치도 높음 → TRUE (신뢰도 90%)"
Progress: 40%

=== 7초 후 ===
Logic Agent 완료:
- "0.7과 0.72는 통계적 오차 범위"
- "논리적 일관성 확인 → TRUE (신뢰도 95%)"
Progress: 60%

=== 10초 후 ===
Social Agent 완료:
- "관련 커뮤니티 토론 분석"
- "사회적 우려 높지만 수치 정확성 인정 → TRUE (신뢰도 75%)"
Progress: 80%

=== 15초 후 (조기 결론) ===
"4개 에이전트 분석 완료. 높은 신뢰도로 결론 도출 가능"
임시 결과: TRUE (종합 신뢰도 88%)

=== 18초 후 (최종 완료) ===
모든 에이전트 완료:

최종 결과: "PARTIALLY_TRUE - 정확히는 0.72명이지만 
0.7명도 허용 가능한 범위 (종합 신뢰도 89%)"
Progress: 100%
```

**사용자가 느끼는 경험:**
- 0초: 즉시 시작 확인
- 3초: 첫 번째 답변 확인  
- 5초: 두 번째 검증
- 15초: 충분히 신뢰할 만한 결론
- 18초: 완전한 분석 완료

## 8. API 비용 및 제약사항 (2025년 7월 기준)

### 8.1 무료 API (우선 구현)
- **네이버 뉴스 API**: 25,000회/일 무료
- **Semantic Scholar API**: 무료 (rate limit 준수)
- **YouTube Data API**: 10,000 units/일 무료
- **Wikipedia API**: 5,000회/시간 무료
- **Guardian API**: 완전 무료


