# 도구 테스트 시스템

## 테스트 개요

FactWave의 모든 10개 도구를 검증하기 위한 통합 테스트 시스템입니다.

### 테스트 파일
- `test_tools.py`: 전체 도구 통합 테스트

## 테스트 대상 도구

### 📊 통계 도구 (4개)
1. **KOSIS** - 한국 통계청
   - 테스트 쿼리: "실업률"
   - 파라미터: `{"query": "실업률", "limit": 1, "fetch_data": True}`

2. **FRED** - 미국 연준
   - 테스트 쿼리: "unemployment"
   - 파라미터: `{"query": "unemployment", "fetch_data": True, "limit": 3}`

3. **WorldBank** - 세계은행
   - 테스트 쿼리: "GDP growth"
   - 파라미터: `{"query": "GDP growth", "country": "KR", "fetch_data": True, "years": 3}`

4. **OWID** - Our World in Data
   - 테스트 쿼리: "Korea GDP"
   - 파라미터: `{"query": "Korea GDP", "n_results": 2, "use_reranker": True}`

### 🎓 학술 도구 (3개)
1. **ArXiv** - 논문 검색
   - 테스트 쿼리: "machine learning"
   - 파라미터: `{"query": "machine learning", "max_results": 1, "sort_by": "relevance"}`

2. **OpenAlex** - 학술 데이터
   - 테스트 쿼리: "AI"
   - 파라미터: `{"query": "AI", "limit": 1, "year_from": 2023}`

3. **Wikipedia** - 위키피디아
   - 테스트 쿼리: "인공지능"
   - 파라미터: `{"query": "인공지능", "lang": "ko"}`

### 📰 뉴스 도구 (3개)
1. **Naver News** - 네이버 뉴스
   - 테스트 쿼리: "경제"
   - 파라미터: `{"query": "경제", "sort": "sim", "display": 1, "start": 1}`

2. **NewsAPI** - 글로벌 뉴스
   - 테스트 쿼리: "technology"
   - 파라미터: `{"query": "technology", "language": "en", "page_size": 1}`

3. **Google Fact Check** - 구글 팩트체크
   - 테스트 쿼리: "climate change"
   - 파라미터: `{"query": "climate change", "language": "en"}`

## 테스트 결과 분석

### 성공 기준
- ✅ 도구가 오류 없이 실행됨
- ✅ 결과 데이터 반환됨
- ✅ 예외 처리 정상 작동

### 분석 메트릭
- **출력 길이**: 문자 수 측정 (예: 1,234자)
- **데이터 포함**: 숫자 데이터 존재 여부
- **메타데이터**: 구조화된 메타데이터 포함 여부
- **미리보기**: 처음 300자 샘플 표시

### 예시 출력
```
============================================================
🔧 KOSIS 통계청
============================================================
✅ 성공 - 2,156자
🔢 데이터: 있음
📁 메타데이터: 있음

📄 출력:
📊 KOSIS 통계 검색 결과: '실업률'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: 통계청 국가통계포털(KOSIS)
📊 발견된 통계표: 20개

📈 [1] 경제활동인구조사 실업률
────────────────────────────────────────...
```

## 실행 방법

```bash
# 전체 도구 테스트 실행
uv run test_tools.py

# 또는
python test_tools.py
```

## 최종 결과 형식

```
📊 최종 결과
======================================================================
✅ 성공: 8/10 (80.0%)
❌ 실패: 2/10

📈 카테고리별:
  통계 도구: 4개 (KOSIS, FRED, WorldBank, OWID)
  학술 도구: 3개 (ArXiv, OpenAlex, Wikipedia)  
  뉴스 도구: 3개 (Naver, NewsAPI, GoogleFC)
```

## 테스트 환경 요구사항

### API 키 설정 (.env 파일)
```env
# 통계 도구
KOSIS_API_KEY=your_kosis_key
FRED_API_KEY=your_fred_key

# 뉴스 도구  
NAVER_CLIENT_ID=your_naver_id
NAVER_CLIENT_SECRET=your_naver_secret
NEWS_API_KEY=your_newsapi_key
GOOGLE_FACTCHECK_API_KEY=your_google_key

# 기타
ANTHROPIC_API_KEY=your_anthropic_key
```

### 의존성 패키지
- `requests`: HTTP 요청
- `pandas`: 데이터 처리 (KOSIS)
- `wikipedia-api`: 위키피디아 검색
- `arxiv`: ArXiv 논문 검색
- `chromadb`: OWID RAG 시스템
- `sentence-transformers`: 임베딩 생성
- `rank-bm25`: BM25 검색
- `PublicDataReader`: KOSIS API 접근

## 문제 해결

### 자주 발생하는 문제
1. **API 키 오류**: `.env` 파일 설정 확인
2. **의존성 누락**: `uv pip install` 실행
3. **네트워크 오류**: 인터넷 연결 및 방화벽 확인
4. **데이터 없음**: API 쿼리나 파라미터 확인

### 디버깅 팁
- 개별 도구 테스트: 각 도구 클래스를 직접 인스턴스화하여 테스트
- 로그 확인: 예외 메시지와 스택 트레이스 분석
- API 응답 검증: 실제 API 응답 형식 확인