"""Twitter/X 계정 설정 스크립트 - 쿠키 기반 인증"""

import asyncio
from twscrape import API
import os

async def setup_twitter_account():
    """쿠키를 사용한 Twitter 계정 설정"""
    
    # 쿠키 문자열 (브라우저에서 복사한 것)
    cookies = """guest_id_marketing=v1%3A175526173972281417; guest_id_ads=v1%3A175526173972281417; guest_id=v1%3A175526173972281417; __cf_bm=8L.teVKvgC.jJn8JEesqz6QWNrBaviNm_9.y0nkZbAY-1755261739-1.0.1.1-NNgN9bv7WJH574e8gkpCnSMuIBp.2R26YmJHPs2uMIZ5AW_IYWiMgbqCJWCqcuq5T6aNIayVqngPmOr.PxC.E5H7rDSshNas4Ir4BqydzGo; personalization_id="v1_V9z4RHjiN5qUPydJh5F9Vg=="; gt=1956335646530031996; __cuid=2426d0bbebe1415893db105c61426c72; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX|0|8e8t2xd8A2w%3D; att=1-1pHNWfVTtKI9MXEjVHV0y138rziYSQ4OI7uwyrYO; kdt=V7Igls4mptrkS4DDnm3EHpAqT0IGAVOG2RSrvn3O; auth_token=59da2290c63fc1651481e50f5f2f1bd7216fc1ca; ct0=4d4dda61017becdc47dee69973e2044d2e03df59caf7e6664127016b329dd5a3ac4764ff791605b60fb08371a766c0ae53b51f4fa02af7530dd8ed0fcd9935e05a0aa19abf1ea0a653e090677fbf10d1; g_state={"i_l":0}; lang=en; twid=u%3D1956335677861498880"""
    
    # API 초기화 (accounts.db 파일에 저장됨)
    api = API()
    
    try:
        # 계정 추가 (쿠키 사용)
        # username과 password는 형식상 필요하지만 실제로는 쿠키가 인증을 담당
        await api.pool.add_account(
            "factwave_user",  # 임의의 username
            "dummy_password",  # 임의의 password (쿠키 사용시 무시됨)
            "factwave@example.com",  # 임의의 email
            "dummy_email_pass",  # 임의의 email password (쿠키 사용시 무시됨)
            cookies=cookies
        )
        
        print("✅ Twitter 계정이 성공적으로 추가되었습니다!")
        print("📁 계정 정보가 accounts.db에 저장되었습니다.")
        
        # 계정 테스트
        print("\n🔍 계정 테스트 중...")
        tweet_count = 0
        async for tweet in api.search("Korea", limit=3):
            tweet_count += 1
            print(f"  ✓ 트윗 {tweet_count}: @{tweet.user.username}")
        
        if tweet_count > 0:
            print(f"\n✅ 테스트 성공! {tweet_count}개 트윗을 가져왔습니다.")
        else:
            print("\n⚠️ 트윗을 가져오지 못했습니다. 쿠키를 확인해주세요.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print("\n💡 해결 방법:")
        print("1. 브라우저에서 Twitter에 다시 로그인")
        print("2. F12 → Network → 아무 요청 클릭 → Headers → Cookie 전체 복사")
        print("3. 위 cookies 변수에 붙여넣기")
        print("4. 특히 'auth_token'과 'ct0' 값이 포함되어 있는지 확인")

async def test_search():
    """검색 테스트"""
    api = API()
    
    print("\n🔍 한국 관련 최신 트윗 검색 중...")
    tweets = []
    async for tweet in api.search("한국 OR Korea lang:ko", limit=5):
        tweets.append(tweet)
        print(f"📌 @{tweet.user.username}: {tweet.rawContent[:100]}...")
    
    if tweets:
        print(f"\n✅ 총 {len(tweets)}개 트윗 수집 완료!")
    else:
        print("\n⚠️ 트윗을 찾을 수 없습니다.")

if __name__ == "__main__":
    print("🐦 Twitter/X 계정 설정")
    print("="*50)
    
    # 계정 설정
    asyncio.run(setup_twitter_account())
    
    # 검색 테스트 (선택사항)
    print("\n검색 테스트를 실행하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        asyncio.run(test_search())