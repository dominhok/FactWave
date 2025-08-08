# 통계 도구 상세 가이드

## KOSIS (한국 통계청)

### 개요
- **API**: PublicDataReader 라이브러리 사용
- **데이터 소스**: 통계청 국가통계포털(KOSIS)
- **지원 언어**: 한국어 자연어 검색

### 검색 과정
1. KOSIS 통합검색 API로 자연어 쿼리 전송
2. 검색 결과에서 통계표 ID와 기관 ID 추출
3. 통계자료 API로 실제 데이터 조회
4. 시계열 데이터 파싱 및 구조화

### 주요 파라미터
- `searchNm`: 검색어 (예: "실업률", "GDP")
- `orgId`: 기관ID (101: 통계청, 301: 한국은행)
- `tblId`: 통계표ID
- `prdSe`: 기간구분 ("Y": 연간, "M": 월간)
- `newEstPrdCnt`: 최근 N개 시점

### 출력 형식
```
📊 KOSIS 통계 검색 결과: '실업률'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: 통계청 국가통계포털(KOSIS)
📊 발견된 통계표: 5개

📈 [1] 경제활동인구조사 실업률
────────────────────────────────────────
🏛️  제공기관: 통계청
📋  테이블ID: DT_1DA7102S
📊 실제 통계 데이터:
  📁 데이터 메타데이터:
    • 기관ID: 101
    • 통계표명: 경제활동인구조사 실업률
    • 분류값명1: 전체
    • 단위명: %
    • 수록시점: 2024
    • 수치값: 2.7
```

## FRED (미국 연준)

### 개요
- **API**: Federal Reserve Economic Data API
- **접근 방법**: 직접 REST API 호출
- **지원 언어**: 영어 자연어 검색

### 검색 과정
1. series/search API로 시계열 검색
2. 인기도 순으로 정렬된 결과 받기
3. series/observations API로 데이터 조회
4. 시계열 데이터 구조화

### 주요 파라미터
- `search_text`: 검색어
- `series_id`: 시계열 ID (예: UNRATE, GDP)
- `order_by`: 정렬 기준 (popularity)
- `limit`: 결과 개수

### 출력 형식
```
📊 FRED 경제 데이터 검색: 'unemployment'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: 미국 연방준비은행(Federal Reserve Bank)
📊 발견된 시계열: 3개

📈 [1] Unemployment Rate
────────────────────────────────────────
  📋 id: UNRATE
  📋 title: Unemployment Rate
  📋 units: Percent
  📋 frequency: Monthly
  📋 seasonal_adjustment: Seasonally Adjusted
  📋 observation_start: 1948-01-01
  📋 observation_end: 2024-11-01

📊 시계열 데이터:
  📅 최근 5개 데이터포인트:
    📅 관측 데이터:
      date: 2024-11-01
      value: 4.1
      realtime_start: 2024-12-06
      realtime_end: 9999-12-31
```

## World Bank (세계은행)

### 개요
- **API**: World Bank WDI API
- **접근 방법**: 직접 REST API 호출 + 지표 매핑
- **지원 언어**: 영어 자연어 검색

### 검색 과정
1. 로컬 지표 매핑(wdi2name.json)에서 키워드 매칭
2. 매칭 점수 계산 및 정렬
3. country/indicator API로 데이터 조회
4. 국가별 시계열 데이터 구조화

### 주요 파라미터
- `indicator_code`: WDI 지표 코드 (예: NY.GDP.MKTP.KD.ZG)
- `country`: 국가 코드 (ISO 2자리, 예: KR)
- `date`: 기간 범위
- `format`: 응답 형식 (json)

### 출력 형식
```
📊 World Bank WDI 검색 결과: 'GDP growth'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: 세계은행(World Bank) - World Development Indicators
📊 발견된 지표: 3개

📈 [1] GDP growth (annual %)
────────────────────────────────────────
  📋 지표코드: NY.GDP.MKTP.KD.ZG
  📋 관련도: 100%
  📋 대상국가: KR

📊 지표 데이터:
  📅 최근 3개 데이터포인트:
    📊 데이터 항목:
      indicator:
        id: NY.GDP.MKTP.KD.ZG
        value: GDP growth (annual %)
      country:
        id: KR
        value: Korea, Rep.
      countryiso3code: KOR
      date: 2023
      value: 3.1
      unit: 
      obs_status: 
      decimal: 1
```

## OWID (Our World in Data)

### 개요
- **시스템**: 향상된 RAG 시스템
- **데이터 소스**: 38개 OWID 데이터셋
- **지원 언어**: 한국어/영어 자연어 검색

### 주요 기능
- 다국어 임베딩 (Korean + English)
- 하이브리드 검색 (Vector + BM25)
- Cross-encoder 재순위화
- 통계 데이터 최적화된 청킹

### 출력 형식
```
📊 OWID 통계 검색 결과: 'Korea GDP'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: Our World in Data
📊 발견된 결과: 2개

📈 [1] OWID 데이터
────────────────────────────────────────
📁 검색 결과 메타데이터:
  📋 dataset_id: gdp-growth
  📋 chunk_type: overview
  📋 score: 4.2
  📋 metadata:
    year: 2023
    country: Korea

📊 원본 데이터:
  South Korea's GDP growth has averaged 3.1% annually over the past decade
  Latest GDP figures show continued recovery post-pandemic
  Key drivers include technology exports and domestic consumption
```

## 공통 개선사항

### 1. 메타데이터 완전 보존
- ✅ 모든 API 필드를 변경 없이 전달
- ✅ 룰베이스 변환 제거 (단위 변환, 포맷팅 등)
- ✅ 중첩 객체까지 완전 표시

### 2. 구조화된 출력
- ✅ 일관된 이모지 기반 구조
- ✅ 명확한 출처 표시
- ✅ 계층적 정보 배치

### 3. LLM 친화적 설계
- ✅ 팩트체킹에 필요한 모든 컨텍스트 제공
- ✅ 원본 데이터 보존으로 판단 근거 명확화
- ✅ 구조화된 형식으로 파싱 용이성 확보