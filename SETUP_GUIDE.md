# FactWave 설치 및 실행 가이드

## 필수 요구사항
- Python 3.12 이상
- Node.js 18 이상
- Git

## 빠른 시작

### 1. 저장소 클론
```bash
git clone [repository-url]
cd factwave
```

### 자동 설치 (권장)

Windows에서 모든 의존성을 자동으로 설치하려면:

```bash
# PowerShell에서 실행
cd backend
pip install fastapi uvicorn pydantic python-dotenv rich pyyaml requests httpx beautifulsoup4 openai anthropic arxiv wikipedia-api pandas numpy nltk crewai --no-deps json_repair langchain-text-splitters langchain-core tenacity langchain-openai appdirs blinker instructor json5 jsonref openpyxl opentelemetry-api opentelemetry-exporter-otlp-proto-http opentelemetry-sdk pyjwt pyvis tomli tomli-w portalocker==2.7.0 chromadb PublicDataReader websockets python-multipart

# 버전 호환성 문제 해결
pip install "json-repair==0.25.2" "onnxruntime==1.22.0" "openai<1.100.0" --force-reinstall

# .env 파일 생성
cp .env.example .env

# 프론트엔드 설정
cd ../frontend
npm install
```

### 수동 설치 (문제 발생 시)

### 2. 백엔드 설정

#### 2.1 Python 패키지 설치

**중요**: pyproject.toml의 패키지 구조 문제로 인해 의존성을 직접 설치해야 합니다.

```bash
cd backend

# 1. 핵심 패키지 먼저 설치
pip install fastapi uvicorn pydantic python-dotenv rich pyyaml requests httpx beautifulsoup4 openai anthropic arxiv wikipedia-api pandas numpy nltk

# 2. CrewAI 관련 패키지 설치
pip install crewai --no-deps
pip install json_repair langchain-text-splitters langchain-core tenacity
pip install langchain-openai

# 3. 필수 의존성 설치
pip install appdirs blinker instructor json5 jsonref openpyxl opentelemetry-api opentelemetry-exporter-otlp-proto-http opentelemetry-sdk pyjwt pyvis tomli tomli-w portalocker==2.7.0

# 4. 데이터베이스 및 벡터 검색
pip install chromadb

# 5. 한국 공공데이터 API
pip install PublicDataReader

# 6. 버전 호환성 문제 해결
pip install "json-repair==0.25.2" "onnxruntime==1.22.0" "openai<1.100.0" --force-reinstall

# 7. WebSocket 지원
pip install websockets python-multipart
```

**대안 (UV 사용 시):**
```bash
cd backend
uv pip install fastapi uvicorn pydantic python-dotenv rich pyyaml requests httpx beautifulsoup4 openai anthropic arxiv wikipedia-api pandas numpy nltk crewai chromadb PublicDataReader langchain-openai langchain-core tenacity websockets python-multipart
```

#### 2.2 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env
```

`.env` 파일을 열어 필수 API 키 입력:
- `UPSTAGE_API_KEY`: Upstage Solar API 키 (필수)
- `NAVER_CLIENT_ID` & `NAVER_CLIENT_SECRET`: 네이버 개발자 API (필수)

#### 2.3 선택적 패키지 설치 (기능 향상)

**주의**: 다음 패키지들은 선택사항이지만 전체 기능을 위해 권장됩니다.

```bash
# OWID RAG 시스템 및 소셜 미디어 분석 (대용량 패키지)
pip install sentence-transformers rank-bm25 twscrape

# 또는 필요한 것만 선택 설치
pip install sentence-transformers  # OWID 통계 데이터 검색 향상
pip install rank-bm25             # 검색 랭킹 개선
pip install twscrape              # 트위터/X 소셜 미디어 분석
```

#### 2.4 백엔드 서버 실행
```bash
# backend 폴더에서
python -m app.api.server
# 또는
uv run python -m app.api.server
```
서버가 `http://localhost:8000`에서 실행됩니다.

**실행 확인**: 브라우저에서 `http://localhost:8000`에 접속하여 "FactWave API Server"가 표시되는지 확인하세요.

### 3. 프론트엔드 설정

#### 3.1 새 터미널 열기 및 패키지 설치
```bash
cd frontend
npm install
```

#### 3.2 환경 변수 설정 (선택사항)
```bash
# 기본값(localhost:8000)과 다른 백엔드 주소를 사용할 경우
cp .env.example .env
# .env 파일에서 VITE_WS_URL 수정
```

#### 3.3 개발 서버 실행
```bash
npm run dev
```
프론트엔드가 `http://localhost:5173`에서 실행됩니다.

### 4. 크롬 익스텐션으로 사용

#### 4.1 프로덕션 빌드
```bash
cd frontend
npm run build
```

#### 4.2 크롬에서 로드
1. Chrome 브라우저에서 `chrome://extensions` 접속
2. 우측 상단 "개발자 모드" 활성화
3. "압축 해제된 확장 프로그램 로드" 클릭
4. `frontend/dist` 폴더 선택

## 문제 해결

### 백엔드 실행 실패

#### ModuleNotFoundError 오류
```
ModuleNotFoundError: No module named 'crewai'
ModuleNotFoundError: No module named 'chromadb'
ModuleNotFoundError: No module named 'langchain_openai'
```
**해결방법**: 2.1단계의 패키지 설치를 모두 완료했는지 확인하세요.

#### Microsoft Visual C++ Build Tools 오류 (Windows)
```
error: Microsoft Visual C++ 14.0 or greater is required
```
**해결방법**: 
1. https://visualstudio.microsoft.com/visual-cpp-build-tools/ 에서 Build Tools 다운로드
2. 설치 후 `pip install chromadb` 재실행

#### 패키지 버전 충돌 오류
```
ERROR: pip's dependency resolver does not currently take into account...
```
**해결방법**: 단계별로 패키지를 설치하고, 필요시 `--force-reinstall` 옵션 사용

### 백엔드 연결 실패
- 백엔드 서버가 실행 중인지 확인 (`http://localhost:8000`)
- 방화벽이 8000 포트를 차단하지 않는지 확인
- `.env` 파일에 필수 API 키가 설정되었는지 확인

### 이미지가 표시되지 않음
- `frontend/public/img/agent_icons/` 폴더에 다음 파일들이 있는지 확인:
  - academic.png
  - logic.png
  - news.png
  - social.png
  - statistics.png

### API 키 관련 오류
필수 API 키:
- **Upstage Solar**: https://console.upstage.ai/ 에서 발급
- **Naver API**: https://developers.naver.com/apps 에서 발급

선택 API 키 (기능 향상용):
- NewsAPI: https://newsapi.org
- Google Fact Check: Google Cloud Console
- FRED: https://fred.stlouisfed.org/docs/api/api_key.html
- KOSIS: https://kosis.kr/openapi/

## 테스트

### 백엔드 테스트
```bash
cd backend

# 개별 도구 테스트
python test_integrated.py tools wikipedia
python test_integrated.py tools naver_news

# 전체 시스템 테스트
python test_integrated.py crew "테스트할 문장"
```

### WebSocket 연결 테스트
```bash
cd backend
python test_websocket_client.py
```

## 주의사항
- 백엔드 서버를 먼저 실행한 후 프론트엔드를 실행하세요
- Windows에서는 파일 경로에 공백이 있으면 문제가 발생할 수 있습니다
- API 키는 절대 Git에 커밋하지 마세요 (`.env` 파일은 `.gitignore`에 포함됨)