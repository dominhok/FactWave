function Library({ onLoadContext, onClose }) {
  const libraryItems = [
    {
      id: 1,
      title: "키 성장 호르몬의 효과와 위험성",
      date: "2024-01-15",
      agents: ["News", "Academia", "Logic"],
      confidence: 92,
      verdict: "부정적",
      summary: "성인 키 성장 호르몬의 효과에 대한 종합 분석 결과, 일반인 사용의 효과는 입증되지 않았으며 오히려 부작용 위험이 높은 것으로 나타났습니다."
    },
    {
      id: 2,
      title: "코로나 백신 부작용 논란의 진실",
      date: "2024-01-14",
      agents: ["News", "Academia", "Social"],
      confidence: 88,
      verdict: "긍정적",
      summary: "코로나 백신의 부작용에 대한 다양한 주장들을 분석한 결과, 백신의 안전성은 과학적으로 입증되었으며 부작용은 매우 드물게 발생합니다."
    },
    {
      id: 3,
      title: "AI 기술 발전이 일자리에 미치는 영향",
      date: "2024-01-13",
      agents: ["News", "Academia", "Logic", "Social"],
      confidence: 76,
      verdict: "중립적",
      summary: "AI 기술이 일자리에 미치는 영향에 대해 다양한 관점에서 분석한 결과, 일부 직종은 대체될 수 있지만 새로운 일자리 창출 가능성도 존재합니다."
    }
  ]

  return (
    <div className="p-0 relative">
      {/* X 버튼 */}
      <button 
        onClick={onClose}
        className="absolute top-2 right-2 w-6 h-6 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors duration-200 text-sm font-bold"
      >
        ×
      </button>

      <div className="text-center mb-5">
        <h2 className="text-gray-800 mb-2 text-xl font-semibold">팩트체킹 라이브러리</h2>
        <p className="text-gray-500 text-sm m-0">검증된 팩트체킹 결과들을 확인하세요</p>
      </div>

      <div className="min-h-[200px]">
        <div className="grid gap-4">
          {libraryItems.map(item => (
            <div key={item.id} className="bg-white rounded-xl p-5 shadow-lg transition-transform duration-300 hover:-translate-y-0.5 cursor-pointer" onClick={() => onLoadContext && onLoadContext(item)}>
              <div className="flex justify-between items-start mb-3">
                <h3 className="m-0 text-base text-gray-800 flex-1 font-medium">{item.title}</h3>
                <span className="text-gray-500 text-xs">{item.date}</span>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-600 text-sm leading-relaxed m-0">{item.summary}</p>
              </div>
              
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <span className="text-xs text-gray-500 mb-1 block">참여 에이전트:</span>
                  <div className="flex gap-1 flex-wrap">
                    {item.agents.map((agent, index) => (
                      <span key={index} className="bg-gray-100 px-1.5 py-0.5 rounded text-xs text-gray-600">
                        {agent === 'News' ? '📰' : 
                         agent === 'Academia' ? '🎓' : 
                         agent === 'Logic' ? '🤔' : '👥'} {agent}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${
                    item.verdict === '긍정적' ? 'bg-green-100 text-green-800' :
                    item.verdict === '부정적' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {item.verdict}
                  </span>
                  <span className="text-gray-500 text-xs">{item.confidence}% 신뢰도</span>
                </div>
              </div>
              
              <div className="text-center">
                <span className="text-blue-600 text-sm font-medium">클릭하여 컨텍스트 확인</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Library
