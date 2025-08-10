import { useState } from 'react'
import './App.css'

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  const dummyResponses = [
    {
      id: 'News Agent',
      name: 'News',
      avatar: '📰',
      response: '2023년 국정감사에서 밝혀진 바에 따르면, 일반인을 대상으로 한 일명 키 크는 약 처럼은 효과가 입증되지 않았다는 답변을 받았습니다. 특히 터너증후군 등 특정 질환 환자에 한정하여 사용되어야 하며, 일반인의 사용은 오남용 사례가 지적되어 있습니다.',
      source: 'mimed.com+1',
      sourceUrl: 'https://mimed.com'
    },
    {
      id: 'Academia Agent',
      name: 'Academia',
      avatar: '🎓',
      response: '의학적 문헌에 따르면, 남성은 18-20세, 여성은 16-18세 시기에 성장판이 닫혀 키 성장이 멈춥니다. 20세 이후에 약물 복용해서 자연스럽게 성장판이 다시 열리는 것은 거의 불가능합니다. 일반인이 복용하는 약으로 키가 클 수 있다는 등등은 크 논문은 존재하지 않으며, 답지 성장호르몬 주사는 다성을 성장호르몬 결핍 환자에게만 적용됩니다.',
      source: '서울대학교병원+2',
      sourceUrl: 'https://snuh.org'
    },
    {
      id: 'Logic Agent',
      name: 'Logic',
      avatar: '🤔',
      response: '논장 차례를 논리적으로 보면 약 의으면 20세 이후에도 키가 6cm까지 갖 수 있다는 주장에는 뜻 때빼, 복용 전진 또는 개별 차이 등의 변수를 견려 고려하지 않은 절대적 표현입니다. 이 약속된 결과가 과학적으로 기능한 설명과 맞지 않으며, 논리적으로 말녀가 맞지 않습니다. 즉, 주장의 전세가 비현실적이고 과도합니다.'
    },
    {
      id: 'Social Agent',
      name: 'Social',
      avatar: '👥',
      response: '소셜미디어 분석 결과, 해당 약물에 대한 온라인 커뮤니티 반응은 대부분 부정적입니다. 실제 복용 후기들에서는 효과를 보지 못했다는 의견이 80% 이상을 차지하며, 일부 사용자들은 부작용을 호소하고 있습니다. 특히 20대 이후 키 성장에 대한 기대감을 이용한 마케팅에 대한 비판적 시각이 많이 관찰됩니다.',
      source: 'reddit.com+3',
      sourceUrl: 'https://reddit.com'
    }
  ]

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

    // 더미 데이터로 웹소켓 응답 시뮬레이션
    setTimeout(() => {
      // 각 에이전트 응답을 개별 메시지로 추가
      const responseMessages = dummyResponses.map((response, index) => ({
        id: Date.now() + index + 1,
        type: 'response',
        agentId: response.id,
        agentName: response.name,
        avatar: response.avatar,
        content: response.response,
        source: response.source,
        sourceUrl: response.sourceUrl,
        timestamp: new Date()
      }))

      setMessages(prev => [...prev, ...responseMessages])
      setIsLoading(false)
    }, 1000)
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
        {messages.map((message) => (
          <div key={message.id}>
            {message.type === 'question' ? (
              <div className="user-question">
                {message.content}
              </div>
            ) : (
              <div className="response-card">
                <div className="response-header">
                  <span className="avatar">{message.avatar}</span>
                  <span className="agent-name">{message.agentName}</span>
                </div>
                <div className="response-content">
                  {message.content}
                </div>
                <div className="response-footer">
                  {message.source && message.source.trim() && (
                    <a 
                      href={message.sourceUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="source-link"
                    >
                      {message.source}
                    </a>
                  )}
                  <div className="actions">
                    <button 
                      className="action-btn"
                      onClick={() => copyText(message.content)}
                      title="복사"
                    >
                      📋
                    </button>
                    <button 
                      className="action-btn"
                      onClick={() => exportText(message.content)}
                      title="내보내기"
                    >
                      📤
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="loading">
            분석 중...
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
