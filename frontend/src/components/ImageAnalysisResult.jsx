import React from 'react'

const ImageAnalysisResult = ({ analysis, imageUrl }) => {
  if (!analysis) return null

  const { ai_score, human_score, confidence, verdict_kr, risk_level } = analysis

  // 위험도별 색상
  const getRiskColor = (level) => {
    switch(level) {
      case 'high': return 'bg-red-500'
      case 'medium': return 'bg-yellow-500'
      case 'low': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  // 점수별 색상 그라데이션
  const getScoreColor = (score) => {
    if (score >= 80) return 'bg-gradient-to-r from-red-500 to-red-600'
    if (score >= 60) return 'bg-gradient-to-r from-orange-500 to-orange-600'
    if (score >= 40) return 'bg-gradient-to-r from-yellow-500 to-yellow-600'
    if (score >= 20) return 'bg-gradient-to-r from-blue-500 to-blue-600'
    return 'bg-gradient-to-r from-green-500 to-green-600'
  }

  // 판정 아이콘
  const getVerdictIcon = () => {
    return ai_score >= 50 ? '🤖' : '📸'
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <span className="text-2xl">🔍</span>
          AI 이미지 분석 결과
        </h3>
      </div>

      {/* 이미지 미리보기 */}
      {imageUrl && (
        <div className="p-4 bg-gray-50 border-b">
          <img 
            src={imageUrl} 
            alt="분석된 이미지" 
            className="max-w-full h-auto rounded-lg shadow-md max-h-48 mx-auto object-contain"
          />
        </div>
      )}

      {/* 메인 판정 */}
      <div className="p-6 text-center border-b bg-gradient-to-b from-white to-gray-50">
        <div className="text-5xl mb-3">{getVerdictIcon()}</div>
        <h4 className="text-2xl font-bold text-gray-800 mb-2">{verdict_kr}</h4>
        <div className="flex justify-center gap-2 items-center">
          <span className="text-sm text-gray-600">위험도:</span>
          <span className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${getRiskColor(risk_level)}`}>
            {risk_level === 'high' ? '높음' : risk_level === 'medium' ? '중간' : '낮음'}
          </span>
        </div>
      </div>

      {/* 점수 막대 그래프 */}
      <div className="p-6 space-y-6">
        {/* AI 점수 */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <span className="text-lg">🤖</span> AI 생성 확률
            </span>
            <span className="text-lg font-bold text-gray-900">{ai_score.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-8 overflow-hidden shadow-inner">
            <div 
              className={`h-full flex items-center justify-end pr-3 text-white text-sm font-semibold transition-all duration-500 ease-out ${getScoreColor(ai_score)}`}
              style={{ width: `${Math.min(ai_score, 100)}%` }}
            >
              {ai_score >= 10 && `${ai_score.toFixed(0)}%`}
            </div>
          </div>
        </div>

        {/* 실제 사진 점수 */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <span className="text-lg">📸</span> 실제 사진 확률
            </span>
            <span className="text-lg font-bold text-gray-900">{human_score.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-8 overflow-hidden shadow-inner">
            <div 
              className={`h-full flex items-center justify-end pr-3 text-white text-sm font-semibold transition-all duration-500 ease-out ${getScoreColor(human_score)}`}
              style={{ width: `${Math.min(human_score, 100)}%` }}
            >
              {human_score >= 10 && `${human_score.toFixed(0)}%`}
            </div>
          </div>
        </div>

        {/* 신뢰도 */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
              <span className="text-lg">📊</span> 분석 신뢰도
            </span>
            <span className="text-lg font-bold text-gray-900">{confidence.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden shadow-inner">
            <div 
              className="h-full bg-gradient-to-r from-purple-500 to-purple-600 flex items-center justify-end pr-3 text-white text-xs font-semibold transition-all duration-500 ease-out"
              style={{ width: `${Math.min(confidence, 100)}%` }}
            >
              {confidence >= 15 && `${confidence.toFixed(0)}%`}
            </div>
          </div>
        </div>
      </div>

      {/* 해석 가이드 */}
      <div className="bg-gray-50 p-4 border-t">
        <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <span>📈</span> 해석 가이드
        </h5>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-600">80% 이상: 거의 확실한 AI 생성</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-orange-500"></div>
            <span className="text-gray-600">60-80%: 높은 AI 생성 가능성</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <span className="text-gray-600">40-60%: AI 생성 의심</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-gray-600">20-40%: 실제일 가능성 높음</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-600">20% 미만: 실제 사진으로 판정</span>
          </div>
        </div>
      </div>

      {/* 기술 정보 */}
      <div className="bg-blue-50 p-3 text-xs text-blue-700 border-t border-blue-200">
        <div className="flex items-center gap-2">
          <span>⚙️</span>
          <span>Powered by Sightengine AI Detection API</span>
        </div>
      </div>
    </div>
  )
}

export default ImageAnalysisResult