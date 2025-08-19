"""전체 도구 테스트 - 모든 도구 검증"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tools import (
    ArxivSearchTool,
    WikipediaSearchTool, 
    OpenAlexTool,
    NaverNewsTool,
    KOSISSearchTool,
    WorldBankSearchTool,
    FREDSearchTool,
    OWIDRAGTool,
    NewsAPITool,
    GoogleFactCheckTool,
    TwitterTool
)

# TavilySearchTool은 별도 패키지
try:
    from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ TavilySearchTool not available (crewai-tools 패키지 필요)")


def test_tool(tool_class, tool_name, params):
    """도구 테스트"""
    print(f"\n{'='*60}")
    print(f"🔧 {tool_name}")
    print('='*60)
    
    try:
        tool = tool_class()
        result = tool._run(**params)
        
        # 결과 분석
        char_count = len(result)
        has_data = any(char.isdigit() for char in result)
        has_metadata = '📋' in result or 'metadata' in result.lower() or '출처' in result
        
        print(f"✅ 성공 - {char_count:,}자")
        print(f"🔢 데이터: {'있음' if has_data else '없음'}")
        print(f"📁 메타데이터: {'있음' if has_metadata else '없음'}")
        
        # 미리보기 (처음 300자)
        preview = result[:300] + "..." if len(result) > 300 else result
        print(f"\n📄 출력:")
        print(preview)
        
        return True
        
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        return False


def test_tavily_tool():
    """Tavily 도구 테스트"""
    print(f"\n{'='*60}")
    print(f"🔧 Tavily 웹 검색")
    print('='*60)
    
    try:
        # Tavily는 초기화 시 파라미터 필요
        tool = TavilySearchTool(
            topic="general",
            search_depth="basic", 
            max_results=5
        )
        
        # run 메서드 호출 (not _run)
        result = tool.run(query="한국 경제 성장률")
        
        # 결과 분석
        char_count = len(str(result))
        has_data = any(char.isdigit() for char in str(result))
        
        print(f"✅ 성공 - {char_count:,}자")
        print(f"🔢 데이터: {'있음' if has_data else '없음'}")
        
        # 미리보기 (처음 300자)
        preview = str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
        print(f"\n📄 출력:")
        print(preview)
        
        return True
        
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        # API 키 확인
        if "TAVILY_API_KEY" not in os.environ:
            print("   💡 TAVILY_API_KEY가 설정되지 않았습니다")
        return False


def main():
    """모든 도구 테스트"""
    
    print("🚀 FactWave 전체 도구 테스트")
    print("="*70)
    
    # 테스트 설정
    tests = [
        # 통계 도구들
        (KOSISSearchTool, "KOSIS 통계청", {"query": "실업률", "limit": 1, "fetch_data": True}),
        (FREDSearchTool, "FRED 미연준", {"query": "unemployment", "fetch_data": True, "limit": 3}),
        (WorldBankSearchTool, "WorldBank 세계은행", {"query": "GDP growth", "country": "KR", "fetch_data": True, "years": 3}),
        (OWIDRAGTool, "OWID", {"query": "Korea GDP", "n_results": 2, "use_reranker": True}),
        
        # 학술 도구들
        (ArxivSearchTool, "ArXiv 논문", {"query": "machine learning", "max_results": 1, "sort_by": "relevance"}),
        (OpenAlexTool, "OpenAlex 학술", {"query": "AI", "limit": 1, "year_from": 2023}),
        (WikipediaSearchTool, "Wikipedia", {"query": "인공지능", "lang": "ko"}),
        
        # 뉴스 도구들
        (NaverNewsTool, "Naver 뉴스", {"query": "경제", "sort": "sim", "display": 1, "start": 1}),
        (NewsAPITool, "NewsAPI", {"query": "technology", "language": "en", "page_size": 1}),
        (GoogleFactCheckTool, "Google 팩트체크", {"query": "climate change", "languageCode": "en"})
    ]
    
    # Tavily 검색 도구 (모든 에이전트가 사용하는 핵심 도구)
    if TAVILY_AVAILABLE:
        # Tavily는 초기화 방식이 다름
        tests.insert(0, (None, "Tavily 웹 검색", "tavily_special"))
    
    # 커뮤니티 도구
    tests.append((TwitterTool, "Twitter/X", {"query": "Korea", "limit": 3}))
    
    success_count = 0
    total_count = len(tests)
    
    for tool_class, tool_name, params in tests:
        success = test_tool(tool_class, tool_name, params)
        if success:
            success_count += 1
    
    # 최종 결과
    print(f"\n{'='*70}")
    print("📊 최종 결과")
    print('='*70)
    print(f"✅ 성공: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print(f"❌ 실패: {total_count-success_count}/{total_count}")
    
    # 카테고리별 분석
    print(f"\n📈 카테고리별:")
    if TAVILY_AVAILABLE:
        print(f"  핵심 도구: 1개 (Tavily 웹 검색)")
    print(f"  통계 도구: 4개 (KOSIS, FRED, WorldBank, OWID)")
    print(f"  학술 도구: 3개 (ArXiv, OpenAlex, Wikipedia)")  
    print(f"  뉴스 도구: 3개 (Naver, NewsAPI, GoogleFC)")
    print(f"  커뮤니티 도구: 1개 (Twitter/X)")


if __name__ == "__main__":
    main()