import React, { useState } from 'react'

const YouTubeThumbnail = ({ videoInfo, url }) => {
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)
  
  if (!videoInfo && !url) return null
  
  const displayUrl = videoInfo?.url || url
  const thumbnailUrl = videoInfo?.thumbnail
  
  return (
    <div className="youtube-thumbnail-container mb-3">
      <div className="bg-gradient-to-r from-red-500 to-red-600 text-white px-3 py-1 rounded-t-lg text-sm font-semibold inline-flex items-center gap-2">
        <span>🎥</span>
        <span>YouTube 영상</span>
      </div>
      
      <div className="bg-white border border-gray-200 rounded-b-lg rounded-tr-lg shadow-sm overflow-hidden">
        {thumbnailUrl && !imageError && (
          <div className="relative group">
            {/* 썸네일 이미지 */}
            <div className="relative">
              {!imageLoaded && (
                <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
                  <div className="text-gray-400">
                    <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
              )}
              
              <img 
                src={thumbnailUrl}
                alt="YouTube 썸네일"
                className={`w-full h-auto max-h-64 object-cover transition-opacity duration-300 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
                onLoad={() => setImageLoaded(true)}
                onError={() => {
                  setImageError(true)
                  setImageLoaded(true)
                }}
              />
              
              {/* 재생 버튼 오버레이 */}
              {imageLoaded && !imageError && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="bg-black bg-opacity-70 rounded-full p-3 group-hover:bg-opacity-90 transition-all">
                    <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </div>
                </div>
              )}
            </div>
            
            {/* 호버 시 정보 */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <p className="text-white text-xs truncate">
                {displayUrl}
              </p>
            </div>
          </div>
        )}
        
        {/* URL 표시 */}
        <div className="p-3 bg-gray-50">
          <a 
            href={displayUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-2 truncate"
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            <span className="truncate">{displayUrl}</span>
          </a>
        </div>
        
        {/* 에러 메시지 */}
        {imageError && (
          <div className="p-4 bg-red-50 border-t border-red-200">
            <p className="text-sm text-red-600 flex items-center gap-2">
              <span>⚠️</span>
              <span>썸네일을 불러올 수 없습니다</span>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default YouTubeThumbnail