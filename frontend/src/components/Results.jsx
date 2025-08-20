import { useState } from 'react'
import ImageAnalysisResult from './ImageAnalysisResult'
import YouTubeThumbnail from './YouTubeThumbnail'

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
                <div className="flex items-center gap-2 flex-1">
                  {/* 분석 타입 표시 */}
                  {result.analysisType === 'image' && (
                    <span className="text-2xl" title="이미지 분석">🖼️</span>
                  )}
                  {result.analysisType === 'youtube' && (
                    <span className="text-2xl" title="YouTube 동영상 분석">🎥</span>
                  )}
                  <h3 className="m-0 text-base text-gray-800 flex-1 font-medium">{result.question}</h3>
                </div>
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
                  {/* 신뢰도 표시 (새로운 형식) */}
                  {result.finalReport?.confidenceLevel && (
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      result.finalReport.confidenceLevel === '높음' ? 'bg-green-100 text-green-700' :
                      result.finalReport.confidenceLevel === '중간' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      신뢰도: {result.finalReport.confidenceLevel}
                    </span>
                  )}
                </div>
                
                <div className="flex gap-2">
                  {result.agents?.map((agent, index) => (
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
              
              {/* 미디어 정보 미리보기 */}
              {result.mediaInfo && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  {result.analysisType === 'image' && result.mediaInfo.imageUrl && (
                    <div className="flex items-center gap-2">
                      <img 
                        src={result.mediaInfo.imageUrl} 
                        alt="분석된 이미지" 
                        className="w-16 h-16 object-cover rounded"
                      />
                      <span className="text-xs text-gray-600">이미지 분석 결과 포함</span>
                    </div>
                  )}
                  {result.analysisType === 'youtube' && result.mediaInfo.videoInfo && (
                    <div className="flex items-center gap-2">
                      <YouTubeThumbnail videoInfo={result.mediaInfo.videoInfo} size="small" />
                      <span className="text-xs text-gray-600">동영상 분석 결과 포함</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* 상세 분석 - 선택된 결과 바로 아래에 표시 */}
            {selectedResult?.id === result.id && (
              <div className="bg-white rounded-xl p-5 shadow-lg mt-3 animate-in slide-in-from-top-2">
                <h3 className="text-gray-800 mb-5 text-lg font-semibold">상세 분석: {selectedResult.question}</h3>
                
                {/* 토론 하이라이트 섹션 */}
                {selectedResult.debateHighlights && selectedResult.debateHighlights.length > 0 && (
                  <div className="mb-5">
                    <h4 className="text-gray-700 mb-3 text-base font-semibold">💬 토론 하이라이트</h4>
                    <div className="space-y-3">
                      {selectedResult.debateHighlights.map((highlight, idx) => (
                        <div key={idx} className="bg-yellow-50 rounded-lg p-3 border-l-4 border-yellow-400">
                          <div className="font-medium text-sm text-gray-800 mb-1">{highlight.agentName}</div>
                          {highlight.openingStatement && (
                            <p className="text-sm text-gray-700 mb-2">"{highlight.openingStatement}"</p>
                          )}
                          {highlight.myArgument && (
                            <p className="text-sm text-gray-700 italic">핵심 주장: {highlight.myArgument}</p>
                          )}
                          {highlight.questions && highlight.questions.length > 0 && (
                            <div className="mt-2">
                              <span className="text-xs text-gray-600">질문:</span>
                              <ul className="text-xs text-gray-600 ml-4">
                                {highlight.questions.map((q, qIdx) => (
                                  <li key={qIdx}>• {q}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* 에이전트별 분석 */}
                <div className="grid gap-4 mb-5">
                  {selectedResult.agents?.map((agent, index) => (
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
                      </div>
                      
                      <div className="flex items-center">
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
                
                {/* 최종 종합 판단 */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="text-blue-800 mb-2 text-base font-semibold">종합 판단</h4>
                  
                  {/* 새로운 형식의 최종 보고서 표시 */}
                  {selectedResult.finalReport && (
                    <>
                      {/* 요약 */}
                      {selectedResult.finalReport.executiveSummary && (
                        <div className="mb-3">
                          <p className="text-blue-800 text-sm leading-relaxed font-medium">
                            📝 {selectedResult.finalReport.executiveSummary}
                          </p>
                        </div>
                      )}
                      
                      {/* 핵심 요소 */}
                      {selectedResult.finalReport.keyFactors && selectedResult.finalReport.keyFactors.length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-blue-700 text-sm font-semibold mb-1">⚡ 판정의 핵심 요소:</h5>
                          <ul className="list-disc list-inside text-blue-700 text-sm">
                            {selectedResult.finalReport.keyFactors.map((factor, idx) => (
                              <li key={idx}>{factor}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* 맥락 분석 */}
                      {selectedResult.finalReport.contextualAnalysis && (
                        <div className="mt-3">
                          <h5 className="text-blue-700 text-sm font-semibold mb-1">📍 맥락 분석:</h5>
                          <p className="text-blue-800 text-sm leading-relaxed">{selectedResult.finalReport.contextualAnalysis}</p>
                        </div>
                      )}
                      
                      {/* 전문가 요약 */}
                      {selectedResult.finalReport.expertSummary && Object.keys(selectedResult.finalReport.expertSummary).length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-blue-700 text-sm font-semibold mb-2">👥 전문가별 판정:</h5>
                          <div className="space-y-1">
                            {Object.entries(selectedResult.finalReport.expertSummary).map(([agent, data]) => (
                              <div key={agent} className="flex items-center gap-2 text-xs">
                                <span className="font-medium">{agent}:</span>
                                <span className={`px-1.5 py-0.5 rounded ${
                                  data.verdict?.includes('참') ? 'bg-green-100 text-green-700' :
                                  data.verdict?.includes('거짓') ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {data.verdict}
                                </span>
                                {data.reliability && (
                                  <span className={`text-xs ${
                                    data.reliability === '높음' ? 'text-green-600' :
                                    data.reliability === '중간' ? 'text-yellow-600' :
                                    'text-gray-600'
                                  }`}>
                                    (신뢰도: {data.reliability})
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {/* 합의점과 이견 */}
                      {selectedResult.finalReport.consensusPoints && selectedResult.finalReport.consensusPoints.length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-blue-700 text-sm font-semibold mb-1">🤝 전문가 합의점:</h5>
                          <ul className="list-disc list-inside text-blue-700 text-sm">
                            {selectedResult.finalReport.consensusPoints.map((point, idx) => (
                              <li key={idx}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {selectedResult.finalReport.divergencePoints && selectedResult.finalReport.divergencePoints.length > 0 && (
                        <div className="mt-3">
                          <h5 className="text-blue-700 text-sm font-semibold mb-1">🤔 전문가 이견:</h5>
                          <ul className="list-disc list-inside text-blue-700 text-sm">
                            {selectedResult.finalReport.divergencePoints.map((point, idx) => (
                              <li key={idx}>{point}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {/* 주의사항 */}
                      {selectedResult.finalReport.caveats && selectedResult.finalReport.caveats.length > 0 && (
                        <div className="mt-3 p-2 bg-orange-50 rounded">
                          <h5 className="text-orange-600 text-sm font-semibold mb-1">⚠️ 주의사항:</h5>
                          <ul className="list-disc list-inside text-orange-600 text-sm">
                            {selectedResult.finalReport.caveats.map((caveat, idx) => (
                              <li key={idx}>{caveat}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                  
                  {/* 기존 형식 호환성 (이전 데이터) */}
                  {!selectedResult.finalReport && (
                    <>
                      <p className="text-blue-800 m-0 text-sm leading-relaxed mb-3">
                        {selectedResult.agents?.filter(a => a.verdict === selectedResult.overallVerdict).length}개의 에이전트가 
                        "{selectedResult.overallVerdict}" 판단을 내렸습니다.
                      </p>
                      
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
                    </>
                  )}
                </div>
                
                {/* 미디어 상세 정보 */}
                {selectedResult.mediaInfo && (
                  <div className="mt-5">
                    {selectedResult.analysisType === 'image' && selectedResult.mediaInfo.imageUrl && (
                      <div>
                        <h4 className="text-gray-700 mb-3 text-base font-semibold">🖼️ 분석된 이미지</h4>
                        <ImageAnalysisResult 
                          analysis={selectedResult.mediaInfo.analysis} 
                          imageUrl={selectedResult.mediaInfo.imageUrl}
                        />
                      </div>
                    )}
                    {selectedResult.analysisType === 'youtube' && selectedResult.mediaInfo.videoInfo && (
                      <div>
                        <h4 className="text-gray-700 mb-3 text-base font-semibold">🎥 분석된 동영상</h4>
                        <YouTubeThumbnail videoInfo={selectedResult.mediaInfo.videoInfo} size="large" />
                        {selectedResult.mediaInfo.analysis && (
                          <div className="mt-3 p-3 bg-gray-50 rounded">
                            <p className="text-sm text-gray-700">{selectedResult.mediaInfo.analysis}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
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