function Library({ onLoadContext, onClose, savedConversations = [] }) {
  // 저장된 대화 목록을 Library 형식으로 변환
  const conversationItems = savedConversations.map(conv => {
    // 최종 판정 찾기 (Step3 또는 final_result에서)
    let finalVerdict = '분석완료';
    let confidence = 85;
    let summary = '';
    
    // Super Agent 메시지 찾기
    const superAgentMessage = conv.messages?.find(msg => 
      msg.agentId === 'super' || msg.agentName === 'Super Agent'
    );
    
    if (superAgentMessage) {
      finalVerdict = superAgentMessage.verdict || '분석완료';
      
      // Step3 결과에서 1줄 요약 추출
      // verdict_reasoning 또는 summary에서 첫 문장 추출
      if (superAgentMessage.verdictReasoning) {
        // verdict_reasoning의 첫 문장 또는 전체 (80자 이내)
        const firstSentence = superAgentMessage.verdictReasoning.split('.')[0];
        summary = firstSentence.length <= 80 ? 
                  firstSentence + '.' : 
                  superAgentMessage.verdictReasoning.substring(0, 77) + '...';
      } else if (superAgentMessage.summary) {
        // summary 필드가 있으면 그대로 사용
        summary = superAgentMessage.summary.length <= 80 ? 
                  superAgentMessage.summary : 
                  superAgentMessage.summary.substring(0, 77) + '...';
      } else if (superAgentMessage.reasoning) {
        // reasoning에서 추출
        const firstSentence = superAgentMessage.reasoning.split('.')[0];
        summary = firstSentence.length <= 80 ? 
                  firstSentence + '.' : 
                  superAgentMessage.reasoning.substring(0, 77) + '...';
      } else {
        summary = `${finalVerdict} - ${conv.totalResponses || 11}개 전문가 종합 분석`;
      }
    } else {
      summary = `${conv.totalResponses || 11}개의 전문가 분석을 통한 다각도 팩트체킹 완료`;
    }
    
    // 실제 사용자 질문 사용
    const actualQuestion = conv.question || '팩트체킹 질문';
    
    return {
      id: conv.id,
      title: actualQuestion, // 실제 질문 사용
      date: conv.date,
      agents: ["News", "Academia", "Logic", "Social", "Statistics"],
      confidence: confidence,
      verdict: finalVerdict,
      summary: summary, // Step3 1줄 요약
      isConversation: true,
      fullData: conv
    };
  });

  // 저장된 대화만 사용 (더미 데이터 제거)
  const allItems = conversationItems

  return (
    <div className="p-0">
      <style jsx>{`
        /* 판정 결과 색상 클래스 */
        .verdict-참 { background: #dcfce7; color: #16a34a; }
        .verdict-거짓 { background: #fee2e2; color: #dc2626; }
        .verdict-불확실 { background: #f3f4f6; color: #6b7280; }
        .verdict-정보부족 { background: #f3f4f6; color: #6b7280; }
      `}</style>
      <h2 className="text-gray-800 mb-5 text-xl font-semibold">팩트체킹 라이브러리</h2>

      {allItems.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <p className="text-gray-500 text-lg">아직 저장된 팩트체킹 결과가 없습니다</p>
          <p className="text-gray-400 text-sm mt-2">토론 탭에서 팩트체킹을 완료하면 여기에 저장됩니다</p>
        </div>
      ) : (
        <>
          {savedConversations.length > 0 && (
            <div className="mb-6">
              <h3 className="text-gray-600 mb-3 text-sm font-medium">저장된 팩트체킹 결과</h3>
              <div className="h-px bg-gray-200 mb-4"></div>
            </div>
          )}
          <div className="grid gap-4 mb-5">
            {allItems.map(item => (
            <div key={item.id} className="bg-white rounded-xl p-5 shadow-lg transition-transform duration-300 hover:-translate-y-0.5 cursor-pointer" onClick={() => onLoadContext && onLoadContext(item)}>
              <div className="flex justify-between items-start mb-3">
                <div className="flex-1">
                  <h3 className="m-0 text-base text-gray-800 font-medium">{item.title}</h3>
                  {item.isConversation && (
                    <span className="text-blue-600 text-xs font-medium">💬 저장된 대화</span>
                  )}
                </div>
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
                         agent === 'Logic' ? '🤔' : 
                         agent === 'Social' ? '👥' :
                         agent === 'Statistics' ? '📊' : '🔍'} {agent}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-1">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    item.verdict?.includes('참') ? 'verdict-참' :
                    item.verdict?.includes('거짓') || item.verdict?.includes('과장') ? 'verdict-거짓' :
                    item.verdict?.includes('불확실') || item.verdict?.includes('논란') || item.verdict?.includes('오해') ? 'verdict-불확실' :
                    item.verdict?.includes('정보부족') ? 'verdict-정보부족' :
                    item.verdict === '분석완료' ? 'verdict-불확실' :
                    'verdict-불확실'
                  }`}>
                    {item.verdict || '판정중'}
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
        </>
      )}
    </div>
  )
}

export default Library
