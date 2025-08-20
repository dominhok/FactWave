import requests
import json

# 테스트용 이미지 URL
test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabass.jpg/1200px-New_york_times_square-terabass.jpg"

print(f"이미지 분석 테스트: {test_url[:50]}...")

# REST API 호출
response = requests.post(
    "http://localhost:8000/api/analyze-image",
    json={"url": test_url}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ 분석 성공!")
    print(f"상태: {result.get('status')}")
    print(f"결과 길이: {len(result.get('result', ''))}")
    print("\n=== 분석 결과 (처음 500자) ===")
    print(result.get('result', '')[:500])
else:
    print(f"❌ 오류: {response.status_code}")
    print(response.text)
