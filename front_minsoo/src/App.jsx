import { useState } from 'react'
import Discussion from './components/Discussion'
import Results from './components/Results'
import Library from './components/Library'

function App() {
  const [activeTab, setActiveTab] = useState('discussion')
  const [loadedContext, setLoadedContext] = useState(null)

  // 디버깅용 로그
  console.log('Factwave App loaded', { activeTab, loadedContext })

  const handleLoadContext = (context) => {
    setLoadedContext(context)
    setActiveTab('discussion')
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'discussion':
        return <Discussion context={loadedContext} />
      case 'results':
        return <Results context={loadedContext} />
      case 'library':
        return <Library onLoadContext={handleLoadContext} />
      default:
        return <Discussion context={loadedContext} />
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-0 h-[600px] flex flex-col bg-white">
      <div className="flex bg-white px-5 py-4">
        <button 
          className={`flex-1 py-2 text-sm transition-colors duration-200 bg-transparent border-none ${
            activeTab === 'discussion' 
              ? 'text-gray-900 font-bold' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('discussion')}
        >
          토론
        </button>
        <button 
          className={`flex-1 py-2 text-sm transition-colors duration-200 bg-transparent border-none ${
            activeTab === 'results' 
              ? 'text-gray-900 font-bold' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('results')}
        >
          결과보기
        </button>
        <button 
          className={`flex-1 py-2 text-sm transition-colors duration-200 bg-transparent border-none ${
            activeTab === 'library' 
              ? 'text-gray-900 font-bold' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('library')}
        >
          라이브러리
        </button>
      </div>

             <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-6 bg-white">
        {renderContent()}
      </div>
    </div>
  )
}

export default App
