# FactWave 🌊

**AI 기반 실시간 팩트체킹 시스템**

5개의 전문 AI 에이전트가 협력하여 정보를 검증하는 멀티 에이전트 팩트체킹 플랫폼입니다.

## ✨ 주요 특징

- 🤖 **5개 전문 에이전트**: 학술·뉴스·통계·논리·사회 분야별 전문 검증
- ⚡ **실시간 스트리밍**: WebSocket 기반 실시간 분석 과정 표시
- 🎯 **3단계 검증**: 독립분석 → 토론 → 최종종합의 체계적 검증
- 🌐 **웹 인터페이스**: React 기반 직관적인 Chrome Extension UI
- 📊 **구조화된 결과**: JSON 기반 명확한 판정 및 근거 제시

## 🚀 빠른 시작

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd FactWave
```

### 2. 백엔드 설정

```bash
cd backend
uv pip install -e .  # 또는 pip install -e .

# 환경변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정 (UPSTAGE_API_KEY, NAVER_CLIENT_ID 등)
```

### 3. 프론트엔드 설정

```bash
cd frontend_minho
npm install
```

### 4. 실행

**백엔드 서버 (터미널 1):**
```bash
cd backend
uv run python -m app.api.server
```

**프론트엔드 개발 서버 (터미널 2):**
```bash
cd frontend_minho
npm run dev
```

- 백엔드: http://localhost:8000
- 프론트엔드: http://localhost:5173

## 📁 프로젝트 구조

```
FactWave/
├── backend/                    # 백엔드 (Python/FastAPI)
│   ├── app/
│   │   ├── agents/            # AI 에이전트
│   │   ├── api/               # WebSocket API
│   │   ├── config/            # 프롬프트 설정
│   │   ├── core/              # 팩트체킹 엔진
│   │   ├── models/            # 데이터 모델
│   │   ├── services/tools/    # 외부 API 도구들
│   │   └── utils/             # 유틸리티
│   ├── docs/                  # 백엔드 문서
│   ├── owid_datasets/         # 통계 데이터셋
│   ├── tests/                 # 테스트
│   └── main.py               # CLI 인터페이스
├── frontend_minho/             # 프론트엔드 (React/Vite)
│   ├── src/
│   │   ├── App.jsx           # 메인 컴포넌트
│   │   ├── App.css           # 스타일
│   │   └── assets/           # 리소스
│   ├── public/               # Chrome Extension 설정
│   └── package.json
├── FRONTEND_API_GUIDE.md      # 프론트엔드 개발 가이드
├── CLAUDE.md                  # Claude Code 가이드
└── README.md                  # 이 파일
```

## 🤖 AI 에이전트 시스템

| 에이전트 | 역할 | 가중치 | 전문 도구 |
|----------|------|--------|-----------|
| 🎓 **Academic** | 학술 연구 검증 | 25% | Wikipedia, ArXiv, OpenAlex |
| 📰 **News** | 뉴스 미디어 검증 | 30% | Naver News, NewsAPI, Google Fact Check |
| 📊 **Statistics** | 통계 데이터 검증 | 20% | KOSIS, FRED, World Bank, OWID |
| 🤔 **Logic** | 논리적 일관성 분석 | 15% | 논리 추론 |
| 👥 **Social** | 사회적 맥락 분석 | 10% | Twitter API |

### 3단계 검증 프로세스

1. **독립 분석**: 각 에이전트가 독립적으로 검증
2. **구조화된 토론**: 에이전트들이 결과를 검토하고 토론
3. **최종 종합**: 가중치 기반 종합 판정

## 🛠️ 기술 스택

### 백엔드
- **Python 3.12+** - 메인 언어
- **FastAPI** - WebSocket API 서버
- **CrewAI** - 멀티 에이전트 오케스트레이션
- **Upstage Solar-pro2** - 메인 LLM
- **ChromaDB** - 벡터 데이터베이스 (OWID RAG)
- **Pydantic** - 구조화된 응답 검증

### 프론트엔드
- **React 19** - UI 프레임워크
- **Vite** - 빌드 툴
- **Chrome Extension** - 브라우저 확장
- **WebSocket** - 실시간 통신

### 외부 API
- **Naver News API** - 한국 뉴스 검색
- **NewsAPI** - 글로벌 뉴스
- **Google Fact Check API** - 팩트체크 DB
- **Wikipedia API** - 백과사전
- **ArXiv API** - 학술 논문
- **KOSIS API** - 한국 통계
- **FRED API** - 미국 경제 통계
- **World Bank API** - 세계 통계
- **Twitter API** - 소셜 트렌드

## 📚 개발 가이드

### 프론트엔드 개발자
👉 **[FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)** - WebSocket API 사용법

### 백엔드 개발자  
👉 **[backend/docs/](./backend/docs/)** - 상세 백엔드 가이드

### Claude Code 사용자
👉 **[CLAUDE.md](./CLAUDE.md)** - 개발 환경 및 명령어

## 🧪 테스트

```bash
# 개별 도구 테스트
cd backend && uv run python test_integrated.py tools wikipedia

# 전체 시스템 테스트
cd backend && uv run python test_integrated.py crew "테스트 문장"

# CLI 버전 실행
cd backend && uv run python main.py
```

## 🔧 주요 명령어

```bash
# 백엔드 서버 실행
cd backend && uv run python -m app.api.server

# 프론트엔드 개발 서버
cd frontend_minho && npm run dev

# 프론트엔드 빌드
cd frontend_minho && npm run build

# 코드 품질 체크
cd backend && ruff check .
cd backend && ruff format .
```

## 🌍 사용 예시

1. **Chrome Extension 설치**: `frontend_minho/` 폴더를 Chrome 개발자 모드로 로드
2. **백엔드 서버 실행**: 포트 8000에서 실행
3. **팩트체킹 요청**: 확장 프로그램에서 검증하고 싶은 문장 입력
4. **실시간 결과 확인**: 5개 에이전트의 분석 과정과 최종 판정 확인

## 📊 판정 유형

- `참` / `대체로_참` / `부분적_참` - 사실
- `불확실` / `정보부족` / `논란중` - 판단 어려움  
- `부분적_거짓` / `대체로_거짓` / `거짓` - 거짓
- `과장됨` / `오해소지` / `시대착오` - 기타

## 🔑 API 키 설정

`backend/.env` 파일:

```bash
# 필수
UPSTAGE_API_KEY=your_upstage_api_key
NAVER_CLIENT_ID=your_naver_client_id  
NAVER_CLIENT_SECRET=your_naver_client_secret

# 선택 (기능 확장)
NEWSAPI_KEY=your_newsapi_key
GOOGLE_FACT_CHECK_KEY=your_google_key
FRED_API_KEY=your_fred_key
TWITTER_BEARER_TOKEN=your_twitter_token
```
