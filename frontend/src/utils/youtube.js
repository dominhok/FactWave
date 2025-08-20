/**
 * YouTube URL에서 비디오 ID 추출
 * @param {string} url - YouTube URL
 * @returns {string|null} 비디오 ID 또는 null
 */
export const extractYouTubeVideoId = (url) => {
  if (!url) return null
  
  // 다양한 YouTube URL 형식 지원
  const patterns = [
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)/,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)/,
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)/,
    /(?:https?:\/\/)?youtu\.be\/([^?]+)/,
    /(?:https?:\/\/)?m\.youtube\.com\/watch\?v=([^&]+)/,
    /(?:https?:\/\/)?www\.youtube\.com\/shorts\/([^?]+)/
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match && match[1]) {
      return match[1]
    }
  }
  
  return null
}

/**
 * YouTube 비디오 ID로부터 썸네일 URL 생성
 * @param {string} videoId - YouTube 비디오 ID
 * @param {string} quality - 썸네일 품질 (default, medium, high, standard, maxres)
 * @returns {string} 썸네일 URL
 */
export const getYouTubeThumbnail = (videoId, quality = 'high') => {
  if (!videoId) return null
  
  const qualityMap = {
    'default': 'default',      // 120x90
    'medium': 'mqdefault',     // 320x180
    'high': 'hqdefault',        // 480x360
    'standard': 'sddefault',    // 640x480
    'maxres': 'maxresdefault'   // 1280x720
  }
  
  const imageQuality = qualityMap[quality] || 'hqdefault'
  return `https://img.youtube.com/vi/${videoId}/${imageQuality}.jpg`
}

/**
 * YouTube URL 유효성 검사
 * @param {string} url - 검사할 URL
 * @returns {boolean} YouTube URL 여부
 */
export const isYouTubeUrl = (url) => {
  if (!url) return false
  return extractYouTubeVideoId(url) !== null
}

/**
 * YouTube 비디오 정보 가져오기 (썸네일, 제목 등)
 * @param {string} url - YouTube URL
 * @returns {object} 비디오 정보
 */
export const getYouTubeVideoInfo = (url) => {
  const videoId = extractYouTubeVideoId(url)
  
  if (!videoId) {
    return null
  }
  
  return {
    videoId,
    url: url,
    thumbnail: getYouTubeThumbnail(videoId, 'high'),
    thumbnailMedium: getYouTubeThumbnail(videoId, 'medium'),
    thumbnailMax: getYouTubeThumbnail(videoId, 'maxres'),
    embedUrl: `https://www.youtube.com/embed/${videoId}`,
    watchUrl: `https://www.youtube.com/watch?v=${videoId}`
  }
}