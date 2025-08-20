# Twitter/X Multi-Account Management Guide

## 🚀 Quick Start

### 1. 쿠키 획득 방법
1. Twitter/X 웹사이트 로그인 (https://twitter.com 또는 https://x.com)
2. F12 키를 눌러 개발자 도구 열기
3. Application/Storage 탭 → Cookies → https://twitter.com
4. 다음 쿠키 값들을 복사:
   - `ct0` (CSRF 토큰)
   - `auth_token` (인증 토큰)

### 2. 계정 관리 도구 실행

#### 대화형 메뉴 모드
```bash
cd backend
uv run python manage_twitter_accounts.py
```

#### 명령줄 모드
```bash
# 계정 상태 확인
uv run python manage_twitter_accounts.py status

# 단일 계정 추가
uv run python manage_twitter_accounts.py add username "ct0=xxx;auth_token=yyy"

# 파일에서 여러 계정 추가
uv run python manage_twitter_accounts.py add-file accounts.txt

# 검색 테스트
uv run python manage_twitter_accounts.py test "검색어"
```

## 📋 accounts.txt 파일 형식

### 기본 형식
```
username|cookies
```

### 예제
```
# 문자열 형식 쿠키
user1|ct0=abcd1234567890;auth_token=xyz987654321

# JSON 형식 쿠키
user2|{"ct0": "abcd1234567890", "auth_token": "xyz987654321"}

# 프록시 포함 (선택사항)
user3|ct0=abcd1234567890;auth_token=xyz987654321|http://proxy.example.com:8080
```

## 🔄 Rate Limit 처리

### 자동 계정 전환
- twscrape가 자동으로 rate limit 감지 및 계정 전환
- 한 계정이 제한에 걸리면 다음 활성 계정으로 자동 전환
- 24시간 후 자동으로 다시 사용 가능

### 권장 계정 수
- **최소**: 3-5개 계정
- **권장**: 5-10개 계정
- **대량 스크래핑**: 10개 이상

### Rate Limit 현황 (2025년 기준)
- 계정당 약 11-13개 요청/24시간
- 15분 단위로 리셋되는 엔드포인트별 제한
- 검색: 10초 간격 권장

## 🛡️ 계정 보호 팁

### 1. 프록시 사용
```
username|cookies|http://proxy:port
```

### 2. 계정 로테이션
- 여러 계정을 등록하여 자동 로테이션
- 한 계정이 차단되어도 다른 계정으로 계속 작동

### 3. 쿠키 갱신
- 쿠키는 보통 30일 유효
- 주기적으로 새 쿠키로 업데이트 필요

## 🔧 문제 해결

### 계정이 작동하지 않을 때
```bash
# 실패한 계정 재로그인 시도
uv run python manage_twitter_accounts.py relogin

# 계정 상태 확인
uv run python manage_twitter_accounts.py status
```

### 모든 계정이 rate limit에 걸렸을 때
1. 24시간 대기
2. 새 계정 추가
3. 프록시 사용 고려

## 📊 계정 상태 확인

`manage_twitter_accounts.py status` 실행 시 표시되는 정보:
- **Username**: 계정 이름
- **Active**: 활성 상태 (✅/❌)
- **Logged In**: 로그인 상태 (✅/❌)
- **Requests**: 총 요청 수
- **Last Used**: 마지막 사용 시간
- **Error**: 오류 메시지 (있을 경우)

## 🚨 주의사항

1. **계정 보안**
   - 쿠키는 민감한 정보이므로 안전하게 보관
   - accounts.db 파일을 git에 커밋하지 않도록 주의
   - .gitignore에 accounts.db 포함 확인

2. **API 제한**
   - Twitter/X는 적극적인 안티-스크래핑 정책 운영
   - 과도한 요청 시 계정 정지 가능
   - 항상 적절한 간격으로 요청

3. **법적 준수**
   - Twitter/X 서비스 약관 확인
   - 개인정보 수집 관련 법규 준수
   - 상업적 사용 시 추가 제한 확인

## 💡 팁

### 효율적인 계정 관리
1. 5-10개 계정을 미리 준비
2. 각 계정마다 다른 프록시 할당 (가능한 경우)
3. 주기적으로 계정 상태 모니터링
4. 실패한 계정은 즉시 재로그인 시도

### 쿠키 자동 추출 (브라우저 확장)
- EditThisCookie 확장 프로그램 사용
- Cookie-Editor 확장 프로그램 사용
- 쿠키를 JSON 형식으로 내보내기 가능

## 📝 예제 시나리오

### 시나리오 1: 초기 설정
```bash
# 1. 예제 파일 생성
uv run python manage_twitter_accounts.py
# 옵션 8 선택

# 2. accounts.txt 작성
# (쿠키 정보 입력)

# 3. 계정 추가
uv run python manage_twitter_accounts.py add-file accounts.txt

# 4. 상태 확인
uv run python manage_twitter_accounts.py status
```

### 시나리오 2: Rate Limit 대응
```bash
# 1. 여러 계정 준비 (accounts.txt)
user1|ct0=xxx;auth_token=yyy
user2|ct0=aaa;auth_token=bbb
user3|ct0=ccc;auth_token=ddd

# 2. 일괄 추가
uv run python manage_twitter_accounts.py add-file accounts.txt

# 3. 자동 로테이션 확인
uv run python manage_twitter_accounts.py test "AI"
```

## 🔗 관련 파일
- `app/services/tools/community/twitter_tool.py`: Twitter 도구 구현
- `manage_twitter_accounts.py`: 계정 관리 도구
- `accounts.db`: SQLite 데이터베이스 (자동 생성)
- `.env`: 환경 변수 설정 (필요시)