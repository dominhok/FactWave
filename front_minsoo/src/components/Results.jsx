import { useState } from 'react'

function Results() {
  const [selectedResult, setSelectedResult] = useState(null)

  // 더미 결과 데이터
  const results = [
    {
      id: 1,
      question: "키 크는 약이 정말 효과가 있나요?",
      date: "2024-01-15",
      agents: [
        { name: "News", confidence: 85, verdict: "부정적" },
        { name: "Academia", confidence: 92, verdict: "부정적" },
        { name: "Logic", confidence: 78, verdict: "부정적" },
        { name: "Social", confidence: 81, verdict: "부정적" }
      ],
      overallVerdict: "부정적",
      confidence: 84
    },
    {
      id: 2,
      question: "코로나 백신의 부작용이 심각한가요?",
      date: "2024-01-14",
      agents: [
        { name: "News", confidence: 88, verdict: "긍정적" },
        { name: "Academia", confidence: 95, verdict: "긍정적" },
        { name: "Logic", confidence: 82, verdict: "긍정적" },
        { name: "Social", confidence: 75, verdict: "중립적" }
      ],
      overallVerdict: "긍정적",
      confidence: 85
    }
  ]

  return (
    <div className="p-0">
      <h2 className="text-gray-800 mb-5 text-xl font-semibold">팩트체킹 결과</h2>
      
      <div className="grid gap-4 mb-5">
        {results.map((result) => (
          <div 
            key={result.id} 
                         className={`bg-white rounded-xl p-5 shadow-lg cursor-pointer transition-all duration-300 border-2 ${
               selectedResult?.id === result.id ? 'border-gray-600' : 'border-transparent'
             } hover:-translate-y-0.5 hover:shadow-xl`}
            onClick={() => setSelectedResult(result)}
          >
            <div className="flex justify-between items-start mb-3">
              <h3 className="m-0 text-base text-gray-800 flex-1 font-medium">{result.question}</h3>
              <span className="text-gray-500 text-xs whitespace-nowrap ml-2.5">{result.date}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${
                  result.overallVerdict === '긍정적' ? 'bg-green-100 text-green-800' :
                  result.overallVerdict === '부정적' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {result.overallVerdict}
                </span>
                <span className="text-gray-500 text-xs">{result.confidence}% 신뢰도</span>
              </div>
              
              <div className="flex gap-2">
                {result.agents.map((agent, index) => (
                  <div key={index} className="flex flex-col items-center text-xs">
                    <span className="font-semibold text-gray-800">{agent.name}</span>
                    <span className={`px-1 py-0.5 rounded text-xs uppercase ${
                      agent.verdict === '긍정적' ? 'bg-green-100 text-green-800' :
                      agent.verdict === '부정적' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.verdict}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedResult && (
        <div className="bg-white rounded-xl p-5 shadow-lg mt-5">
          <h3 className="text-gray-800 mb-5 text-lg font-semibold">상세 분석: {selectedResult.question}</h3>
          
          <div className="grid gap-4 mb-5">
            {selectedResult.agents.map((agent, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xl w-8 h-8 flex items-center justify-center bg-white rounded-full">
                    {agent.name === 'News' ? '📰' : 
                     agent.name === 'Academia' ? '🎓' : 
                     agent.name === 'Logic' ? '🤔' : '👥'}
                  </span>
                  <span className="font-medium text-gray-800">{agent.name} Agent</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full relative mr-3">
                                         <div 
                       className="h-full bg-gray-600 rounded-full transition-all duration-300"
                       style={{ width: `${agent.confidence}%` }}
                     ></div>
                    <span className="absolute -right-8 -top-0.5 text-xs text-gray-500">{agent.confidence}%</span>
                  </div>
                  
                  <div className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${
                    agent.verdict === '긍정적' ? 'bg-green-100 text-green-800' :
                    agent.verdict === '부정적' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {agent.verdict}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="text-blue-800 mb-2 text-base font-semibold">종합 판단</h4>
            <p className="text-blue-800 m-0 text-sm leading-relaxed">
              {selectedResult.agents.filter(a => a.verdict === selectedResult.overallVerdict).length}개의 에이전트가 
              "{selectedResult.overallVerdict}" 판단을 내렸으며, 
              전체 신뢰도는 {selectedResult.confidence}%입니다.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Results
