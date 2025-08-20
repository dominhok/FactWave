import React from 'react'

const LoadingMessage = ({ type = 'default' }) => {
  const getLoadingContent = () => {
    switch(type) {
      case 'image':
        return {
          icon: '🖼️',
          title: '이미지 분석 중',
          subtitle: 'AI 탐지 모델이 이미지를 검사하고 있습니다...',
          color: 'from-blue-500 to-purple-600'
        }
      case 'video':
        return {
          icon: '🎥',
          title: '영상 분석 중',
          subtitle: 'YouTube 영상 내용을 분석하고 있습니다...',
          color: 'from-purple-500 to-pink-600'
        }
      case 'fact':
        return {
          icon: '🔍',
          title: '팩트체킹 중',
          subtitle: 'AI 에이전트들이 정보를 검증하고 있습니다...',
          color: 'from-green-500 to-blue-600'
        }
      default:
        return {
          icon: '⏳',
          title: '처리 중',
          subtitle: '잠시만 기다려주세요...',
          color: 'from-gray-500 to-gray-600'
        }
    }
  }

  const content = getLoadingContent()

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 mb-5">
      {/* 상단 그라데이션 바 */}
      <div className={`h-1 bg-gradient-to-r ${content.color}`}>
        <div className="h-full bg-white/30 animate-pulse"></div>
      </div>
      
      <div className="p-6">
        <div className="flex items-center gap-4">
          {/* 아이콘 영역 */}
          <div className="relative">
            <div className="w-16 h-16 rounded-full bg-gradient-to-r from-gray-100 to-gray-200 flex items-center justify-center">
              <span className="text-3xl animate-pulse">{content.icon}</span>
            </div>
            {/* 회전하는 원 */}
            <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-blue-500 animate-spin"></div>
          </div>
          
          {/* 텍스트 영역 */}
          <div className="flex-1">
            <h4 className="text-lg font-semibold text-gray-800 mb-1">
              {content.title}
            </h4>
            <p className="text-sm text-gray-600">
              {content.subtitle}
            </p>
          </div>
          
          {/* 로딩 인디케이터 */}
          <div className="flex gap-1">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
        
        {/* 진행 바 */}
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className={`h-full bg-gradient-to-r ${content.color} rounded-full animate-loading-bar`}></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingMessage