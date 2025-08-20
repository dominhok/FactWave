"""AI Image Detection Tool using Sightengine API - AI 생성 이미지 탐지"""

import os
import hashlib
import json
import requests
import logging
from typing import Type, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from pathlib import Path

from ..base_tool import EnhancedBaseTool
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

# Check if sightengine is available
try:
    from sightengine.client import SightengineClient
    SIGHTENGINE_SDK_AVAILABLE = True
except ImportError:
    SIGHTENGINE_SDK_AVAILABLE = False
    # SDK not required - we'll use direct API calls


class AIImageDetectionInput(BaseModel):
    """AI 이미지 탐지 입력 스키마"""
    image_url: str = Field(..., description="분석할 이미지 URL")
    confidence_threshold: Optional[float] = Field(0.5, description="AI 판정 임계값 (0.0~1.0)")


class AIImageDetectorTool(EnhancedBaseTool):
    """Sightengine API를 사용한 AI 생성 이미지 탐지 도구"""
    
    name: str = "AI Image Detector"
    description: str = """
    Sightengine API를 사용하여 이미지가 AI로 생성되었는지 탐지합니다.
    - Stable Diffusion, DALL-E, Midjourney, Flux 등 주요 AI 모델 탐지
    - 월 2,000회 무료 (일일 500회 제한)
    - 98%+ 정확도로 AI 생성 이미지 식별
    - 이미지 URL을 제공하면 AI 생성 확률을 분석
    - 팩트체킹 시 이미지 진위 여부 판단에 활용
    """
    args_schema: Type[BaseModel] = AIImageDetectionInput
    cache_duration: int = 86400  # 24시간 캐시
    
    def __init__(self):
        super().__init__()
        self.api_user = os.getenv('SIGHTENGINE_API_USER')
        self.api_secret = os.getenv('SIGHTENGINE_API_SECRET')
        self.base_url = "https://api.sightengine.com/1.0/check.json"
        
        # SDK 사용 가능하면 클라이언트 초기화
        self.client = None
        if SIGHTENGINE_SDK_AVAILABLE and self.api_user and self.api_secret:
            try:
                self.client = SightengineClient(self.api_user, self.api_secret)
                console.print("[green]Sightengine SDK 클라이언트 초기화 완료[/green]")
            except Exception as e:
                console.print(f"[yellow]SDK 초기화 실패, API 직접 호출 사용: {str(e)}[/yellow]")
    
    def _detect_with_api(self, image_url: str) -> Dict[str, Any]:
        """Sightengine API로 직접 AI 이미지 탐지"""
        if not self.api_user or not self.api_secret:
            logger.warning("[Sightengine] API 자격 증명이 설정되지 않음")
            return {
                "error": "Sightengine API 자격 증명이 설정되지 않았습니다",
                "setup_required": True
            }
        
        params = {
            'url': image_url,
            'models': 'genai',  # AI generation detection model
            'api_user': self.api_user,
            'api_secret': self.api_secret
        }
        
        logger.info(f"[Sightengine] API 요청 시작: {image_url[:100]}...")
        logger.debug(f"[Sightengine] 요청 파라미터: models=genai, user={self.api_user[:5]}***")
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=30,
                headers={
                    'User-Agent': 'FactWave/1.0 (AI Detection Tool)'
                }
            )
            
            logger.info(f"[Sightengine] API 응답 상태: {response.status_code}")
            
            if response.status_code == 402:
                logger.warning("[Sightengine] 월 무료 한도 초과 (402)")
                return {
                    "error": "월 무료 한도(2,000회)를 초과했습니다",
                    "limit_exceeded": True
                }
            
            response.raise_for_status()
            result = response.json()
            
            logger.debug(f"[Sightengine] API 응답: {json.dumps(result, indent=2)[:500]}...")
            
            if result.get('status') == 'success':
                # genai 모델 응답에서 AI 점수 추출
                ai_score = result.get('type', {}).get('ai_generated', 0)
                if 'genai' in result:
                    # 새로운 응답 형식
                    ai_score = result['genai'].get('ai_generated', 0) * 100
                    confidence = result['genai'].get('confidence', 0) * 100
                    logger.info(f"[Sightengine] AI 탐지 성공 - AI 점수: {ai_score:.1f}%, 신뢰도: {confidence:.1f}%")
                else:
                    # 기존 응답 형식
                    ai_score = ai_score * 100 if ai_score <= 1 else ai_score
                    confidence = 95  # 기본 신뢰도
                    logger.info(f"[Sightengine] AI 탐지 성공 - AI 점수: {ai_score:.1f}%")
                
                return {
                    "success": True,
                    "ai_score": ai_score,
                    "confidence": confidence,
                    "raw_response": result
                }
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                logger.error(f"[Sightengine] API 오류: {error_msg}")
                return {
                    "error": error_msg,
                    "code": result.get('error', {}).get('code', 'unknown')
                }
                
        except requests.exceptions.Timeout:
            logger.error("[Sightengine] 요청 시간 초과 (30초)")
            return {"error": "요청 시간 초과 (30초)"}
        except requests.exceptions.RequestException as e:
            logger.error(f"[Sightengine] API 요청 실패: {str(e)}")
            return {"error": f"API 요청 실패: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"[Sightengine] 응답 파싱 실패: {str(e)}")
            return {"error": f"응답 파싱 실패: {str(e)}"}
    
    def _detect_with_sdk(self, image_url: str) -> Dict[str, Any]:
        """Sightengine SDK를 사용한 AI 이미지 탐지"""
        if not self.client:
            return self._detect_with_api(image_url)
        
        try:
            # SDK를 통한 검사
            result = self.client.check('genai').set_url(image_url)
            
            if result.get('status') == 'success':
                return {
                    "success": True,
                    "ai_score": result.get('type', {}).get('ai_generated', 0),
                    "raw_response": result
                }
            else:
                return {
                    "error": result.get('error', {}).get('message', 'Unknown error'),
                    "code": result.get('error', {}).get('code', 'unknown')
                }
                
        except Exception as e:
            console.print(f"[yellow]SDK 호출 실패, API 직접 호출로 전환: {str(e)}[/yellow]")
            return self._detect_with_api(image_url)
    
    def _determine_ai_model(self, ai_score: float) -> str:
        """AI 점수를 기반으로 가능한 AI 모델 추정"""
        if ai_score >= 0.95:
            return "매우 높은 확률로 AI 생성 (Stable Diffusion/DALL-E/Midjourney 등)"
        elif ai_score >= 0.85:
            return "높은 확률로 AI 생성"
        elif ai_score >= 0.70:
            return "AI 생성 가능성 있음"
        elif ai_score >= 0.50:
            return "AI 생성 의심"
        elif ai_score >= 0.30:
            return "실제 이미지일 가능성 높음"
        else:
            return "실제 이미지로 판정"
    
    def _run(
        self,
        image_url: str,
        confidence_threshold: Optional[float] = 0.5
    ) -> str:
        """AI 이미지 탐지 수행"""
        
        # URL 유효성 검사
        if not image_url.startswith(('http://', 'https://')):
            return "❌ 유효한 이미지 URL을 입력하세요 (http:// 또는 https://로 시작)"
        
        # API 자격 증명 확인
        if not self.api_user or not self.api_secret:
            return self._get_setup_instructions()
        
        # AI 탐지 수행
        console.print(f"[cyan]Sightengine API로 이미지 분석 중...[/cyan]")
        logger.info(f"[Sightengine] 이미지 분석 시작: {image_url[:100]}...")
        
        # SDK 우선, 실패 시 API 직접 호출
        if SIGHTENGINE_SDK_AVAILABLE and self.client:
            logger.debug("[Sightengine] SDK 사용하여 분석")
            result = self._detect_with_sdk(image_url)
        else:
            logger.debug("[Sightengine] 직접 API 호출하여 분석")
            result = self._detect_with_api(image_url)
        
        # 오류 처리
        if result.get('error'):
            if result.get('setup_required'):
                return self._get_setup_instructions()
            elif result.get('limit_exceeded'):
                return """❌ Sightengine API 월 무료 한도 초과

📊 무료 플랜 한도:
• 월 2,000회 작업
• 일일 최대 500회

💡 해결 방법:
1. 다음 달까지 대기
2. 유료 플랜 업그레이드 ($29/월부터)
3. 다른 계정 사용

🔗 https://sightengine.com/pricing"""
            else:
                return f"❌ API 오류: {result['error']}"
        
        # 결과 파싱 (ai_score는 0-100 범위)
        ai_score_percent = result.get('ai_score', 0)  # 0-100 범위
        ai_score_normalized = ai_score_percent / 100  # 0-1 범위로 정규화
        
        # 판정 (threshold와 비교를 위해 정규화된 값 사용)
        is_ai = ai_score_normalized >= confidence_threshold
        verdict_emoji = "🤖" if is_ai else "📸"
        verdict = "AI 생성 이미지" if is_ai else "실제 이미지"
        
        # AI 모델 추정 (0-1 범위 필요)
        model_guess = self._determine_ai_model(ai_score_normalized)
        
        # 신뢰도 계산 (50%에서 멀수록 높은 신뢰도)
        confidence = abs(ai_score_percent - 50) * 2
        
        # 결과 포맷팅 (이미 백분율이므로 .1f 사용)
        output = f"""🔍 **AI 이미지 탐지 결과** (Sightengine API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📎 이미지: {image_url[:60]}{'...' if len(image_url) > 60 else ''}

📊 **분석 결과**
• AI 생성 점수: **{ai_score_percent:.1f}%**
• 실제 이미지 점수: **{(100-ai_score_percent):.1f}%**
• 탐지 신뢰도: **{confidence:.1f}%**

{verdict_emoji} **판정: {verdict}**
🎯 추정: {model_guess}

📈 **해석 가이드**
• 90% 이상: 거의 확실한 AI 생성
• 70-90%: 높은 AI 생성 가능성
• 50-70%: AI 생성 의심
• 30-50%: 실제일 가능성 높음
• 30% 미만: 실제 이미지로 판정

⚙️ **설정**
• 판정 임계값: {confidence_threshold:.1%}
• 탐지 엔진: Sightengine GenAI Model
• 지원 AI: Stable Diffusion, DALL-E, Midjourney, Flux 등

💡 **참고사항**
• AI 탐지는 100% 정확하지 않을 수 있습니다
• 편집되거나 필터가 적용된 실제 이미지도 AI로 오탐될 수 있습니다
• 고품질 AI 이미지는 탐지가 어려울 수 있습니다"""
        
        return output
    
    def _get_setup_instructions(self) -> str:
        """Sightengine API 설정 안내"""
        return """❌ Sightengine API 설정 필요

📋 **설정 방법:**

1. **계정 생성** (무료)
   🔗 https://sightengine.com/signup
   
2. **API 자격 증명 확인**
   - 대시보드 접속: https://dashboard.sightengine.com
   - API User와 API Secret 확인
   
3. **.env 파일에 추가**
   ```
   SIGHTENGINE_API_USER=your_api_user_here
   SIGHTENGINE_API_SECRET=your_api_secret_here
   ```

4. **선택사항: SDK 설치** (더 나은 성능)
   ```bash
   pip install sightengine
   # 또는
   uv pip install sightengine
   ```

📊 **무료 플랜 제공사항:**
• 월 2,000회 API 호출
• 일일 최대 500회
• AI 생성 이미지 탐지 (genai 모델)
• 추가 모델 사용 가능 (부적절한 콘텐츠 등)

💰 **유료 플랜 (필요시):**
• Starter: $29/월 (10,000회)
• Growth: $99/월 (40,000회)
• Pro: $399/월 (200,000회)

🎯 **Sightengine 장점:**
• 업계 최고 수준 정확도 (98%+)
• Stable Diffusion, DALL-E, Midjourney 등 모든 주요 AI 탐지
• 빠른 응답 시간 (<1초)
• 추가 기능: 부적절한 콘텐츠, 텍스트, 얼굴 탐지 등"""


# 테스트용 코드
if __name__ == "__main__":
    # .env 파일 로드 - 루트 디렉토리
    from dotenv import load_dotenv
    from pathlib import Path
    root_dir = Path(__file__).parent.parent.parent.parent.parent
    env_path = root_dir / ".env"
    load_dotenv(env_path)
    
    tool = AIImageDetectorTool()
    
    # 테스트 이미지 URL (실제 테스트 시 변경 필요)
    test_urls = [
        "https://example.com/real-photo.jpg",  # 실제 사진
        "https://example.com/ai-generated.jpg",  # AI 생성 이미지
    ]
    
    for url in test_urls:
        print("\n" + "="*50)
        result = tool._run(url)
        print(result)