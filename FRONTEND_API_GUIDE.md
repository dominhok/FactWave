# FactWave Frontend API 가이드

프론트엔드 개발자를 위한 FactWave WebSocket API 핵심 가이드입니다.

## 🚀 빠른 시작

### 1. WebSocket 연결

```javascript
const sessionId = `session_${Date.now()}`;
const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
```

### 2. 팩트체킹 요청

```javascript
ws.send(JSON.stringify({
  action: 'start',
  statement: '검증하고 싶은 문장'
}));
```

## 📨 메시지 타입

### 보내는 메시지 (Client → Server)

```javascript
{
  "action": "start",
  "statement": "임찬규는 두산 베어스 선수야?"
}
```

### 받는 메시지 (Server → Client)

#### 1. 연결 확인
```javascript
{
  "type": "connection_established",
  "content": {
    "session_id": "session_1234567890",
    "message": "WebSocket 연결이 설정되었습니다"
  }
}
```

#### 2. 에이전트 분석 완료 (핵심!)
```javascript
{
  "type": "task_completed",
  "step": "step1",           // step1, step2, step3
  "agent": "academic",       // academic, news, statistics, logic, social
  "content": {
    "analysis": "{\"agent_name\":\"academic\",\"verdict\":\"거짓\",\"key_findings\":[\"발견사항\"],\"evidence_sources\":[\"출처\"],\"reasoning\":\"판정근거\"}"
  }
}
```

#### 3. 최종 결과 (핵심!)
```javascript
{
  "type": "final_result",
  "content": {
    "statement": "검증한 문장",
    "final_verdict": "거짓",
    "summary": "최종 분석 결과",
    "agent_verdicts": {
      "academic": {"verdict": "거짓", "confidence": 0.85},
      "news": {"verdict": "거짓", "confidence": 0.90},
      "social": {"verdict": "참", "confidence": 0.70}
    },
    "evidence_summary": ["주요 근거 1", "주요 근거 2"]
  }
}
```

#### 4. 에러
```javascript
{
  "type": "error",
  "content": {
    "error": "오류 메시지",
    "error_code": "FACT_CHECK_ERROR"
  }
}
```

## 🎯 에이전트 & 판정

### 에이전트 타입
- `academic` - 학술 연구 (🎓)
- `news` - 뉴스 검증 (📰)  
- `statistics` - 통계 데이터 (📊)
- `logic` - 논리 추론 (🤔)
- `social` - 사회 맥락 (👥)

### 판정 결과
- `참` / `대체로_참` / `부분적_참`
- `불확실` / `정보부족` / `논란중`
- `부분적_거짓` / `대체로_거짓` / `거짓`
- `과장됨` / `오해소지` / `시대착오`

## 📝 실제 구현 예시

```javascript
class FactWaveClient {
  constructor() {
    this.ws = null;
    this.sessionId = null;
  }

  connect() {
    this.sessionId = `session_${Date.now()}`;
    this.ws = new WebSocket(`ws://localhost:8000/ws/${this.sessionId}`);
    
    this.ws.onopen = () => {
      console.log('✅ WebSocket 연결됨');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('❌ WebSocket 오류:', error);
    };
    
    this.ws.onclose = () => {
      console.log('🔌 WebSocket 연결 종료');
    };
  }

  handleMessage(data) {
    switch(data.type) {
      case 'connection_established':
        console.log('연결 확인:', data.content.session_id);
        break;
        
      case 'task_completed':
        // 에이전트 분석 완료 - JSON 파싱 필요
        const analysis = this.parseAgentResponse(data.content.analysis);
        this.onAgentResult(data.agent, analysis);
        break;
        
      case 'final_result':
        // 최종 결과
        this.onFinalResult(data.content);
        break;
        
      case 'error':
        console.error('오류:', data.content.error);
        break;
    }
  }

  parseAgentResponse(analysisString) {
    try {
      const jsonMatch = analysisString.match(/\{[\s\S]*\}/);
      return jsonMatch ? JSON.parse(jsonMatch[0]) : null;
    } catch (error) {
      console.error('JSON 파싱 오류:', error);
      return null;
    }
  }

  startFactCheck(statement) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'start',
        statement: statement
      }));
    }
  }

  onAgentResult(agent, analysis) {
    // 에이전트별 결과 처리
    console.log(`${agent} 결과:`, analysis);
  }

  onFinalResult(result) {
    // 최종 결과 처리
    console.log('최종 판정:', result.final_verdict);
    console.log('요약:', result.summary);
  }
}

// 사용법
const client = new FactWaveClient();
client.connect();

// 팩트체킹 시작
client.startFactCheck('임찬규는 두산 베어스 선수야?');
```

## 🎨 UI 표시 팁

### 판정 결과 색상 코딩
```css
.verdict-참 { background: #dcfce7; color: #16a34a; }
.verdict-거짓 { background: #fee2e2; color: #dc2626; }
.verdict-불확실 { background: #f3f4f6; color: #6b7280; }
.verdict-정보부족 { background: #f3f4f6; color: #6b7280; }
```

### 에이전트 아바타
```javascript
const agentConfig = {
  'academic': { name: 'Academia', avatar: '🎓' },
  'news': { name: 'News', avatar: '📰' },
  'statistics': { name: 'Statistics', avatar: '📊' },
  'logic': { name: 'Logic', avatar: '🤔' },
  'social': { name: 'Social', avatar: '👥' }
};
```

### 실시간 업데이트 표시
```javascript
// 분석 중 표시
<div className="loading">분석 중...</div>

// 에이전트별 카드 표시
<div className="response-card">
  <div className="response-header">
    <span className="avatar">{agentConfig[agent].avatar}</span>
    <span className="agent-name">{agentConfig[agent].name}</span>
    <span className={`verdict verdict-${analysis.verdict}`}>
      {analysis.verdict}
    </span>
  </div>
  <div className="response-content">
    <strong>핵심 발견사항:</strong>
    <ul>
      {analysis.key_findings.map(finding => 
        <li key={finding}>{finding}</li>
      )}
    </ul>
  </div>
</div>
```

## ⚠️ 주의사항

1. **JSON 파싱**: `task_completed`의 `analysis` 필드는 문자열로 온 JSON을 파싱해야 함
2. **WebSocket 상태 확인**: 메시지 전송 전에 `readyState === WebSocket.OPEN` 확인
3. **에러 처리**: `error` 타입 메시지에 대한 처리 필수
4. **세션 ID**: 각 팩트체킹 세션마다 고유한 ID 사용

## 🔧 개발 환경

- **Backend 서버**: `cd backend && uv run python -m app.api.server`
- **Frontend 서버**: `cd frontend_minho && npm run dev`
- **Backend Port**: 8000
- **Frontend Port**: 5173