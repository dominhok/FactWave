# FactWave 🌊

**AI 기반 다중 에이전트 실시간 팩트체킹 시스템**

FactWave는 CrewAI 오케스트레이션을 활용하여 5개의 전문 AI 에이전트가 협업하는 3단계 검증 시스템입니다. 실시간 WebSocket 통신과 Chrome 확장 프로그램을 통해 웹 브라우징 중 즉시 정보 검증이 가능합니다.

## ✨ 주요 특징

- 🤖 **5개 전문 에이전트**: 학술(25%), 뉴스(30%), 통계(20%), 논리(15%), 소셜(10%) 가중치 기반 협업
- ⚡ **실시간 스트리밍**: WebSocket 기반 분석 과정 실시간 모니터링
- 🎯 **3단계 검증 파이프라인**: 독립 분석 → 구조화된 토론 → 최종 종합
- 🌐 **Chrome 사이드 패널**: Manifest V3 기반 450x600px 확장 프로그램
- 📊 **10+ 전문 연구 도구**: 학술 논문, 뉴스, 통계 데이터, SNS 트렌드 통합 분석
- 🧠 **RAG 시스템**: 40+ OWID 데이터셋 사전 인덱싱된 ChromaDB 벡터 검색
- 🌍 **다국어 지원**: 한국어 우선, 영어 보조 지원

## 🏗️ 시스템 아키텍처

### 3단계 협업 검증 파이프라인

```
[입력 진술] → [Step 1: 독립 분석] → [Step 2: 구조화된 토론] → [Step 3: 최종 종합] → [검증 결과]
```

#### **Step 1: 독립적 초기 분석**
각 에이전트가 자신의 전문 도구를 활용하여 독립적으로 분석:

| 에이전트 | 가중치 | 전문 도구 | 캐싱 전략 |
|---------|--------|-----------|-----------|
| 📚 **학술 에이전트** | 25% | OpenAlex (240M+ 논문), ArXiv, Wikipedia, Tavily | 72시간 |
| 📰 **뉴스 에이전트** | 30% | Naver News, NewsAPI (80K+ 언론사), Google Fact Check | 1시간 |
| 📊 **통계 에이전트** | 20% | KOSIS, FRED, World Bank, OWID RAG | 72시간 |
| 🤔 **논리 에이전트** | 15% | 순수 논리 분석 (도구 미사용) | - |
| 👥 **소셜 에이전트** | 10% | Twitter API (twscrape), YouTube | 30분 |

#### **Step 2: 구조화된 토론**
- 모든 에이전트가 Step 1 결과를 공유하고 상호 검토
- 외부 도구 없이 순수 토론과 분석
- 다른 관점을 고려한 의견 개선 및 반박

#### **Step 3: 최종 종합**
- **Super Agent**가 모든 분석 종합
- 가중 신뢰도 매트릭스 생성
- 최종 판정 및 상세 근거 제시

## 🚀 빠른 시작

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd FactWave
```

### 2. 백엔드 설정

```bash
cd backend
pip install -e .  # 또는 uv pip install -e . (더 빠름)

# 환경변수 설정
cp example.env .env
# .env 파일에 필수 API 키 추가
```

### 3. 프론트엔드 설정

```bash
cd frontend
npm install
```

### 4. 실행

**백엔드 서버 (터미널 1):**
```bash
cd backend
python -m app.api.server  # FastAPI WebSocket 서버 (포트 8000)
```

**프론트엔드 개발 서버 (터미널 2):**
```bash
cd frontend
npm run dev  # Vite 개발 서버 (포트 5173)
```

### 5. Chrome 확장 프로그램 설치
1. Chrome에서 `chrome://extensions/` 열기
2. "개발자 모드" 활성화
3. "압축 해제된 확장 프로그램 로드" 클릭
4. `frontend/dist` 폴더 선택

## 📁 프로젝트 구조

### 백엔드 아키텍처
```
backend/
├── app/
│   ├── agents/                    # AI 에이전트 시스템
│   │   ├── base.py               # FactWaveAgent 기본 클래스
│   │   ├── academic_agent.py     # 학술 연구 전문가
│   │   ├── news_agent.py         # 뉴스 검증 전문가
│   │   ├── statistics_agent.py   # 통계 데이터 전문가
│   │   ├── logic_agent.py        # 논리 검증 전문가
│   │   ├── social_agent.py       # 소셜 미디어 전문가
│   │   └── super_agent.py        # 최종 종합 코디네이터
│   │
│   ├── services/tools/            # 도메인별 연구 도구
│   │   ├── base_tool.py          # EnhancedBaseTool (캐싱, 재시도)
│   │   ├── academic/             # 학술 도구
│   │   │   ├── arxiv_tool.py
│   │   │   ├── openalex_tool.py
│   │   │   └── wikipedia_tool.py
│   │   ├── news/                 # 뉴스 도구
│   │   │   ├── naver_news_tool.py
│   │   │   ├── newsapi_tool.py
│   │   │   └── factcheck_google_tool.py
│   │   ├── statistics/           # 통계 도구
│   │   │   ├── kosis_search_tool.py
│   │   │   ├── fred_search_tool.py
│   │   │   ├── worldbank_search_tool.py
│   │   │   └── owid_enhanced_rag.py
│   │   ├── community/            # 커뮤니티 도구
│   │   │   ├── twitter_tool.py
│   │   │   └── youtube_tool.py
│   │   └── verification/         # 검증 도구
│   │       ├── ai_image_detector.py
│   │       └── youtube_video_analyzer.py
│   │
│   ├── core/
│   │   ├── crew.py               # FactWaveCrew 메인 오케스트레이터
│   │   └── streaming_crew.py     # WebSocket 스트리밍 지원
│   │
│   ├── api/
│   │   └── server.py             # FastAPI WebSocket 서버
│   │
│   ├── config/
│   │   └── prompts.yaml          # 중앙화된 프롬프트 관리
│   │
│   └── utils/
│       ├── llm_config.py         # LLM 설정 (GPT-4.1-mini)
│       ├── prompt_loader.py      # 동적 프롬프트 로딩
│       └── websocket_manager.py  # WebSocket 이벤트 관리
│
├── owid_enhanced_vectordb/        # ChromaDB 벡터 데이터베이스
└── owid_datasets/                 # 40+ OWID 데이터셋
```

### 프론트엔드 구조
```
frontend/
├── manifest.json                  # Chrome Extension Manifest V3
├── background.js                  # Service Worker
├── src/
│   ├── App.jsx                   # 메인 앱 컴포넌트
│   ├── components/
│   │   ├── Discussion.jsx        # 토론 탭 (실시간 팩트체킹)
│   │   ├── Results.jsx           # 결과 탭 (검증 결과 표시)
│   │   ├── Library.jsx           # 라이브러리 탭 (저장된 검증)
│   │   ├── LoadingMessage.jsx    # 로딩 애니메이션
│   │   ├── ImageAnalysisResult.jsx
│   │   └── YouTubeThumbnail.jsx
│   └── utils/
│       └── youtube.js             # YouTube 유틸리티
```

## 🛠️ 핵심 구현 세부사항

### 에이전트 시스템
- **기본 클래스**: `FactWaveAgent` - 모든 에이전트의 부모 클래스
- **Step별 LLM**: GPT-4.1-mini 사용, 단계별 온도/토큰 최적화
- **도구 로깅**: 실시간 도구 사용 모니터링 및 결과 추적
- **독립 실행**: Step 1에서 개별 Crew 인스턴스로 독립성 보장

### 연구 도구 특징
- **EnhancedBaseTool**: 모든 도구의 기본 클래스
- **MD5 캐싱**: 도구별 TTL 설정 (학술: 72h, 뉴스: 1h, 소셜: 30m)
- **HTTP 재시도**: 지수 백오프로 안정성 확보
- **속도 제한**: API별 rate limiting 자동 관리
- **우아한 실패**: 도구 실패 시 시스템 중단 없이 계속 진행

### RAG 시스템 (OWID)
- **ChromaDB**: 영구 벡터 저장소
- **40+ 데이터셋**: 기후, 경제, 건강, 교육 등 사전 인덱싱
- **하이브리드 검색**: 벡터 유사도 + BM25 순위
- **메타데이터 필터**: 카테고리, 날짜, 국가별 필터링

### WebSocket 통신 프로토콜
```javascript
// 클라이언트 → 서버
{"action": "start", "statement": "검증할 문장"}

// 서버 → 클라이언트
{
  "type": "task_started|task_completed|agent_analysis|tool_call|final_result",
  "step": "step1|step2|step3",
  "agent": "academic|news|logic|social|statistics|super",
  "content": {...},
  "timestamp": "ISO 8601"
}
```

### 프롬프트 관리 (prompts.yaml)
- **중앙화된 관리**: 모든 에이전트 프롬프트 YAML 파일 관리
- **핫 리로딩**: 시스템 재시작 없이 프롬프트 수정 가능
- **Step별 템플릿**: 단계별 맞춤형 프롬프트
- **판정 옵션**: 13가지 세분화된 판정 카테고리

## 🛠️ 기술 스택

### 백엔드
- **Python 3.12+** / **UV 패키지 관리자**
- **FastAPI** - WebSocket API 서버
- **CrewAI** - 멀티 에이전트 오케스트레이션 프레임워크
- **OpenAI GPT-4.1-mini** - 메인 LLM (모든 Step에서 사용)
- **ChromaDB** - 벡터 데이터베이스 (OWID RAG 시스템)
- **Pydantic** - 구조화된 응답 스키마 검증
- **Rich** - 터미널 UI 및 로깅 시각화

### 프론트엔드
- **React 19.1.0** - 최신 UI 프레임워크
- **Vite** - 차세대 번들러
- **Tailwind CSS** - 유틸리티 기반 스타일링
- **Chrome Extension Manifest V3** - 최신 확장 프로그램 표준
- **Service Worker** - 백그라운드 처리

### 연구 도구 API
- **OpenAlex** - 240M+ 학술 논문 (API키 불필요)
- **ArXiv** - 수학/물리/CS 프리프린트 논문
- **Naver News API** - 한국 뉴스 검색
- **NewsAPI** - 80,000+ 글로벌 언론사
- **Google Fact Check API** - ClaimReview 팩트체크 데이터베이스
- **Wikipedia API** - 다국어 백과사전
- **KOSIS API** - 한국 통계청
- **FRED API** - 미국 연방준비제도 경제 데이터
- **World Bank API** - 세계은행 개발 지표
- **Twitter API (twscrape)** - 소셜 미디어 트렌드

## 🧪 테스트 및 개발

### 테스트 실행
```bash
# WebSocket 클라이언트 테스트
cd backend
python test_websocket_client.py

# 개별 도구 테스트
python tests/test_tavily.py
python tests/test_tool_usage.py
python tests/test_youtube_tool.py

# 유닛 테스트 전체 실행
python -m pytest tests/

# CLI 인터페이스 테스트
python main.py
```

### 개발 워크플로우
```bash
# 백엔드 개발
cd backend
python -m app.api.server  # 포트 8000에서 서버 시작

# 프론트엔드 개발  
cd frontend
npm run dev  # 포트 5173에서 개발 서버 시작
npm run build  # 프로덕션 빌드
npm run build:watch  # 빌드 감시 모드

# 코드 품질 관리
cd backend
ruff check .    # 린팅 검사
ruff format .   # 코드 포매팅
cd frontend
npm run lint    # ESLint 검사
```

### 성능 최적화 팁
- **캐시 관리**: `.cache/` 디렉토리 정기 정리
- **벡터 DB 재구성**: `python build_owid_index.py` (데이터셋 업데이트 시)
- **도구별 TTL**: 학술(72h), 뉴스(1h), 소셜(30m)로 최적화
- **동시 실행**: Step 1에서 5개 에이전트 병렬 처리

## 🌍 사용 시나리오

### 1. 뉴스 기사 검증
**입력**: "2024년 한국 GDP 성장률이 3.2%를 기록했다"
- 📰 **뉴스 에이전트**: 최신 경제 뉴스 검색
- 📊 **통계 에이전트**: KOSIS, FRED 경제 지표 확인
- 🤔 **논리 에이전트**: 수치의 합리성 분석

### 2. 과학적 주장 검증  
**입력**: "비타민 C가 감기를 예방한다는 연구 결과가 발표되었다"
- 📚 **학술 에이전트**: ArXiv, OpenAlex 논문 검색
- 📰 **뉴스 에이전트**: 의학 뉴스 및 팩트체크 결과
- 🤔 **논리 에이전트**: 과학적 방법론 평가

### 3. 소셜 트렌드 검증
**입력**: "최근 젊은층 사이에서 환경 보호 관심이 급증했다"
- 👥 **소셜 에이전트**: Twitter 트렌드 분석
- 📊 **통계 에이전트**: 환경 관련 통계 데이터
- 📰 **뉴스 에이전트**: 환경 관련 보도 현황

## 📊 13가지 판정 카테고리

### ✅ 사실 계열
- **참**: 확실하게 사실 (95-100% 신뢰도)
- **대체로_참**: 대부분 사실 (75-95% 신뢰도)
- **부분적_참**: 일부만 사실 (50-75% 신뢰도)

### ❓ 판단 어려움 계열
- **불확실**: 증거 부족으로 판단 어려움
- **정보부족**: 검증할 충분한 정보 없음
- **논란중**: 전문가들 사이에 의견 분분

### ❌ 거짓 계열
- **부분적_거짓**: 일부가 거짓 (25-50% 거짓)
- **대체로_거짓**: 대부분 거짓 (5-25% 사실)
- **거짓**: 확실하게 거짓 (0-5% 사실)

### ⚠️ 기타 계열
- **과장됨**: 사실이지만 과장된 표현
- **오해소지**: 오해의 여지가 있는 표현
- **맥락오류**: 맥락에서 벗어난 주장
- **시대착오**: 과거에는 맞았지만 현재는 부정확

## 🔑 API 키 설정

### 필수 API 키
```bash
# .env 파일에 추가
OPENAI_API_KEY=your_openai_api_key  # GPT-4.1-mini 사용
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
```

### 선택적 API 키 (고도화 기능)
```bash
# 국제 뉴스 확장
NEWSAPI_KEY=your_newsapi_key

# Google 팩트체크 데이터베이스
GOOGLE_API_KEY=your_google_api_key

# 경제 통계 데이터  
FRED_API_KEY=your_fred_key

# 한국 통계청
KOSIS_API_KEY=your_kosis_key

# 소셜 미디어 분석 (고급 기능)
# Twitter 계정 설정은 TWITTER_ACCOUNTS_GUIDE.md 참조
```

## 📚 추가 문서

- **[CLAUDE.md](./CLAUDE.md)** - Claude Code 개발 가이드
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - 상세 설치 가이드
- **[backend/docs/](./backend/docs/)** - 백엔드 API 문서
- **[backend/TWITTER_ACCOUNTS_GUIDE.md](./backend/TWITTER_ACCOUNTS_GUIDE.md)** - Twitter 계정 설정

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 라이선스

MIT License - [LICENSE](LICENSE) 파일 참조

## 🙏 감사의 말

- [CrewAI](https://crewai.com) - 멀티 에이전트 오케스트레이션
- [OpenAlex](https://openalex.org) - 오픈 학술 논문 데이터베이스  
- [Our World in Data](https://ourworldindata.org) - 글로벌 통계 데이터
- 모든 오픈소스 기여자들

---

**FactWave** - *AI 협업으로 진실을 밝히다* 🌊
