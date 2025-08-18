import { useState } from 'react'

function Results({ savedResults = [] }) {
  const [selectedResult, setSelectedResult] = useState(null)

  // 저장된 결과만 사용 (더미 데이터 제거)
  const results = savedResults

  // 클릭 핸들러 - 토글 기능 구현
  const handleResultClick = (result) => {
    // 같은 결과를 다시 클릭하면 null로 설정 (닫기)
    if (selectedResult?.id === result.id) {
      setSelectedResult(null)
    } else {
      setSelectedResult(result)
    }
  }

  return (
    <div className="p-0">
      <style jsx>{`
        /* 판정 결과 색상 클래스 */
        .verdict-참 { background: #dcfce7; color: #16a34a; }
        .verdict-거짓 { background: #fee2e2; color: #dc2626; }
        .verdict-불확실 { background: #f3f4f6; color: #6b7280; }
        .verdict-정보부족 { background: #f3f4f6; color: #6b7280; }
      `}</style>
      <h2 className="text-gray-800 mb-5 text-xl font-semibold">팩트체킹 결과</h2>
      
      {results.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-gray-500 text-lg">아직 팩트체킹 결과가 없습니다</p>
          <p className="text-gray-400 text-sm mt-2">토론 탭에서 질문을 입력하면 결과가 여기에 표시됩니다</p>
        </div>
      ) : (
        <>
          {savedResults.length > 0 && (
            <div className="mb-6">
              <h3 className="text-gray-600 mb-3 text-sm font-medium">최근 팩트체킹 결과</h3>
              <div className="h-px bg-gray-200 mb-4"></div>
            </div>
          )}
          
          <div className="grid gap-4 mb-5">
        {results.map((result) => (
          <div key={result.id}>
            {/* 결과 카드 */}
            <div 
              className={`bg-white rounded-xl p-5 shadow-lg cursor-pointer transition-all duration-300 border-2 ${
                selectedResult?.id === result.id ? 'border-gray-600' : 'border-transparent'
              } hover:-translate-y-0.5 hover:shadow-xl`}
              onClick={() => handleResultClick(result)}
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="m-0 text-base text-gray-800 flex-1 font-medium">{result.question}</h3>
                <span className="text-gray-500 text-xs whitespace-nowrap ml-2.5">{result.date}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    result.overallVerdict?.includes('참') ? 'verdict-참' :
                    result.overallVerdict?.includes('거짓') || result.overallVerdict?.includes('과장') ? 'verdict-거짓' :
                    result.overallVerdict?.includes('불확실') || result.overallVerdict?.includes('논란') || result.overallVerdict?.includes('오해') ? 'verdict-불확실' :
                    result.overallVerdict?.includes('정보부족') ? 'verdict-정보부족' :
                    'verdict-불확실'
                  }`}>
                    {result.overallVerdict || '판정중'}
                  </span>
                  <span className="text-gray-500 text-xs">{result.confidence}% 신뢰도</span>
                </div>
                
                <div className="flex gap-2">
                  {result.agents.map((agent, index) => (
                    <div key={index} className="flex flex-col items-center text-xs">
                      <span className="font-semibold text-gray-800">{agent.name}</span>
                      <span className={`px-1 py-0.5 rounded text-xs ${
                        agent.verdict?.includes('참') ? 'verdict-참' :
                        agent.verdict?.includes('거짓') || agent.verdict?.includes('과장') ? 'verdict-거짓' :
                        agent.verdict?.includes('불확실') || agent.verdict?.includes('논란') || agent.verdict?.includes('오해') ? 'verdict-불확실' :
                        agent.verdict?.includes('정보부족') ? 'verdict-정보부족' :
                        'verdict-불확실'
                      }`}>
                        {agent.verdict || '판정중'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 상세 분석 - 선택된 결과 바로 아래에 표시 */}
            {selectedResult?.id === result.id && (
              <div className="bg-white rounded-xl p-5 shadow-lg mt-3 animate-in slide-in-from-top-2">
                <h3 className="text-gray-800 mb-5 text-lg font-semibold">상세 분석: {selectedResult.question}</h3>
                
                <div className="grid gap-4 mb-5">
                  {selectedResult.agents.map((agent, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-3">
                        <span className="text-xl w-8 h-8 flex items-center justify-center bg-white rounded-full">
                          {agent.name === 'News' ? '📰' : 
                           agent.name === 'Academia' ? '🎓' : 
                           agent.name === 'Logic' ? '🤔' : 
                           agent.name === 'Social' ? '👥' :
                           agent.name === 'Statistics' ? '📊' : '🔍'}
                        </span>
                        <span className="font-medium text-gray-800">{agent.name} Agent</span>
                        <span className="text-sm text-gray-500 ml-auto">{agent.confidence}%</span>
                      </div>
                      
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-200 rounded-full relative">
                          <div 
                            className="h-full bg-gray-600 rounded-full transition-all duration-300"
                            style={{ width: `${agent.confidence}%` }}
                          ></div>
                        </div>
                        
                        <div className={`px-2 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
                          agent.verdict?.includes('참') ? 'verdict-참' :
                          agent.verdict?.includes('거짓') || agent.verdict?.includes('과장') ? 'verdict-거짓' :
                          agent.verdict?.includes('불확실') || agent.verdict?.includes('논란') || agent.verdict?.includes('오해') ? 'verdict-불확실' :
                          agent.verdict?.includes('정보부족') ? 'verdict-정보부족' :
                          'verdict-불확실'
                        }`}>
                          {agent.verdict || '판정중'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-blue-800 mb-2 text-base font-semibold">종합 판단</h4>
                  <p className="text-blue-800 m-0 text-sm leading-relaxed mb-3">
                    {selectedResult.agents.filter(a => a.verdict === selectedResult.overallVerdict).length}개의 에이전트가 
                    "{selectedResult.overallVerdict}" 판단을 내렸으며, 
                    전체 신뢰도는 {selectedResult.confidence}%입니다.
                  </p>
                  
                  {/* Super Agent 분석 결과 표시 */}
                  {selectedResult.verdictReasoning && (
                    <div className="mt-3 pt-3 border-t border-blue-200">
                      <p className="text-blue-800 text-sm leading-relaxed">{selectedResult.verdictReasoning}</p>
                    </div>
                  )}
                  
                  {selectedResult.keyAgreements && selectedResult.keyAgreements.length > 0 && (
                    <div className="mt-3">
                      <h5 className="text-blue-700 text-sm font-semibold mb-1">주요 합의점:</h5>
                      <ul className="list-disc list-inside text-blue-700 text-sm">
                        {selectedResult.keyAgreements.map((agreement, idx) => (
                          <li key={idx}>{agreement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedResult.keyDisagreements && selectedResult.keyDisagreements.length > 0 && (
                    <div className="mt-3">
                      <h5 className="text-blue-700 text-sm font-semibold mb-1">주요 불일치점:</h5>
                      <ul className="list-disc list-inside text-blue-700 text-sm">
                        {selectedResult.keyDisagreements.map((disagreement, idx) => (
                          <li key={idx}>{disagreement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
        </>
      )}
    </div>
  )
}

export default Results