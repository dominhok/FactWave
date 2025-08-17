import { useState } from 'react'
import Discussion from './components/Discussion'
import Results from './components/Results'
import Library from './components/Library'

function App() {
  const [activeTab, setActiveTab] = useState('discussion')
  const [loadedContext, setLoadedContext] = useState(null)
  const [savedResults, setSavedResults] = useState([])
  const [savedConversations, setSavedConversations] = useState([])

  // 디버깅용 로그
  console.log('Factwave App loaded', { activeTab, loadedContext })

  const handleLoadContext = (context) => {
    console.log('컨텍스트 로드:', context)
    setLoadedContext(context)
    setActiveTab('discussion')
  }

  const handleClearContext = () => {
    console.log('컨텍스트 클리어')
    setLoadedContext(null)
  }

  const handleSaveResult = (result) => {
    console.log('App에서 결과 저장:', result)
    setSavedResults(prev => {
      // 같은 질문에 대한 기존 결과 찾기
      const existingIndex = prev.findIndex(r => r.question === result.question);
      
      if (existingIndex !== -1) {
        // 이미 같은 질문이 있으면
        const existing = prev[existingIndex];
        
        // 새 결과의 종합 판단이 더 길거나 더 많은 정보를 가지고 있으면 교체
        const existingLength = (existing.verdictReasoning?.length || 0) + 
                              (existing.summary?.length || 0);
        const newLength = (result.verdictReasoning?.length || 0) + 
                         (result.summary?.length || 0);
        
        if (newLength > existingLength) {
          console.log('기존 결과를 더 상세한 결과로 교체:', result.question);
          const updated = [...prev];
          updated[existingIndex] = result;
          return updated;
        } else {
          console.log('기존 결과 유지 (더 상세함):', result.question);
          return prev;
        }
      }
      
      // 새로운 질문인 경우 추가
      return [result, ...prev];
    })
  }

  const handleSaveConversation = (conversation) => {
    console.log('App에서 대화 저장:', conversation)
    setSavedConversations(prev => {
      // 중복 체크 (같은 질문과 시간으로 판단)
      const isDuplicate = prev.some(c => 
        c.question === conversation.question && 
        Math.abs(c.id - conversation.id) < 1000 // 1초 이내 같은 대화는 중복으로 간주
      )
      if (isDuplicate) {
        console.log('중복 대화 저장 방지:', conversation.question)
        return prev
      }
      return [conversation, ...prev] // 최신 대화를 맨 앞에 추가
    })
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'discussion':
        return <Discussion context={loadedContext} onSaveResult={handleSaveResult} onSaveConversation={handleSaveConversation} onClearContext={handleClearContext} />
      case 'results':
        return <Results context={loadedContext} savedResults={savedResults} />
      case 'library':
        return <Library onLoadContext={handleLoadContext} savedConversations={savedConversations} />
      default:
        return <Discussion context={loadedContext} onSaveResult={handleSaveResult} onSaveConversation={handleSaveConversation} onClearContext={handleClearContext} />
    }
  }

  return (
    <div className="w-full p-0 h-screen flex flex-col bg-white">
      <div className="flex justify-center bg-white px-5 py-4">
        <div className="flex bg-gray-100 rounded-lg p-1" style={{ width: '360px' }}>
          <button 
            className={`flex-1 py-2 text-sm transition-colors duration-200 border-none rounded-md ${
              activeTab === 'discussion' 
                ? 'text-gray-900 font-bold bg-white shadow-sm' 
                : 'text-gray-500 hover:text-gray-700 bg-transparent'
            }`}
            onClick={() => setActiveTab('discussion')}
          >
            토론
          </button>
          <button 
            className={`flex-1 py-2 text-sm transition-colors duration-200 border-none rounded-md ${
              activeTab === 'results' 
                ? 'text-gray-900 font-bold bg-white shadow-sm' 
                : 'text-gray-500 hover:text-gray-700 bg-transparent'
            }`}
            onClick={() => setActiveTab('results')}
          >
            결과보기
          </button>
          <button 
            className={`flex-1 py-2 text-sm transition-colors duration-200 border-none rounded-md ${
              activeTab === 'library' 
                ? 'text-gray-900 font-bold bg-white shadow-sm' 
                : 'text-gray-500 hover:text-gray-700 bg-transparent'
            }`}
            onClick={() => setActiveTab('library')}
          >
            라이브러리
          </button>
        </div>
      </div>

             <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-6 bg-white">
        {renderContent()}
      </div>
    </div>
  )
}

export default App
