import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [activeTab, setActiveTab] = useState('토론')
  const [finalResult, setFinalResult] = useState(null)
  const wsRef = useRef(null)
  const sessionIdRef = useRef(null)

  // 에이전트 설정
  const agentConfig = {
    'academic': { name: 'Academia', avatar: '🎓' },
    'news': { name: 'News', avatar: '📰' },
    'statistics': { name: 'Statistics', avatar: '📊' },
    'logic': { name: 'Logic', avatar: '🤔' },
    'social': { name: 'Social', avatar: '👥' },
    'super': { name: 'Super Agent', avatar: '🔮' },
    // 역호환성을 위한 매핑
    'Academic Agent': { name: 'Academia', avatar: '🎓' },
    'News Agent': { name: 'News', avatar: '📰' },
    'Statistics Agent': { name: 'Statistics', avatar: '📊' },
    'Logic Agent': { name: 'Logic', avatar: '🤔' },
    'Social Agent': { name: 'Social', avatar: '👥' },
    'Super Agent': { name: 'Super Agent', avatar: '🔮' }
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

    ws.onerror = (error) => {
      console.error('WebSocket 오류:', error)
      setConnectionStatus('error')
      setIsLoading(false)
    }

    ws.onclose = () => {
      console.log('WebSocket 연결 종료')
      setConnectionStatus('disconnected')
    }

    return ws
  }

  // JSON 응답 파싱 함수
  const parseAgentResponse = (responseText) => {
    try {
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
            verdict: parsedResponse.verdict || parsedResponse.final_verdict,
            keyFindings: parsedResponse.key_findings || [],
            evidenceSources: parsedResponse.evidence_sources || [],
            reasoning: parsedResponse.reasoning || parsedResponse.verdict_reasoning || '',
            agreements: parsedResponse.agreements || [],
            disagreements: parsedResponse.disagreements || [],
            additionalPerspective: parsedResponse.additional_perspective || '',
            timestamp: new Date(data.timestamp || Date.now())
          }
          setMessages(prev => [...prev, taskCompletedMessage])
        }
        break

      case 'final_result':
        // 최종 보고서 JSON 파싱
        const finalResponse = parseAgentResponse(content.summary || content.analysis || '{}')
        
        const finalResultData = {
          verdict: finalResponse?.final_verdict || content.final_verdict || content.verdict,
          summary: finalResponse?.summary || content.summary || '분석 완료',
          reasoning: finalResponse?.verdict_reasoning || finalResponse?.reasoning || '',
          keyAgreements: finalResponse?.key_agreements || [],
          keyDisagreements: finalResponse?.key_disagreements || [],
          agentVerdicts: content.agent_verdicts || {},
          evidenceSummary: content.evidence_summary || [],
          statement: content.statement || ''
        }
        
        setFinalResult(finalResultData)
        setIsLoading(false)
        break

      case 'error':
        const errorMessage = {
          id: `error_${Date.now()}`,
          type: 'error',
          content: content.error || data.message || '오류가 발생했습니다',
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
    setInput('')
    setIsLoading(true)
    setMessages([]) // 새로운 질문 시 이전 메시지 클리어
    setFinalResult(null) // 이전 결과 클리어
    setActiveTab('토론') // 토론 탭으로 전환

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

    const sendFactCheckRequest = () => {
      ws.send(JSON.stringify({
        action: 'start',
        statement: currentQuestion
      }))
    }

    if (ws.readyState === WebSocket.OPEN) {
      sendFactCheckRequest()
    } else {
      const openHandler = () => {
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

  // 탭별 콘텐츠 렌더링
  const renderTabContent = () => {
    if (activeTab === '결과보기' && finalResult) {
      return (
        <div className="final-report">
          {finalResult.statement && (
            <div className="statement">
              <strong>검증 주장:</strong> {finalResult.statement}
            </div>
          )}
          
          <div className="response-header">
            <span className="avatar">📋</span>
            <span className="agent-name">최종 보고서</span>
            {finalResult.verdict && (
              <span className={`verdict verdict-${finalResult.verdict}`}>
                {finalResult.verdict}
              </span>
            )}
          </div>
          
          <div className="response-content">
            {finalResult.summary}
          </div>
          
          {finalResult.keyAgreements.length > 0 && (
            <div className="agreements">
              <strong>주요 합의점:</strong>
              <ul>
                {finalResult.keyAgreements.map((agreement, idx) => (
                  <li key={idx}>{agreement}</li>
                ))}
              </ul>
            </div>
          )}
          
          {finalResult.keyDisagreements.length > 0 && (
            <div className="disagreements">
              <strong>주요 이견:</strong>
              <ul>
                {finalResult.keyDisagreements.map((disagreement, idx) => (
                  <li key={idx}>{disagreement}</li>
                ))}
              </ul>
            </div>
          )}
          
          {Object.keys(finalResult.agentVerdicts).length > 0 && (
            <div className="agent-verdicts">
              <strong>에이전트별 판정:</strong>
              <ul>
                {Object.entries(finalResult.agentVerdicts).map(([agent, data]) => (
                  <li key={agent}>
                    <span className="agent">{agentConfig[agent]?.name || agent}:</span>
                    <span className={`verdict verdict-${data.verdict}`}>
                      {data.verdict}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {finalResult.evidenceSummary.length > 0 && (
            <div className="evidence-summary">
              <strong>주요 근거:</strong>
              <ul>
                {finalResult.evidenceSummary.map((evidence, idx) => (
                  <li key={idx}>{evidence}</li>
                ))}
              </ul>
            </div>
          )}
          
          {finalResult.reasoning && (
            <div className="reasoning">
              <details>
                <summary>상세 판정 근거</summary>
                <div>{finalResult.reasoning}</div>
              </details>
            </div>
          )}
          
          <div className="response-footer">
            <div className="actions">
              <button 
                className="action-btn"
                onClick={() => copyText(finalResult.summary)}
                title="복사"
              >
                📋
              </button>
              <button 
                className="action-btn"
                onClick={() => exportText(finalResult.summary)}
                title="내보내기"
              >
                📤
              </button>
            </div>
          </div>
        </div>
      )
    }
    
    if (activeTab === '라이브러리') {
      return (
        <div style={{padding: '20px', textAlign: 'center', color: '#666'}}>
          라이브러리 기능은 개발 중입니다.
        </div>
      )
    }
    
    // 토론 탭 - 에이전트 분석 과정
    return (
      <>
        {messages.map((message) => {
          if (message.type === 'question') {
            return (
              <div key={message.id} className="user-question">
                {message.content}
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

          // 에이전트 응답
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
                </div>
                
                <div className="response-content">
                  {message.keyFindings && message.keyFindings.length > 0 && (
                    <div className="findings">
                      <strong>핵심 발견사항:</strong>
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
          }

          return null
        })}

        {isLoading && (
          <div className="loading">
            분석 중...
          </div>
        )}
      </>
    )
  }

  return (
    <div className="app">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === '토론' ? 'active' : ''}`}
          onClick={() => setActiveTab('토론')}
        >
          토론
        </button>
        <button 
          className={`tab ${activeTab === '결과보기' ? 'active' : ''}`}
          onClick={() => setActiveTab('결과보기')}
        >
          결과보기
        </button>
        <button 
          className={`tab ${activeTab === '라이브러리' ? 'active' : ''}`}
          onClick={() => setActiveTab('라이브러리')}
        >
          라이브러리
        </button>
      </div>

      <div className="content">
        {renderTabContent()}
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