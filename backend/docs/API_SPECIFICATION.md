# FactWave API 명세서

## 개요

FactWave는 AI 기반 다중 에이전트 팩트체킹 시스템으로, WebSocket을 통한 실시간 스트리밍 API를 제공합니다.

## 목차

1. [WebSocket API](#websocket-api)
2. [메시지 타입](#메시지-타입)
3. [LLM 응답 구조](#llm-응답-구조)
4. [에러 처리](#에러-처리)
5. [인증](#인증)

---

## WebSocket API

### 기본 정보

- **Base URL**: `ws://localhost:8000`
- **Protocol**: WebSocket
- **Content-Type**: JSON

### 엔드포인트

#### 팩트체킹 세션

```
WS /ws/{session_id}
```

**Parameters:**
- `session_id` (string): 고유한 세션 식별자

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session_123456789');
```

---

## 메시지 타입

### 1. 연결 확인

서버에서 클라이언트로 전송되는 첫 번째 메시지

```json
{
  "type": "connection_established",
  "content": {
    "session_id": "session_123456789",
    "message": "WebSocket 연결이 설정되었습니다",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. 팩트체킹 시작

```json
{
  "type": "fact_check_started",
  "content": {
    "statement": "검증할 진술",
    "session_id": "session_123456789"
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

### 3. 단계 시작

```json
{
  "type": "step_start",
  "step": "step1",
  "content": {
    "name": "Step 1: 초기 분석",
    "description": "각 전문가가 독립적으로 분석을 시작합니다"
  },
  "timestamp": "2024-01-15T10:30:02Z"
}
```

### 4. 에이전트 시작

```json
{
  "type": "agent_start",
  "step": "step1",
  "agent": "academic",
  "content": {
    "message": "학술 연구 전문가 작업 시작",
    "task_id": "task_abc123",
    "role": "학술 연구 전문가"
  },
  "timestamp": "2024-01-15T10:30:03Z"
}
```

### 5. 태스크 시작

```json
{
  "type": "task_started",
  "step": "step1",
  "agent": "academic",
  "content": {
    "message": "학술 연구 전문가 작업 시작",
    "task_id": "task_abc123",
    "role": "학술 연구 전문가"
  },
  "timestamp": "2024-01-15T10:30:04Z"
}
```

### 6. 태스크 완료

가장 중요한 메시지 타입으로, 각 에이전트의 분석 결과를 포함합니다.

```json
{
  "type": "task_completed",
  "step": "step1",
  "agent": "academic",
  "content": {
    "message": "학술 연구 전문가 작업 완료",
    "analysis": "{\"agent_name\":\"academic\",\"verdict\":\"거짓\",\"key_findings\":[\"발견사항1\",\"발견사항2\"],\"evidence_sources\":[\"출처1\",\"출처2\"],\"reasoning\":\"판정근거\"}",
    "verdict": "거짓",
    "confidence": 0.85,
    "role": "학술 연구 전문가"
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### 7. 단계 완료

```json
{
  "type": "step_complete",
  "step": "step1",
  "content": {
    "summary": "Step 1 완료 - 5명 전문가 분석 완료"
  },
  "timestamp": "2024-01-15T10:40:00Z"
}
```

### 8. 최종 결과

```json
{
  "type": "final_result",
  "content": {
    "statement": "검증한 진술",
    "final_verdict": "거짓",
    "confidence": 0.82,
    "verdict_korean": "거짓",
    "summary": "{\"final_verdict\":\"거짓\",\"summary\":\"종합분석결과\",\"key_agreements\":[\"합의점1\"],\"key_disagreements\":[\"불일치점1\"]}",
    "agent_verdicts": {
      "academic": {"verdict": "거짓", "confidence": 0.85},
      "news": {"verdict": "거짓", "confidence": 0.90},
      "social": {"verdict": "참", "confidence": 0.70},
      "logic": {"verdict": "정보부족", "confidence": 0.50},
      "statistics": {"verdict": "정보부족", "confidence": 0.50}
    },
    "evidence_summary": [
      "주요 근거 1",
      "주요 근거 2"
    ],
    "tool_usage_stats": {},
    "timestamp": "2024-01-15T10:45:00Z"
  },
  "timestamp": "2024-01-15T10:45:00Z"
}
```

### 9. 에러

```json
{
  "type": "error",
  "content": {
    "error": "오류 메시지",
    "details": "상세 오류 정보",
    "error_code": "FACT_CHECK_ERROR"
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

---

## LLM 응답 구조

### Step 1: 초기 분석

각 에이전트의 초기 분석 응답 구조입니다.

```json
{
  "agent_name": "academic",
  "verdict": "참|대체로_참|부분적_참|불확실|정보부족|논란중|부분적_거짓|대체로_거짓|거짓|과장됨|오해소지|시대착오",
  "key_findings": [
    "핵심 발견사항 1",
    "핵심 발견사항 2", 
    "핵심 발견사항 3"
  ],
  "evidence_sources": [
    "출처 1",
    "출처 2",
    "출처 3"
  ],
  "reasoning": "판정 근거 및 상세한 분석 내용"
}
```

### Step 2: 토론

```json
{
  "agent_name": "academic",
  "agreements": [
    "동의하는 점 1",
    "동의하는 점 2"
  ],
  "disagreements": [
    "이견이나 보완점 1", 
    "이견이나 보완점 2"
  ],
  "additional_perspective": "내 전문성으로 추가하는 관점과 새로운 인사이트",
  "final_verdict": "참|대체로_참|부분적_참|불확실|정보부족|논란중|부분적_거짓|대체로_거짓|거짓|과장됨|오해소지|시대착오"
}
```

### Step 3: 최종 종합

```json
{
  "final_verdict": "참|대체로_참|부분적_참|불확실|정보부족|논란중|부분적_거짓|대체로_거짓|거짓|과장됨|오해소지|시대착오",
  "confidence_matrix": {
    "academic": 0.85,
    "news": 0.90,
    "social": 0.70,
    "logic": 0.50,
    "statistics": 0.50
  },
  "weighted_confidence": 0.78,
  "key_agreements": [
    "전문가들이 합의한 주요 사실 1",
    "전문가들이 합의한 주요 사실 2"
  ],
  "key_disagreements": [
    "전문가들 간 의견이 갈린 부분 1",
    "전문가들 간 의견이 갈린 부분 2"
  ],
  "summary": "종합 판정 요약과 핵심 근거",
  "verdict_reasoning": "최종 판정에 대한 상세한 근거"
}
```

---

## 에러 처리

### 에러 코드

| 코드 | 설명 |
|------|------|
| `CONNECTION_ERROR` | WebSocket 연결 오류 |
| `FACT_CHECK_ERROR` | 팩트체킹 프로세스 오류 |
| `AGENT_ERROR` | 에이전트 실행 오류 |
| `LLM_ERROR` | LLM 호출 오류 |
| `TOOL_ERROR` | 도구 실행 오류 |
| `VALIDATION_ERROR` | 입력 데이터 검증 오류 |

### 에러 응답 예시

```json
{
  "type": "error",
  "content": {
    "error": "LLM Provider NOT provided",
    "details": "Pass in the LLM provider you are trying to call. You passed model=solar-pro2",
    "error_code": "LLM_ERROR",
    "timestamp": "2024-01-15T10:30:05Z"
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

---

## 인증

현재 버전에서는 별도의 인증이 필요하지 않습니다. 향후 API 키 기반 인증이 추가될 예정입니다.

---

## 클라이언트 예시

### JavaScript WebSocket 클라이언트

```javascript
class FactWaveClient {
  constructor(sessionId) {
    this.sessionId = sessionId;
    this.ws = null;
    this.messageHandlers = new Map();
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws/${this.sessionId}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket 연결됨');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket 연결 종료');
    };
  }

  handleMessage(data) {
    const handler = this.messageHandlers.get(data.type);
    if (handler) {
      handler(data);
    }
  }

  onMessage(type, handler) {
    this.messageHandlers.set(type, handler);
  }

  startFactCheck(statement) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'start_fact_check',
        statement: statement
      }));
    }
  }
}

// 사용 예시
const client = new FactWaveClient('session_123456789');

client.onMessage('task_completed', (data) => {
  console.log('태스크 완료:', data);
  const analysis = JSON.parse(data.content.analysis);
  console.log('분석 결과:', analysis);
});

client.onMessage('final_result', (data) => {
  console.log('최종 결과:', data);
});

client.connect();
client.startFactCheck('임찬규는 두산 베어스 선수야?');
```

---

## 변경 이력

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0.0 | 2024-01-15 | 초기 API 명세서 작성 |
