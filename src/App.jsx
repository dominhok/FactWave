import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected') // 'disconnected', 'connecting', 'connected'
  const wsRef = useRef(null)
  const sessionIdRef = useRef(null)

  // 에이전트 설정 (백엔드와 일치하도록 소문자 키 사용)
  const agentConfig = {
    'academic': { name: '학술 연구', avatar: '🎓' },
    'news': { name: '뉴스 검증', avatar: '📰' },
    'statistics': { name: '통계 데이터', avatar: '📊' },
    'logic': { name: '논리 추론', avatar: '🤔' },
    'social': { name: '사회 맥락', avatar: '👥' },
    'super': { name: '총괄 코디네이터', avatar: '🔮' },
    // 역호환성을 위한 매핑
    'Academic Agent': { name: '학술 연구', avatar: '🎓' },
    'News Agent': { name: '뉴스 검증', avatar: '📰' },
    'Statistics Agent': { name: '통계 데이터', avatar: '📊' },
    'Logic Agent': { name: '논리 추론', avatar: '🤔' },
    'Social Agent': { name: '사회 맥락', avatar: '👥' },
    'Super Agent': { name: '총괄 코디네이터', avatar: '🔮' }
  }

  // WebSocket 연결 함수
  const connectWebSocket = (sessionId) => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`)
    wsRef.current = ws
    sessionIdRef.current = sessionId
    setConnectionStatus('connecting')

    ws.onopen = () => {
      console.log('WebSocket 연결 성공')
      setConnectionStatus('connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('메시지 파싱 오류:', error)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket 연결 종료')
      setConnectionStatus('disconnected')
      setIsLoading(false)
    }

    ws.onerror = (error) => {
      console.error('WebSocket 오류:', error)
      setConnectionStatus('disconnected')
      setIsLoading(false)
    }

    return ws
  }

  // JSON 응답 파싱 함수
  const parseAgentResponse = (responseText) => {
    try {
      // JSON 블록 추출
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return null;
    } catch (error) {
      console.error('JSON 파싱 오류:', error);
      return null;
    }
  }

  // WebSocket 메시지 처리
  const handleWebSocketMessage = (data) => {
    console.log('수신된 메시지:', data)
    console.log('메시지 타입:', data.type)
    console.log('콘텐츠:', data.content)

    // content 필드에서 실제 데이터 추출
    const content = data.content || {}
    const agent = data.agent
    const step = data.step

    switch (data.type) {
      case 'connection_established':
        console.log('WebSocket 연결 확인:', content.session_id)
        break

      case 'fact_check_started':
        console.log('팩트체킹 시작:', content.statement)
        break

      case 'agent_start':
        const startMessage = {
          id: `${agent}_start_${Date.now()}`,
          type: 'agent_status',
          agentId: agent,
          agentName: agentConfig[agent]?.name || agent,
          avatar: agentConfig[agent]?.avatar || '🤖',
          content: content.message || `${agent} 분석 시작`,
          task: content.task,
          step: step,
          status: 'thinking',
          timestamp: new Date(data.timestamp || Date.now())
        }
        setMessages(prev => [...prev, startMessage])
        break

      case 'task_completed':
        // JSON 응답 파싱
        const parsedResponse = parseAgentResponse(content.analysis || content.message || '{}')
        
        if (parsedResponse) {
          const taskCompletedMessage = {
            id: `${agent}_task_complete_${Date.now()}`,
            type: 'response',
            agentId: agent,
            agentName: agentConfig[agent]?.name || agent,
            avatar: agentConfig[agent]?.avatar || '🤖',
            step: step,
            status: 'completed',
            timestamp: new Date(data.timestamp || Date.now()),
            
            // JSON 구조화된 데이터
            verdict: parsedResponse.verdict || parsedResponse.final_verdict,
            keyFindings: parsedResponse.key_findings || [],
            evidenceSources: parsedResponse.evidence_sources || [],
            reasoning: parsedResponse.reasoning || parsedResponse.verdict_reasoning || '',
            
            // Step 2 데이터
            agreements: parsedResponse.agreements || [],
            disagreements: parsedResponse.disagreements || [],
            additionalPerspective: parsedResponse.additional_perspective || '',
            
            // Step 3 데이터
            keyAgreements: parsedResponse.key_agreements || [],
            keyDisagreements: parsedResponse.key_disagreements || [],
            summary: parsedResponse.summary || ''
          }
          setMessages(prev => [...prev, taskCompletedMessage])
        } else {
          // 파싱 실패시 기본 메시지
          const fallbackMessage = {
            id: `${agent}_task_complete_${Date.now()}`,
            type: 'response',
            agentId: agent,
            agentName: agentConfig[agent]?.name || agent,
            avatar: agentConfig[agent]?.avatar || '🤖',
            content: content.analysis || content.message || '분석 완료',
            step: step,
            status: 'completed',
            timestamp: new Date(data.timestamp || Date.now())
          }
          setMessages(prev => [...prev, fallbackMessage])
        }
        break

      case 'step_start':
        const stepStartMessage = {
          id: `step_start_${step}_${Date.now()}`,
          type: 'stage_info',
          content: `${content.name}: ${content.description}`,
          stage: step,
          timestamp: new Date(data.timestamp || Date.now())
        }
        setMessages(prev => [...prev, stepStartMessage])
        break

      case 'step_complete':
        const stepCompleteMessage = {
          id: `step_complete_${step}_${Date.now()}`,
          type: 'stage_info',
          content: `${step} 완료`,
          stage: step,
          summary: content.summary,
          timestamp: new Date(data.timestamp || Date.now())
        }
        setMessages(prev => [...prev, stepCompleteMessage])
        break

      case 'final_result':
        // 최종 보고서 JSON 파싱 시도
        const finalResponse = parseAgentResponse(content.summary || content.analysis || '{}')
        
        const finalMessage = {
          id: `final_${Date.now()}`,
          type: 'final_report',
          agentName: '최종 보고서',
          avatar: '📋',
          timestamp: new Date(data.timestamp || Date.now()),
          
          // 구조화된 최종 결과
          verdict: finalResponse?.final_verdict || content.final_verdict || content.verdict,
          summary: finalResponse?.summary || content.summary || '분석 완료',
          reasoning: finalResponse?.verdict_reasoning || finalResponse?.reasoning || '',
          keyAgreements: finalResponse?.key_agreements || [],
          keyDisagreements: finalResponse?.key_disagreements || [],
          
          // 전체 최종 결과 데이터
          agentVerdicts: content.agent_verdicts || {},
          evidenceSummary: content.evidence_summary || [],
          toolUsageStats: content.tool_usage_stats || {},
          statement: content.statement || '',
          confidence: content.confidence || 0.5
        }
        setMessages(prev => [...prev, finalMessage])
        setIsLoading(false)
        break

      case 'error':
        const errorMessage = {
          id: `error_${Date.now()}`,
          type: 'error',
          content: content.error || data.message || '오류가 발생했습니다',
          details: content.details,
          timestamp: new Date(data.timestamp || Date.now())
        }
        setMessages(prev => [...prev, errorMessage])
        setIsLoading(false)
        break

      default:
        console.log('처리되지 않은 메시지 타입:', data.type)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const currentQuestion = input.trim()
    setInput('') // 입력창 즉시 클리어
    setIsLoading(true)

    // 사용자 질문을 메시지에 추가
    const questionMessage = {
      id: Date.now(),
      type: 'question',
      content: currentQuestion,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, questionMessage])

    // WebSocket을 통한 실시간 팩트체킹 요청
    const sessionId = `session_${Date.now()}`
    const ws = connectWebSocket(sessionId)

    // 연결이 열리면 팩트체킹 요청 전송
    const sendFactCheckRequest = () => {
      ws.send(JSON.stringify({
        action: 'start',  // 백엔드가 기대하는 형식
        statement: currentQuestion
      }))
    }

    if (ws.readyState === WebSocket.OPEN) {
      sendFactCheckRequest()
    } else {
      // onopen 이벤트 리스너 추가
      const openHandler = () => {
        // 연결 확립 메시지를 받은 후에 요청 전송
        setTimeout(sendFactCheckRequest, 100)
      }
      ws.addEventListener('open', openHandler)
    }
  }

  const copyText = (text) => {
    navigator.clipboard.writeText(text)
  }

  const exportText = (text) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'factcheck-result.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app">
      <div className="tabs">
        <button className="tab active">토론</button>
        <button className="tab">결과보기</button>
        <button className="tab">라이브러리</button>
      </div>

      <div className="content">
        {messages.map((message) => {
          if (message.type === 'question') {
            return (
              <div key={message.id} className="user-question">
                {message.content}
              </div>
            )
          }

          if (message.type === 'agent_status') {
            return (
              <div key={message.id} className="agent-status">
                <span className="avatar">{message.avatar}</span>
                <span className="status-text">{message.content}</span>
                <span className="thinking-indicator">🤔</span>
              </div>
            )
          }

          if (message.type === 'stage_info') {
            return (
              <div key={message.id} className="stage-info">
                <div className="stage-content">
                  📍 {message.content}
                </div>
              </div>
            )
          }

          if (message.type === 'final_report') {
            return (
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
                  
                  {/* 최종 요약 - JSON 파싱된 내용 우선 표시 */}
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
                  
                  {/* 주요 근거 요약 */}
                  {message.evidenceSummary && message.evidenceSummary.length > 0 && (
                    <div className="evidence-summary">
                      <strong>주요 근거:</strong>
                      <ul>
                        {message.evidenceSummary.map((evidence, index) => (
                          <li key={index}>{evidence}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {message.keyAgreements && message.keyAgreements.length > 0 && (
                    <div className="agreements">
                      <strong>주요 합의점:</strong>
                      <ul>
                        {message.keyAgreements.map((agreement, index) => (
                          <li key={index}>{agreement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {message.keyDisagreements && message.keyDisagreements.length > 0 && (
                    <div className="disagreements">
                      <strong>주요 불일치점:</strong>
                      <ul>
                        {message.keyDisagreements.map((disagreement, index) => (
                          <li key={index}>{disagreement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                <div className="response-footer">
                  <div className="actions">
                    <button 
                      className="action-btn"
                      onClick={() => copyText(message.summary)}
                      title="복사"
                    >
                      📋
                    </button>
                    <button 
                      className="action-btn"
                      onClick={() => exportText(message.summary)}
                      title="내보내기"
                    >
                      📤
                    </button>
                  </div>
                </div>
              </div>
            )
          }

          if (message.type === 'error') {
            return (
              <div key={message.id} className="error-message">
                ⚠️ {message.content}
              </div>
            )
          }

          // 기본 response 타입 (에이전트 분석/토론) - JSON 구조화된 데이터
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
                    <strong>분석 근거:</strong>
                    <p>{message.reasoning}</p>
                  </div>
                )}
                
                {/* Step 2: 토론 */}
                {message.agreements && message.agreements.length > 0 && (
                  <div className="agreements">
                    <strong>동의 사항:</strong>
                    <ul>
                      {message.agreements.map((agreement, index) => (
                        <li key={index}>{agreement}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {message.disagreements && message.disagreements.length > 0 && (
                  <div className="disagreements">
                    <strong>이견/보완점:</strong>
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
                <div className="actions">
                  <button 
                    className="action-btn"
                    onClick={() => copyText(message.reasoning || message.additionalPerspective || '내용')}
                    title="복사"
                  >
                    📋
                  </button>
                  <button 
                    className="action-btn"
                    onClick={() => exportText(message.reasoning || message.additionalPerspective || '내용')}
                    title="내보내기"
                  >
                    📤
                  </button>
                </div>
              </div>
            </div>
          )
        })}

        {isLoading && (
          <div className="loading">
            <div className="loading-spinner">🔄</div>
            <div className="loading-text">
              팩트체킹 진행 중... (연결 상태: {connectionStatus})
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Write any opinion..."
          className="input-field"
        />
        <button type="submit" className="submit-btn">
          ↑
        </button>
      </form>
    </div>
  )
}

export default App
