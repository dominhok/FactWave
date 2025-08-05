# FactWave

**AI-Powered Multi-Agent Fact-Checking System**

FactWave는 5개의 전문 AI 에이전트가 협력하여 정보를 검증하는 팩트체킹 시스템입니다.

## 🚀 Quick Start

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd FactWave

# 의존성 설치 (UV 권장)
uv pip install -e .
# 또는 pip install -e .

# 환경변수 설정
cp .env.example .env
# .env 파일에서 API 키 설정
```

### 2. API 키 설정 (.env 파일)
```bash
# 필수: AI 모델 API 키
UPSTAGE_API_KEY=your_upstage_api_key_here

# 필수: 한국 뉴스 검색용  
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
```

### 3. 실행
```bash
# 메인 애플리케이션 실행
uv run python main.py

# 도구 테스트
uv run python test_integrated.py tools

# 전체 시스템 테스트  
uv run python test_integrated.py crew
```

## 🤖 Multi-Agent Architecture

| Agent | 가중치 | 역할 | 사용 도구 |
|-------|-------|------|----------|
| **Academic Agent** | 30% | 학술 자료 검증 | Wikipedia, Semantic Scholar, ArXiv, Global Statistics |
| **News Verification Agent** | 35% | 언론 보도 교차 검증 | Naver News, 기타 뉴스 API |
| **Logic Verification Agent** | 20% | 논리적 일관성 분석 | 알고리즘 분석 |
| **Social Intelligence Agent** | 15% | 사회적 맥락 분석 | 소셜미디어 API |
| **Super Agent** | - | 종합 판단 및 신뢰도 매트릭스 생성 | 모든 에이전트 결과 통합 |

## 🔧 Available Research Tools

### Academic Research
- **Wikipedia Search**: 배경 정보 및 정의
- **Semantic Scholar**: 214M+ 학술 논문 검색  
- **ArXiv**: 최신 연구 논문
- **Global Statistics**: World Bank 경제/사회 통계

### News & Media
- **Naver News**: 한국 언론 보도 검색
- **Media Bias Detection**: 언론사별 편향 분석

### Data Sources (API Key 불필요)
- Wikipedia API
- Semantic Scholar API
- ArXiv API  
- World Bank Open Data

## 🎯 Usage Examples

### Command Line Interface
```bash
$ uv run python main.py
🔍 FactWave - AI Fact-Checking System

Enter a statement to verify:
> 2024년 한국의 합계출산율이 0.7명이다

🤖 Academic Agent: 통계청 자료 검증 중...
📰 News Agent: 언론 보도 교차 확인 중...  
🧠 Logic Agent: 수치 논리성 분석 중...
👥 Social Agent: 사회적 맥락 분석 중...
⭐ Super Agent: 종합 판단 중...

📊 Fact-Check Result:
✅ TRUE (신뢰도: 92%)
- 2024년 3분기 한국 합계출산율 0.70명 (통계청)
- 여러 언론사에서 동일하게 보도
- OECD 최하위 수준으로 논리적으로 일관성 있음
```

### API Integration
```python
from app.core.crew import FactWaveCrew

crew = FactWaveCrew()
result = crew.check_fact("GPT-4는 2023년 3월에 출시되었다")
print(result)
```

## 🛠 Development

### Project Structure
```
FactWave/
├── app/
│   ├── agents/          # AI 에이전트 구현
│   ├── services/tools/  # 연구 도구들
│   ├── core/           # CrewAI 설정
│   └── api/            # FastAPI 엔드포인트
├── tests/              # 테스트 파일
├── docs/               # 문서
└── main.py            # 메인 실행 파일
```

### Testing
```bash
# 개별 도구 테스트
uv run python test_integrated.py tools

# 전체 시스템 테스트
uv run python test_integrated.py crew

# 특정 도구 테스트
python -c "from app.services.tools import GlobalStatisticsTool; print('OK')"
```

### Code Quality
```bash
# 린팅
ruff check .

# 포맷팅  
ruff format .
```

## 📋 Requirements

### Minimum Requirements
- Python 3.12+
- UPSTAGE API Key (Solar-pro2 LLM)
- NAVER API Key (한국 뉴스 검색)

### Optional APIs  
- Anthropic Claude API (대체 LLM)
- OpenAI API (추가 모델 지원)

### System Dependencies
- UV package manager (권장)
- Git

## 🔍 Core Features

- **3단계 검증 프로세스**: 초기 분석 → 에이전트 간 토론 → 최종 종합
- **실시간 스트리밍**: WebSocket 기반 실시간 결과 업데이트  
- **다국어 지원**: 한국어/영어 질의 처리
- **신뢰도 매트릭스**: 각 에이전트 가중치 기반 종합 신뢰도 계산
- **캐싱 시스템**: Redis 기반 검색 결과 캐싱 (선택사항)