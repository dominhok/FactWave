import { useState } from 'react'

function Discussion() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasStarted, setHasStarted] = useState(false)
  const [activeAgents, setActiveAgents] = useState([
    { id: 'news', name: 'News', avatar: '📰', active: true },
    { id: 'academia', name: 'Academia', avatar: '🎓', active: true },
    { id: 'logic', name: 'Logic', avatar: '🤔', active: true },
    { id: 'social', name: 'Social', avatar: '👥', active: true },
    { id: 'statistic', name: 'Statistic', avatar: '📊', active: true }
  ])

  // 디버깅용 로그
  console.log('Discussion component loaded', { input, messages, isLoading, hasStarted })

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
    setHasStarted(true)

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

  const toggleAgent = (agentId) => {
    setActiveAgents(prev => prev.map(agent => 
      agent.id === agentId ? { ...agent, active: !agent.active } : agent
    ))
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
    <div className="flex flex-col h-full bg-white">
      {/* Agent Selection */}
      <div className="overflow-x-auto border-b border-gray-200 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        <div className="flex gap-6 p-4 min-w-max">
          {activeAgents.map((agent) => (
            <div 
              key={agent.id} 
              className="relative flex flex-col items-center flex-shrink-0 w-16"
            >
              {/* Agent 이미지 */}
              <div className="relative">
                <img 
                  src={`/public/${agent.id}.png`}
                  alt={agent.name}
                  className={`w-10 h-10 object-cover rounded-full transition-all duration-200 cursor-pointer ${
                    !agent.active ? 'opacity-50' : ''
                  }`}
                  onClick={() => !agent.active && toggleAgent(agent.id)}
                />
                
                {/* X 버튼 - 활성화된 Agent에만 표시 */}
                {agent.active && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleAgent(agent.id)
                    }}
                    className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center text-xs transition-colors z-10 bg-black text-white hover:bg-gray-800"
                  >
                    ×
                  </button>
                )}
              </div>
              
              {/* Agent 제목 */}
              <span className="text-xs font-medium text-gray-700 text-center mt-1">
                {agent.name.toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>

      {!hasStarted ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <h2 className="text-gray-800 mb-4 text-xl font-bold">You're about to use FactWave</h2>
          <p className="text-gray-600 leading-relaxed mb-4 text-xs max-w-md">
            FactWave는 AI 에이전트가 협력하여 정보의 진위를 분석하는 차세대 팩트체킹 플랫폼입니다. 
            뉴스, 학술, 논리, 소셜 미디어 전문 에이전트들이 다각도로 검증하여 신뢰할 수 있는 판단을 제공합니다.
          </p>
          <p className="text-gray-600 leading-relaxed text-xs max-w-md">
            AI 분석 결과는 참고용으로만 사용하세요. 
            중요한 의사결정 전에는 반드시 추가적인 검증과 전문가 자문을 받으시기 바랍니다.
            최종 판단과 그 결과에 대한 책임은 사용자에게 있습니다.
          </p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {messages.map((message) => (
            <div key={message.id} className="mb-6">
              {message.type === 'question' ? (
                <div className="bg-blue-50 p-4 rounded-xl mb-5 text-base leading-relaxed text-blue-800 border-l-4 border-blue-500">
                  {message.content}
                </div>
              ) : (
                                 <div className="bg-white rounded-xl p-5 shadow-lg border border-gray-200">
                   <div className="flex items-center gap-3 mb-3">
                     <span className="text-2xl w-10 h-10 flex items-center justify-center bg-gray-100 rounded-full">
                       {message.avatar}
                     </span>
                     <span className="font-semibold text-base text-gray-800">{message.agentName}</span>
                   </div>
                   <div className="leading-relaxed text-gray-700 mb-4 text-sm">
                     {message.content}
                   </div>
                   <div className="flex justify-between items-center pt-3 border-t border-gray-100 relative">
                     {message.source && message.source.trim() && (
                       <a 
                         href={message.sourceUrl} 
                         target="_blank" 
                         rel="noopener noreferrer"
                         className="text-gray-600 text-sm font-medium hover:underline"
                       >
                         {message.source}
                       </a>
                     )}
                    <div className="flex gap-2">
                      <button 
                        className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
                        onClick={() => copyText(message.content)}
                        title="복사"
                      >
                        📋
                      </button>
                      <button 
                        className="bg-none border-none cursor-pointer p-1.5 rounded-md text-base transition-colors hover:bg-gray-100"
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
            <div className="text-center py-10 text-gray-600 italic">
              분석 중...
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-5 bg-white border-t border-gray-200">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Write any opinion..."
            className="w-full px-4 py-3 pr-16 bg-white border border-gray-300 rounded-full text-base outline-none transition-all duration-200 focus:border-gray-600 shadow-md"
          />
          <button 
            type="submit" 
            className="absolute right-2 top-1/2 transform -translate-y-1/2 w-10 h-10 bg-gray-200 text-gray-800 rounded-full cursor-pointer text-lg flex items-center justify-center transition-colors hover:bg-gray-300 border-none"
          >
            ↑
          </button>
        </div>
      </form>
    </div>
  )
}

export default Discussion
