# 학술 및 뉴스 도구 가이드

## 🎓 학술 도구

### ArXiv 논문 검색

#### 개요
- **API**: arXiv API
- **데이터**: 논문 메타데이터 및 초록
- **지원**: 영어 자연어 검색

#### 주요 파라미터
- `query`: 검색어 (예: "machine learning", "climate change")
- `max_results`: 최대 결과 수 (기본값: 10)
- `sort_by`: 정렬 기준 (relevance, lastUpdatedDate, submittedDate)

#### 출력 예시
```
📊 ArXiv 검색 결과: 'machine learning'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: arXiv.org
📊 발견된 논문: 5개

📈 [1] Attention Is All You Need
────────────────────────────────────────
📋 arXiv ID: 1706.03762
📋 제목: Attention Is All You Need
📋 저자: Ashish Vaswani, Noam Shazeer, Niki Parmar...
📋 발행일: 2017-06-12
📋 카테고리: cs.CL, cs.AI, cs.LG
📋 링크: http://arxiv.org/abs/1706.03762

📄 초록:
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and decoder. The best performing models also connect the encoder and decoder through an attention mechanism...
```

### OpenAlex 학술 데이터

#### 개요
- **API**: OpenAlex API  
- **데이터**: 2억+ 학술 논문 메타데이터
- **지원**: 영어 자연어 검색

#### 주요 파라미터
- `query`: 검색어
- `limit`: 결과 개수 (기본값: 10)
- `year_from`: 시작 연도
- `sort`: 정렬 기준 (relevance, cited_by_count, publication_date)

#### 출력 예시
```
📊 OpenAlex 검색 결과: 'artificial intelligence'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: OpenAlex
📊 발견된 논문: 3개

📈 [1] Deep Learning for Medical Image Analysis
────────────────────────────────────────
📋 OpenAlex ID: W2963094952
📋 제목: Deep Learning for Medical Image Analysis
📋 저자: Li Zhang, Sarah Johnson, Michael Chen
📋 발행일: 2023-03-15
📋 저널: Nature Machine Intelligence
📋 인용 횟수: 127
📋 DOI: 10.1038/s42256-023-00234-5

📄 요약:
This comprehensive review examines the application of deep learning techniques in medical image analysis, covering recent advances in convolutional neural networks...
```

### Wikipedia 검색

#### 개요
- **API**: Wikipedia API
- **데이터**: 위키피디아 문서 내용
- **지원**: 한국어/영어 자연어 검색

#### 주요 파라미터
- `query`: 검색어
- `lang`: 언어 코드 ("ko", "en")
- `sentences`: 요약 문장 수 (기본값: 5)

#### 출력 예시
```
📊 Wikipedia 검색 결과: '인공지능'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: Wikipedia (한국어)
📊 발견된 문서: 1개

📈 [1] 인공지능
────────────────────────────────────────
📋 페이지 ID: 12345
📋 제목: 인공지능
📋 언어: ko
📋 URL: https://ko.wikipedia.org/wiki/인공지능

📄 내용:
인공지능(人工知能, 영어: artificial intelligence, AI)은 인간의 학습능력, 추론능력, 지각능력, 자연언어의 이해능력 등을 컴퓨터 프로그램으로 실현한 기술이다. 인공지능의 개념은 1950년대부터 존재했지만, 21세기 들어 빅데이터와 컴퓨팅 파워의 발전으로 급속도로 발전하고 있다...
```

---

## 📰 뉴스 도구

### Naver News 검색

#### 개요
- **API**: 네이버 검색 API
- **데이터**: 네이버 뉴스 검색 결과
- **지원**: 한국어 자연어 검색

#### 주요 파라미터
- `query`: 검색어
- `sort`: 정렬 기준 ("sim": 정확도, "date": 최신순)
- `display`: 검색 결과 개수 (최대 100)
- `start`: 검색 시작 위치

#### 출력 예시
```
📊 Naver News 검색 결과: '경제'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: 네이버 뉴스
📊 발견된 기사: 5개

📈 [1] 한국경제 성장률 전망 상향 조정
────────────────────────────────────────
📋 제목: 한국경제 성장률 전망 상향 조정
📋 언론사: 연합뉴스
📋 발행일: 2024-12-06T09:30:00+09:00
📋 링크: https://news.naver.com/main/read.naver?mode=...

📄 요약:
한국은행이 올해 경제성장률 전망치를 기존 2.4%에서 2.6%로 상향 조정했다고 발표했다. 수출 증가와 내수 회복이 주요 원인으로 분석된다...
```

### NewsAPI 글로벌 뉴스

#### 개요
- **API**: NewsAPI
- **데이터**: 전 세계 뉴스 소스
- **지원**: 영어 자연어 검색

#### 주요 파라미터
- `query`: 검색어
- `language`: 언어 코드 ("en", "ko")
- `sort_by`: 정렬 기준 (relevancy, popularity, publishedAt)
- `page_size`: 페이지당 결과 수 (최대 100)

#### 출력 예시
```
📊 NewsAPI 검색 결과: 'technology'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: NewsAPI (Global News)
📊 발견된 기사: 3개

📈 [1] AI Breakthrough in Quantum Computing
────────────────────────────────────────
📋 제목: AI Breakthrough in Quantum Computing
📋 언론사: TechCrunch
📋 저자: Sarah Martinez
📋 발행일: 2024-12-06T14:20:00Z
📋 링크: https://techcrunch.com/2024/12/06/ai-breakthrough...

📄 요약:
Researchers at MIT have achieved a significant breakthrough in quantum computing by integrating artificial intelligence algorithms that can optimize quantum gate operations in real-time...
```

### Google Fact Check

#### 개요
- **API**: Google Fact Check Tools API
- **데이터**: 검증된 팩트체크 결과
- **지원**: 다국어 검색

#### 주요 파라미터
- `query`: 검색어
- `language`: 언어 코드 ("en", "ko")
- `maxAgeDays`: 최대 게시 일수
- `pageSize`: 페이지 크기

#### 출력 예시
```
📊 Google Fact Check 검색 결과: 'climate change'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 출처: Google Fact Check Tools
📊 발견된 팩트체크: 2개

📈 [1] Climate Change Temperature Records
────────────────────────────────────────
📋 주장: "2023 was the hottest year on record globally"
📋 팩트체크 결과: TRUE
📋 검증 기관: Climate Feedback
📋 발행일: 2024-01-15
📋 링크: https://climatefeedback.org/evaluation/2023-hottest-year

📄 검증 내용:
Multiple independent datasets including NASA GISS, NOAA, and Berkeley Earth confirm that 2023 was indeed the warmest year in the instrumental temperature record, with global average temperatures exceeding the previous record set in 2016...
```

## 공통 설계 특징

### 메타데이터 보존
- 모든 API 응답 필드를 원본 그대로 전달
- 날짜, URL, 저자, 출처 정보 완전 보존
- LLM이 신뢰성을 판단할 수 있는 충분한 컨텍스트 제공

### 구조화된 출력
- 일관된 이모지 기반 시각적 구조
- 계층적 정보 배치 (제목 → 메타데이터 → 내용)
- 팩트체킹에 필요한 핵심 정보 강조

### 자연어 검색
- 한국어/영어 쿼리 지원
- 복합 검색어 처리 ("한국 경제 성장률")
- 관련도 기반 결과 순위화