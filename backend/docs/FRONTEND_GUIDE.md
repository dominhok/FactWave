# FactWave 프론트엔드 가이드

## 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [Chrome Extension 아키텍처](#chrome-extension-아키텍처)
3. [React 컴포넌트 가이드](#react-컴포넌트-가이드)
4. [WebSocket 통신](#websocket-통신)
5. [상태 관리](#상태-관리)
6. [UI/UX 가이드](#uiux-가이드)
7. [스타일링 시스템](#스타일링-시스템)
8. [성능 최적화](#성능-최적화)
9. [테스팅](#테스팅)
10. [빌드 및 배포](#빌드-및-배포)

---

## 프로젝트 구조

```
src/
├── App.jsx                 # 메인 컴포넌트
├── App.css                 # 글로벌 스타일
├── main.jsx               # React 앱 엔트리 포인트
├── assets/                # 정적 리소스
│   ├── react.svg          # React 로고
│   └── frontend_design/   # 디자인 레퍼런스
├── components/            # 재사용 가능한 컴포넌트 (확장 예정)
├── hooks/                 # 커스텀 훅들 (확장 예정)
├── utils/                 # 유틸리티 함수들 (확장 예정)
└── styles/               # 추가 스타일 파일들 (확장 예정)

public/
├── manifest.json          # Chrome Extension 매니페스트
├── background.js          # 백그라운드 스크립트
├── icon.png              # 익스텐션 아이콘
├── index.html            # HTML 템플릿
└── vite.svg              # Vite 로고

package.json               # 프로젝트 설정 및 의존성
vite.config.js            # Vite 빌드 설정
```

---

## Chrome Extension 아키텍처

### 매니페스트 파일 (manifest.json)

```json
{
  "manifest_version": 3,
  "name": "FactWave",
  "version": "1.0.0",
  "description": "AI 기반 실시간 팩트체킹 도구",
  "permissions": [
    "activeTab",
    "storage"
  ],
  "host_permissions": [
    "http://localhost:8000/*"
  ],
  "action": {
    "default_popup": "index.html",
    "default_title": "FactWave 팩트체커",
    "default_icon": {
      "16": "icon.png",
      "32": "icon.png",
      "48": "icon.png",
      "128": "icon.png"
    }
  },
  "background": {
    "service_worker": "background.js"
  },
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'"
  }
}
```

### 백그라운드 스크립트 (background.js)

```javascript
// Chrome Extension 백그라운드 스크립트
chrome.runtime.onInstalled.addListener(() => {
  console.log('FactWave Extension 설치됨');
});

// 탭 정보 가져오기
chrome.action.onClicked.addListener((tab) => {
  chrome.action.openPopup();
});

// 메시지 처리
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_TAB_INFO') {
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      sendResponse({
        url: tabs[0].url,
        title: tabs[0].title
      });
    });
    return true; // 비동기 응답
  }
});
```

### 팝업 크기 및 제약사항

```css
/* Chrome Extension 팝업 크기 제약 */
html, body, #root {
  width: 450px;
  height: 600px;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

/* 스크롤 가능한 컨텐츠 영역 */
.content {
  height: calc(100vh - 120px); /* 헤더/푸터 제외 */
  overflow-y: auto;
  overflow-x: hidden;
}
```

---

## React 컴포넌트 가이드

### 메인 App 컴포넌트

```javascript
// src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

const App = () => {
  // 상태 관리
  const [ws, setWs] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputText, setInputText] = useState('');
  const [currentTab, setCurrentTab] = useState('토론');

  // WebSocket 연결
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const connectWebSocket = useCallback(() => {
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
    
    websocket.onerror = (error) => {
      console.error('WebSocket 오류:', error);
    };
  }, []);

  // 메시지 처리 로직
  const handleWebSocketMessage = useCallback((data) => {
    // 메시지 처리 로직 (이전에 정의한 로직)
  }, []);

  // 팩트체킹 시작
  const startFactCheck = useCallback(() => {
    if (!inputText.trim()) return;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      alert('서버에 연결되지 않았습니다. 잠시 후 다시 시도해주세요.');
      return;
    }

    setIsLoading(true);
    setMessages([]);
    
    // 사용자 질문 추가
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'question',
      content: inputText,
      timestamp: new Date()
    };
    setMessages([userMessage]);

    // WebSocket으로 요청 전송
    ws.send(JSON.stringify({
      action: 'start_fact_check',
      statement: inputText
    }));
  }, [inputText, ws]);

  return (
    <div className="factwave-app">
      {/* 헤더 */}
      <header className="header">
        <h1>🌊 FactWave</h1>
        <p>AI 기반 실시간 팩트체킹</p>
      </header>

      {/* 입력 영역 */}
      <div className="input-section">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="팩트체킹할 내용을 입력하세요..."
          disabled={isLoading}
        />
        <button 
          onClick={startFactCheck}
          disabled={isLoading || !inputText.trim()}
          className="check-button"
        >
          {isLoading ? '분석 중...' : '팩트체크 시작'}
        </button>
      </div>

      {/* 탭 네비게이션 */}
      <div className="tab-navigation">
        {['토론', '결과보기', '라이브러리'].map(tab => (
          <button
            key={tab}
            className={`tab ${currentTab === tab ? 'active' : ''}`}
            onClick={() => setCurrentTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 컨텐츠 영역 */}
      <div className="content">
        {currentTab === '토론' && (
          <div className="discussion-view">
            {isLoading && (
              <div className="loading">
                <div className="loading-spinner">🔄</div>
                <p>AI 전문가들이 분석 중입니다...</p>
              </div>
            )}
            
            {messages.map(message => renderMessage(message))}
          </div>
        )}
        
        {currentTab === '결과보기' && (
          <div className="results-view">
            {/* 결과 요약 뷰 */}
          </div>
        )}
        
        {currentTab === '라이브러리' && (
          <div className="library-view">
            {/* 이전 분석 기록들 */}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
```

### 메시지 렌더링 컴포넌트

```javascript
// 메시지 렌더링 함수들을 별도 컴포넌트로 분리 가능
const MessageRenderer = {
  // 사용자 질문
  question: (message) => (
    <div key={message.id} className="user-question">
      <div className="question-header">
        <span className="icon">❓</span>
        <span className="label">검증 대상</span>
      </div>
      <div className="question-content">{message.content}</div>
    </div>
  ),

  // 에이전트 상태
  agent_status: (message) => (
    <div key={message.id} className="agent-status">
      <span className="avatar">{message.avatar}</span>
      <span className="status-text">{message.content}</span>
      <span className="thinking-indicator">🤔</span>
    </div>
  ),

  // 단계 정보
  stage_info: (message) => (
    <div key={message.id} className="stage-info">
      <div className="stage-content">
        📍 {message.content}
      </div>
    </div>
  ),

  // 에이전트 응답
  response: (message) => (
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
        {/* Step 1: 초기 분석 */}
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
        
        {message.reasoning && (
          <div className="reasoning">
            <strong>판정 근거:</strong>
            <p>{message.reasoning}</p>
          </div>
        )}

        {/* Step 2: 토론 */}
        {message.agreements && message.agreements.length > 0 && (
          <div className="agreements">
            <strong>동의점:</strong>
            <ul>
              {message.agreements.map((agreement, index) => (
                <li key={index}>{agreement}</li>
              ))}
            </ul>
          </div>
        )}
        
        {message.disagreements && message.disagreements.length > 0 && (
          <div className="disagreements">
            <strong>이견:</strong>
            <ul>
              {message.disagreements.map((disagreement, index) => (
                <li key={index}>{disagreement}</li>
              ))}
            </ul>
          </div>
        )}
        
        {message.additionalPerspective && (
          <div className="additional-perspective">
            <strong>추가 관점:</strong>
            <p>{message.additionalPerspective}</p>
          </div>
        )}
      </div>
      
      <div className="response-footer">
        <div className="timestamp">
          {message.timestamp.toLocaleTimeString()}
        </div>
        <div className="actions">
          <button 
            className="action-btn"
            onClick={() => copyText(message.reasoning || message.content)}
            title="복사"
          >
            📋
          </button>
        </div>
      </div>
    </div>
  ),

  // 최종 보고서
  final_report: (message) => (
    <div key={message.id} className="final-report">
      <div className="response-header">
        <span className="avatar">{message.avatar}</span>
        <span className="agent-name">{message.agentName}</span>
        {message.verdict && (
          <span className={`verdict verdict-${message.verdict}`}>
            {message.verdict}
          </span>
        )}
        {message.confidence && (
          <span className="confidence">
            신뢰도: {Math.round(message.confidence * 100)}%
          </span>
        )}
      </div>
      
      <div className="response-content">
        {/* 분석 대상 */}
        {message.statement && (
          <div className="statement">
            <strong>분석 대상:</strong>
            <p>{message.statement}</p>
          </div>
        )}
        
        {/* 최종 요약 */}
        <div className="summary">
          <strong>최종 종합:</strong>
          {message.reasoning ? (
            <p>{message.reasoning}</p>
          ) : (
            <p>{message.summary}</p>
          )}
        </div>
        
        {/* 에이전트별 판정 요약 */}
        {message.agentVerdicts && Object.keys(message.agentVerdicts).length > 0 && (
          <div className="agent-verdicts">
            <strong>에이전트별 판정:</strong>
            <ul>
              {Object.entries(message.agentVerdicts).map(([agent, data]) => (
                <li key={agent}>
                  <span className="agent">{agent}:</span>
                  <span className={`verdict verdict-${data.verdict}`}>{data.verdict}</span>
                  {data.confidence && (
                    <span className="confidence">({Math.round(data.confidence * 100)}%)</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  ),

  // 에러 메시지
  error: (message) => (
    <div key={message.id} className="error-message">
      <span className="error-icon">⚠️</span>
      <span className="error-text">{message.content}</span>
      {message.details && (
        <div className="error-details">{message.details}</div>
      )}
    </div>
  )
};

// 메시지 렌더링 메인 함수
const renderMessage = (message) => {
  const renderer = MessageRenderer[message.type];
  return renderer ? renderer(message) : null;
};
```

---

## WebSocket 통신

### WebSocket 커스텀 훅

```javascript
// src/hooks/useWebSocket.js
import { useState, useEffect, useCallback, useRef } from 'react';

export const useWebSocket = (url) => {
  const [ws, setWs] = useState(null);
  const [connectionState, setConnectionState] = useState('CONNECTING');
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const websocket = new WebSocket(url);
      wsRef.current = websocket;
      
      websocket.onopen = () => {
        console.log('WebSocket 연결됨');
        setConnectionState('OPEN');
        setWs(websocket);
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      };
      
      websocket.onclose = (event) => {
        console.log('WebSocket 연결 종료:', event.code, event.reason);
        setConnectionState('CLOSED');
        setWs(null);
        
        // 재연결 로직 (선택사항)
        if (event.code !== 1000) { // 정상 종료가 아닌 경우
          setTimeout(() => {
            console.log('WebSocket 재연결 시도...');
            connect();
          }, 3000);
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket 오류:', error);
        setConnectionState('ERROR');
      };
      
    } catch (error) {
      console.error('WebSocket 연결 실패:', error);
      setConnectionState('ERROR');
    }
  }, [url]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
    }
  }, []);

  const sendMessage = useCallback((message) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
      return true;
    }
    console.warn('WebSocket이 연결되지 않음');
    return false;
  }, [ws]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ws,
    connectionState,
    lastMessage,
    sendMessage,
    connect,
    disconnect,
    isConnected: connectionState === 'OPEN'
  };
};
```

### WebSocket 상태 관리

```javascript
// src/hooks/useFactCheckSession.js
import { useState, useCallback, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';

export const useFactCheckSession = () => {
  const sessionId = `session_${Date.now()}`;
  const { ws, connectionState, lastMessage, sendMessage, isConnected } = useWebSocket(
    `ws://localhost:8000/ws/${sessionId}`
  );
  
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);

  // 메시지 처리
  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage);
    }
  }, [lastMessage]);

  const handleWebSocketMessage = useCallback((data) => {
    console.log('수신된 메시지:', data);
    
    switch (data.type) {
      case 'fact_check_started':
        setIsLoading(true);
        setCurrentStep('step1');
        break;
        
      case 'step_start':
        setCurrentStep(data.step);
        break;
        
      case 'task_completed':
        // 메시지 처리 로직
        const parsedResponse = parseAgentResponse(data.content?.analysis || '{}');
        if (parsedResponse) {
          const message = createAgentMessage(data, parsedResponse);
          setMessages(prev => [...prev, message]);
        }
        break;
        
      case 'final_result':
        setIsLoading(false);
        setCurrentStep('completed');
        const finalMessage = createFinalMessage(data);
        setMessages(prev => [...prev, finalMessage]);
        break;
        
      case 'error':
        setIsLoading(false);
        const errorMessage = createErrorMessage(data);
        setMessages(prev => [...prev, errorMessage]);
        break;
    }
  }, []);

  const startFactCheck = useCallback((statement) => {
    if (!isConnected) {
      throw new Error('서버에 연결되지 않았습니다');
    }
    
    setMessages([]);
    setIsLoading(true);
    
    // 사용자 질문 추가
    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'question',
      content: statement,
      timestamp: new Date()
    };
    setMessages([userMessage]);
    
    // 팩트체킹 요청
    sendMessage({
      action: 'start_fact_check',
      statement: statement
    });
  }, [isConnected, sendMessage]);

  return {
    messages,
    isLoading,
    currentStep,
    connectionState,
    isConnected,
    startFactCheck,
    sessionId
  };
};
```

---

## 상태 관리

### Context API 사용

```javascript
// src/contexts/FactCheckContext.js
import React, { createContext, useContext, useReducer } from 'react';

const FactCheckContext = createContext();

// 액션 타입
const actionTypes = {
  SET_LOADING: 'SET_LOADING',
  ADD_MESSAGE: 'ADD_MESSAGE',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES',
  SET_CONNECTION_STATE: 'SET_CONNECTION_STATE',
  SET_CURRENT_STEP: 'SET_CURRENT_STEP'
};

// 초기 상태
const initialState = {
  messages: [],
  isLoading: false,
  connectionState: 'DISCONNECTED',
  currentStep: null,
  sessionId: null
};

// 리듀서
const factCheckReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload };
      
    case actionTypes.ADD_MESSAGE:
      return { 
        ...state, 
        messages: [...state.messages, action.payload] 
      };
      
    case actionTypes.CLEAR_MESSAGES:
      return { ...state, messages: [] };
      
    case actionTypes.SET_CONNECTION_STATE:
      return { ...state, connectionState: action.payload };
      
    case actionTypes.SET_CURRENT_STEP:
      return { ...state, currentStep: action.payload };
      
    default:
      return state;
  }
};

// 프로바이더 컴포넌트
export const FactCheckProvider = ({ children }) => {
  const [state, dispatch] = useReducer(factCheckReducer, initialState);

  const actions = {
    setLoading: (loading) => 
      dispatch({ type: actionTypes.SET_LOADING, payload: loading }),
      
    addMessage: (message) => 
      dispatch({ type: actionTypes.ADD_MESSAGE, payload: message }),
      
    clearMessages: () => 
      dispatch({ type: actionTypes.CLEAR_MESSAGES }),
      
    setConnectionState: (state) => 
      dispatch({ type: actionTypes.SET_CONNECTION_STATE, payload: state }),
      
    setCurrentStep: (step) => 
      dispatch({ type: actionTypes.SET_CURRENT_STEP, payload: step })
  };

  return (
    <FactCheckContext.Provider value={{ state, actions }}>
      {children}
    </FactCheckContext.Provider>
  );
};

// 커스텀 훅
export const useFactCheck = () => {
  const context = useContext(FactCheckContext);
  if (!context) {
    throw new Error('useFactCheck must be used within a FactCheckProvider');
  }
  return context;
};
```

---

## UI/UX 가이드

### 디자인 시스템

```css
/* src/styles/design-system.css */
:root {
  /* 색상 팔레트 */
  --primary-blue: #3b82f6;
  --secondary-green: #10b981;
  --warning-orange: #f59e0b;
  --danger-red: #ef4444;
  --neutral-gray: #6b7280;
  
  /* 판정 결과 색상 */
  --verdict-true: #16a34a;
  --verdict-mostly-true: #059669;
  --verdict-partially-true: #d97706;
  --verdict-uncertain: #6b7280;
  --verdict-false: #dc2626;
  
  /* 간격 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 타이포그래피 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  
  /* 그림자 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  
  /* 둥근 모서리 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

### 컴포넌트 스타일 가이드

```css
/* 버튼 스타일 */
.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-primary:disabled {
  background: var(--neutral-gray);
  cursor: not-allowed;
}

/* 카드 스타일 */
.card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-lg);
  margin: var(--spacing-md) 0;
}

/* 입력 필드 */
.input {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid #d1d5db;
  border-radius: var(--radius-md);
  font-size: var(--font-size-md);
  font-family: var(--font-family);
}

.input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 텍스트 영역 */
.textarea {
  min-height: 100px;
  resize: vertical;
}
```

### 애니메이션

```css
/* 로딩 애니메이션 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner {
  animation: spin 2s linear infinite;
  font-size: 24px;
}

/* 페이드 인 애니메이션 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* 메시지 슬라이드 인 */
.message-enter {
  opacity: 0;
  transform: translateX(-20px);
}

.message-enter-active {
  opacity: 1;
  transform: translateX(0);
  transition: all 0.3s ease;
}
```

### 반응형 디자인

```css
/* Chrome Extension 팝업은 고정 크기이지만, 웹 버전을 위한 반응형 */
@media (max-width: 480px) {
  .factwave-app {
    padding: var(--spacing-sm);
  }
  
  .response-card {
    padding: var(--spacing-md);
  }
  
  .input-section textarea {
    min-height: 80px;
  }
}

@media (max-width: 350px) {
  .tab-navigation {
    flex-direction: column;
  }
  
  .tab {
    width: 100%;
    margin-bottom: var(--spacing-xs);
  }
}
```

---

## 스타일링 시스템

### CSS 모듈 구조

```css
/* src/styles/components/ResponseCard.module.css */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin: 16px 0;
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
}

.header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.avatar {
  font-size: 24px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.agentName {
  font-weight: 600;
  color: #1f2937;
  font-size: 16px;
}

.verdict {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold;
  margin-left: auto;
}

/* 판정별 색상 */
.verdictTrue { background: #dcfce7; color: #16a34a; }
.verdictMostlyTrue { background: #ecfdf5; color: #059669; }
.verdictPartiallyTrue { background: #fef3c7; color: #d97706; }
.verdictUncertain { background: #f3f4f6; color: #6b7280; }
.verdictFalse { background: #fee2e2; color: #dc2626; }
```

### Styled Components (선택사항)

```javascript
// src/components/StyledComponents.js
import styled from 'styled-components';

export const Card = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  margin: 16px 0;
  overflow: hidden;
  animation: fadeIn 0.3s ease-out;
`;

export const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
`;

export const Verdict = styled.span`
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: bold;
  margin-left: auto;
  
  ${props => props.type === '참' && `
    background: #dcfce7;
    color: #16a34a;
  `}
  
  ${props => props.type === '거짓' && `
    background: #fee2e2;
    color: #dc2626;
  `}
`;
```

---

## 성능 최적화

### React 최적화

```javascript
// 메모이제이션
import React, { memo, useMemo, useCallback } from 'react';

const MessageCard = memo(({ message }) => {
  const memoizedContent = useMemo(() => {
    return renderMessageContent(message);
  }, [message.id, message.content]);

  return (
    <div className="message-card">
      {memoizedContent}
    </div>
  );
});

// 가상화된 메시지 리스트 (많은 메시지 처리)
import { FixedSizeList as List } from 'react-window';

const VirtualizedMessageList = ({ messages, height = 400 }) => {
  const Row = useCallback(({ index, style }) => (
    <div style={style}>
      <MessageCard message={messages[index]} />
    </div>
  ), [messages]);

  return (
    <List
      height={height}
      itemCount={messages.length}
      itemSize={120}
      overscanCount={5}
    >
      {Row}
    </List>
  );
};
```

### WebSocket 최적화

```javascript
// 메시지 큐를 이용한 배치 처리
class MessageQueue {
  constructor(flushInterval = 100) {
    this.queue = [];
    this.flushInterval = flushInterval;
    this.timeoutId = null;
  }

  add(message) {
    this.queue.push(message);
    this.scheduleFlush();
  }

  scheduleFlush() {
    if (this.timeoutId) return;
    
    this.timeoutId = setTimeout(() => {
      this.flush();
    }, this.flushInterval);
  }

  flush() {
    if (this.queue.length === 0) return;
    
    const messages = [...this.queue];
    this.queue = [];
    this.timeoutId = null;
    
    // 배치로 메시지 처리
    this.onFlush?.(messages);
  }
}

// 사용 예시
const messageQueue = new MessageQueue(100);
messageQueue.onFlush = (messages) => {
  setMessages(prev => [...prev, ...messages]);
};
```

### 이미지 및 리소스 최적화

```javascript
// 지연 로딩
const LazyImage = ({ src, alt, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={imgRef} {...props}>
      {isInView && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setIsLoaded(true)}
          style={{ opacity: isLoaded ? 1 : 0 }}
        />
      )}
    </div>
  );
};
```

---

## 테스팅

### Jest 단위 테스트

```javascript
// src/__tests__/utils.test.js
import { parseAgentResponse } from '../utils/messageParser';

describe('parseAgentResponse', () => {
  test('should parse valid JSON response', () => {
    const jsonResponse = `{
      "agent_name": "academic",
      "verdict": "참",
      "key_findings": ["finding1", "finding2"],
      "evidence_sources": ["source1", "source2"],
      "reasoning": "test reasoning"
    }`;
    
    const result = parseAgentResponse(jsonResponse);
    
    expect(result).toEqual({
      agent_name: "academic",
      verdict: "참",
      key_findings: ["finding1", "finding2"],
      evidence_sources: ["source1", "source2"],
      reasoning: "test reasoning"
    });
  });

  test('should extract JSON from mixed content', () => {
    const mixedContent = `
      Some text before
      {
        "agent_name": "news",
        "verdict": "거짓"
      }
      Some text after
    `;
    
    const result = parseAgentResponse(mixedContent);
    
    expect(result.agent_name).toBe("news");
    expect(result.verdict).toBe("거짓");
  });

  test('should return null for invalid JSON', () => {
    const invalidJson = "This is not JSON";
    
    const result = parseAgentResponse(invalidJson);
    
    expect(result).toBeNull();
  });
});
```

### React Testing Library

```javascript
// src/__tests__/App.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// WebSocket 모킹
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  close: jest.fn(),
  readyState: 1,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
}));

describe('App Component', () => {
  test('renders FactWave title', () => {
    render(<App />);
    expect(screen.getByText('🌊 FactWave')).toBeInTheDocument();
  });

  test('enables fact check button when text is entered', () => {
    render(<App />);
    
    const textarea = screen.getByPlaceholderText('팩트체킹할 내용을 입력하세요...');
    const button = screen.getByText('팩트체크 시작');
    
    expect(button).toBeDisabled();
    
    fireEvent.change(textarea, {
      target: { value: '테스트 문장' }
    });
    
    expect(button).not.toBeDisabled();
  });

  test('shows loading state when fact check starts', async () => {
    render(<App />);
    
    const textarea = screen.getByPlaceholderText('팩트체킹할 내용을 입력하세요...');
    const button = screen.getByText('팩트체크 시작');
    
    fireEvent.change(textarea, {
      target: { value: '테스트 문장' }
    });
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('분석 중...')).toBeInTheDocument();
    });
  });
});
```

### E2E 테스트 (Cypress)

```javascript
// cypress/integration/factcheck.spec.js
describe('FactWave E2E Tests', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('should complete a fact check session', () => {
    // 입력 영역에 텍스트 입력
    cy.get('textarea[placeholder*="팩트체킹할 내용을 입력하세요"]')
      .type('임찬규는 두산 베어스 선수야?');
    
    // 팩트체크 시작
    cy.get('button').contains('팩트체크 시작').click();
    
    // 로딩 상태 확인
    cy.get('.loading').should('be.visible');
    cy.get('button').contains('분석 중...').should('be.disabled');
    
    // 에이전트 응답 대기 (최대 30초)
    cy.get('.response-card', { timeout: 30000 })
      .should('have.length.at.least', 1);
    
    // 최종 결과 확인
    cy.get('.final-report', { timeout: 60000 })
      .should('be.visible');
    
    // 판정 결과 확인
    cy.get('.verdict').should('exist');
  });

  it('should handle WebSocket connection errors', () => {
    // 서버 중단 시뮬레이션
    cy.window().then((win) => {
      // WebSocket 연결 차단
      win.WebSocket = function() {
        throw new Error('Connection failed');
      };
    });
    
    cy.reload();
    
    // 연결 오류 메시지 확인
    cy.get('.error-message')
      .should('contain', '서버에 연결되지 않았습니다');
  });
});
```

---

## 빌드 및 배포

### Vite 빌드 설정

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        background: resolve(__dirname, 'public/background.js')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          return chunkInfo.name === 'background' 
            ? 'background.js' 
            : 'assets/[name]-[hash].js';
        }
      }
    },
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: process.env.NODE_ENV === 'development'
  },
  server: {
    port: 5173,
    host: true
  },
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
  }
});
```

### Chrome Extension 빌드 스크립트

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "build:extension": "npm run build && npm run copy-manifest",
    "copy-manifest": "cp public/manifest.json dist/ && cp public/icon.png dist/",
    "preview": "vite preview",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open"
  }
}
```

### 배포 자동화

```bash
#!/bin/bash
# scripts/build-extension.sh

echo "🚀 FactWave Chrome Extension 빌드 시작..."

# 의존성 설치
npm ci

# 테스트 실행
npm run test

if [ $? -ne 0 ]; then
  echo "❌ 테스트 실패"
  exit 1
fi

# 빌드
npm run build:extension

# 확장 프로그램 패키징
cd dist
zip -r ../factwave-extension.zip ./*
cd ..

echo "✅ 빌드 완료: factwave-extension.zip"
echo "📦 Chrome 웹 스토어에 업로드할 준비가 되었습니다."
```

### 환경별 설정

```javascript
// src/config/environment.js
const config = {
  development: {
    API_BASE_URL: 'ws://localhost:8000',
    DEBUG_MODE: true,
    RECONNECT_ATTEMPTS: 5
  },
  production: {
    API_BASE_URL: 'wss://api.factwave.ai',
    DEBUG_MODE: false,
    RECONNECT_ATTEMPTS: 3
  },
  test: {
    API_BASE_URL: 'ws://localhost:8001',
    DEBUG_MODE: true,
    RECONNECT_ATTEMPTS: 1
  }
};

export default config[process.env.NODE_ENV || 'development'];
```

---

## 디버깅 및 트러블슈팅

### Chrome DevTools 활용

```javascript
// 디버깅 유틸리티
window.FactWaveDebug = {
  // WebSocket 상태 확인
  checkWebSocket: () => {
    console.log('WebSocket State:', window.wsConnection?.readyState);
  },
  
  // 메시지 히스토리
  getMessageHistory: () => {
    return window.messageHistory || [];
  },
  
  // 성능 모니터링
  startPerformanceMonitoring: () => {
    performance.mark('factcheck-start');
  },
  
  endPerformanceMonitoring: () => {
    performance.mark('factcheck-end');
    performance.measure('factcheck-duration', 'factcheck-start', 'factcheck-end');
    console.log('FactCheck Duration:', 
      performance.getEntriesByName('factcheck-duration')[0].duration + 'ms'
    );
  }
};
```

### 일반적인 문제 해결

#### 1. WebSocket 연결 실패

```javascript
// 연결 진단 함수
const diagnoseConnection = async () => {
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      console.log('✅ 서버가 실행 중입니다');
    } else {
      console.log('❌ 서버가 응답하지 않습니다');
    }
  } catch (error) {
    console.log('❌ 서버에 연결할 수 없습니다:', error.message);
  }
};
```

#### 2. JSON 파싱 오류

```javascript
// 강화된 JSON 파싱
const safeParseJSON = (text) => {
  try {
    // 1. 직접 파싱 시도
    return JSON.parse(text);
  } catch (e1) {
    try {
      // 2. JSON 블록 추출 시도
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (e2) {
      // 3. 정규표현식으로 키-값 쌍 추출
      const keyValuePairs = text.match(/"(\w+)":\s*"([^"]+)"/g);
      if (keyValuePairs) {
        const obj = {};
        keyValuePairs.forEach(pair => {
          const [key, value] = pair.match(/"(\w+)":\s*"([^"]+)"/);
          obj[key] = value;
        });
        return obj;
      }
    }
  }
  return null;
};
```

#### 3. Chrome Extension 권한 문제

```javascript
// 권한 확인
const checkPermissions = () => {
  chrome.permissions.contains({
    origins: ['http://localhost:8000/*']
  }, (result) => {
    if (result) {
      console.log('✅ 필요한 권한이 있습니다');
    } else {
      console.log('❌ 권한이 필요합니다');
      // 권한 요청
      chrome.permissions.request({
        origins: ['http://localhost:8000/*']
      });
    }
  });
};
```

---

이제 FactWave 프론트엔드의 모든 주요 측면을 다룬 종합적인 개발 가이드가 완성되었습니다! 이 가이드를 통해 개발자들이 프론트엔드를 쉽게 이해하고 확장할 수 있을 것입니다.