# Academic Agent Tools Documentation

## Overview
Academic Agent는 학술적 팩트체킹을 위해 다양한 연구 도구를 사용합니다. 모든 도구는 **무료**로 사용 가능하며, API 키가 필요하지 않습니다.

## 현재 구현된 도구

### 1. Wikipedia Search Tool 📚

**설명**: 일반적인 배경 지식과 정의를 검색하는 도구

**API 정보**:
- **키 필요 여부**: ❌ 불필요
- **요청 제한**: 시간당 5,000회
- **지원 언어**: 한국어(ko), 영어(en) 등 300+ 언어
- **공식 문서**: https://www.mediawiki.org/wiki/API:Main_page

**주요 기능**:
- 페이지 요약 정보 추출
- 관련 섹션 목록 제공
- 다국어 검색 지원
- 유사 페이지 자동 검색

**사용 예시**:
```python
# 한국어 검색
result = wikipedia_search("인공지능", lang="ko")

# 영어 검색
result = wikipedia_search("quantum computing", lang="en")
```

### 2. Semantic Scholar Search Tool 🎓

**설명**: 214M+ 학술 논문을 검색하고 AI 요약을 제공하는 도구

**API 정보**:
- **키 필요 여부**: ❌ 불필요
- **요청 제한**: 분당 100회
- **데이터베이스 크기**: 2억 1400만+ 논문
- **공식 문서**: https://api.semanticscholar.org/

**주요 기능**:
- 논문 제목, 저자, 초록 검색
- 인용 수 확인
- AI 생성 TL;DR (요약) 제공
- 연도별 필터링
- 오픈 액세스 PDF 링크 제공

**특별 기능**:
- **SPECTER2 임베딩**: 의미 기반 유사 논문 검색
- **영향력 점수**: 논문의 학술적 영향력 측정
- **분야별 검색**: CS, 의학, 물리학 등 세분화된 검색

**사용 예시**:
```python
# 기본 검색
result = semantic_scholar_search("transformer neural network", limit=5)

# 연도 필터링
result = semantic_scholar_search("GPT-4", limit=5, year_filter="2023-2024")
```

### 3. ArXiv Search Tool 📄

**설명**: CS, 물리, 수학 분야의 프리프린트 논문 검색 도구

**API 정보**:
- **키 필요 여부**: ❌ 불필요
- **요청 제한**: 매우 관대함 (초당 3회 권장)
- **주요 분야**: CS, Physics, Math, Stats, Q-Bio, Q-Fin
- **공식 문서**: https://arxiv.org/help/api/

**주요 기능**:
- 최신 연구 논문 검색
- PDF 다이렉트 다운로드 링크
- 정렬 옵션 (관련성, 날짜순)
- 카테고리별 필터링
- 버전 히스토리 추적

**사용 예시**:
```python
# 관련성 기준 검색
result = arxiv_search("large language models", max_results=5)

# 최신순 검색
result = arxiv_search("quantum ML", max_results=5, sort_by="submittedDate")
```

## 추가 구현 가능한 학술 API

### 4. PubMed API (의학/생명과학) 🏥

**설명**: 의학 및 생명과학 분야 3300만+ 논문 검색

**API 정보**:
- **키 필요 여부**: ⚠️ 선택적 (키 없이도 사용 가능, 키 있으면 더 많은 요청)
- **요청 제한**: 
  - 키 없음: 초당 3회
  - 키 있음: 초당 10회
- **API 키 신청**: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
- **공식 문서**: https://www.ncbi.nlm.nih.gov/books/NBK25501/

**특징**:
- MeSH (Medical Subject Headings) 용어 검색
- 임상시험 데이터 연동
- 전문(Full Text) 링크 제공

### 5. Crossref API (DOI 메타데이터) 🔗

**설명**: 1.5억+ 학술 자료의 DOI 기반 메타데이터 검색

**API 정보**:
- **키 필요 여부**: ❌ 불필요 (Polite Pool 권장)
- **요청 제한**: 초당 50회
- **Polite Pool**: mailto 헤더 추가 시 우선순위 큐
- **공식 문서**: https://github.com/CrossRef/rest-api-doc

**특징**:
- DOI로 정확한 논문 검색
- 참고문헌 네트워크 분석
- 출판사 정보 제공
- 펀딩 정보 추적

### 6. OpenAlex API (구 Microsoft Academic) 📊

**설명**: 2억+ 학술 논문의 오픈 메타데이터

**API 정보**:
- **키 필요 여부**: ❌ 불필요
- **요청 제한**: 초당 10회 (Polite Pool: 초당 50회)
- **공식 문서**: https://docs.openalex.org/

**특징**:
- 저자 프로필 및 h-index
- 기관별 연구 성과 분석
- 주제 분류 및 트렌드 분석
- 오픈 액세스 상태 확인

### 7. CORE API (오픈 액세스 논문) 🌐

**설명**: 2억 5천만+ 오픈 액세스 논문 전문 검색

**API 정보**:
- **키 필요 여부**: ✅ 필요 (무료 등록)
- **요청 제한**: 
  - 무료: 일일 1,000회
  - 유료: 무제한
- **API 키 신청**: https://core.ac.uk/services/api
- **공식 문서**: https://api.core.ac.uk/docs/v3

**특징**:
- 논문 전문(Full Text) 검색
- 다국어 지원
- 기관 리포지토리 통합

## API 사용 시 주의사항

### Rate Limiting
각 API의 요청 제한을 준수해야 합니다:
- Wikipedia: 5,000회/시간
- Semantic Scholar: 100회/분
- ArXiv: 3회/초 권장

### User-Agent 설정
모든 API 요청에 적절한 User-Agent를 설정해야 합니다:
```python
headers = {
    "User-Agent": "FactWave/1.0 (https://factwave.ai; contact@factwave.ai)"
}
```

### 캐싱 전략
PRD에 따른 캐싱 권장사항:
- Academic 데이터: TTL 1시간 (논문은 변하지 않음)
- 중복 검색 방지: 24시간 캐시

### 에러 처리
- 네트워크 오류 시 재시도 (최대 3회)
- Rate limit 초과 시 대기 후 재시도
- API 다운타임 대비 폴백 전략

## 구현 로드맵

1. **Phase 1** (현재 완료) ✅
   - Wikipedia Search Tool
   - Semantic Scholar Tool
   - ArXiv Tool

2. **Phase 2** (계획 중)
   - PubMed API 통합
   - Crossref API 통합
   - 캐싱 시스템 구현

3. **Phase 3** (향후)
   - OpenAlex API 통합
   - CORE API 통합 (키 필요)
   - 한국 학술 DB 연동 (RISS, DBpia 등)

## 한국 학술 데이터베이스 (향후 구현)

### RISS (학술연구정보서비스)
- **제공처**: 한국교육학술정보원(KERIS)
- **API 키**: 필요 (무료 신청)
- **특징**: 국내 학위논문, 학술지 논문

### KCI (한국학술지인용색인)
- **제공처**: 한국연구재단
- **API 키**: 필요 (기관 인증)
- **특징**: 국내 학술지 영향력 지수

### DBpia
- **제공처**: 누리미디어
- **API 키**: 필요 (유료)
- **특징**: 국내 학술지 전문

## 성능 최적화 팁

1. **병렬 요청**: 여러 API를 동시에 호출하여 응답 시간 단축
2. **조기 종료**: 충분한 증거를 찾으면 추가 검색 중단
3. **스마트 쿼리**: 동의어 및 관련 용어로 검색 확장
4. **결과 중복 제거**: 여러 API에서 동일한 논문 제거

## 문제 해결

### Wikipedia API 한글 검색 오류
- URL 인코딩 확인
- 언어 코드 정확히 지정 (ko, not kr)

### Semantic Scholar 느린 응답
- 필드 파라미터로 필요한 데이터만 요청
- 대량 검색 시 배치 처리

### ArXiv 검색 결과 없음
- 카테고리 지정 검색 (cs.AI, physics.quant-ph 등)
- 검색어를 영어로 변환

## 참고 자료

- [Wikipedia API Tutorial](https://www.mediawiki.org/wiki/API:Tutorial)
- [Semantic Scholar API Guide](https://api.semanticscholar.org/api-guide/)
- [ArXiv API User Manual](https://arxiv.org/help/api/user-manual)
- [Academic API Comparison](https://github.com/scholarly/scholarly-api-comparison)