#!/usr/bin/env python3
"""Tavily 도구 개별 테스트"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console

# 환경 설정
load_dotenv()
console = Console()

console.print("[bold cyan]🔍 Tavily Search Tool 테스트[/bold cyan]")
console.print("="*60)

# 1. Import 테스트
console.print("\n[yellow]1. Import 테스트[/yellow]")
try:
    from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool
    console.print("✅ TavilySearchTool import 성공")
except ImportError as e:
    console.print(f"❌ Import 실패: {e}")
    sys.exit(1)

# 2. API 키 확인
console.print("\n[yellow]2. API 키 확인[/yellow]")
api_key = os.getenv("TAVILY_API_KEY")
if api_key:
    console.print(f"✅ TAVILY_API_KEY 설정됨 (길이: {len(api_key)})")
else:
    console.print("❌ TAVILY_API_KEY가 .env에 없습니다")
    console.print("   .env에 추가하세요: TAVILY_API_KEY=your_key_here")

# 3. 도구 초기화 테스트
console.print("\n[yellow]3. 도구 초기화 테스트[/yellow]")
try:
    tool = TavilySearchTool()
    console.print("✅ 기본 초기화 성공")
    console.print(f"   도구 이름: {tool.name}")
    console.print(f"   설명: {tool.description[:100]}...")
except Exception as e:
    console.print(f"❌ 초기화 실패: {e}")
    import traceback
    traceback.print_exc()

# 4. 파라미터 포함 초기화
console.print("\n[yellow]4. 파라미터 포함 초기화[/yellow]")
try:
    tool_with_params = TavilySearchTool(
        topic="general",
        search_depth="basic",
        max_results=5,
        include_answer=True,
        days=30
    )
    console.print("✅ 파라미터 초기화 성공")
except Exception as e:
    console.print(f"❌ 파라미터 초기화 실패: {e}")

# 5. 실제 검색 테스트
console.print("\n[yellow]5. 실제 검색 테스트[/yellow]")
if api_key:
    try:
        tool = TavilySearchTool(
            topic="news",
            search_depth="basic",
            max_results=3
        )
        
        # run 메서드 확인
        console.print("도구 메서드 확인:")
        methods = [m for m in dir(tool) if not m.startswith('_')]
        console.print(f"   공개 메서드: {methods}")
        
        # _run 메서드 확인
        if hasattr(tool, '_run'):
            console.print("   ✅ _run 메서드 존재")
            console.print(f"   _run 타입: {type(tool._run)}")
        else:
            console.print("   ❌ _run 메서드 없음")
        
        # run 메서드 확인
        if hasattr(tool, 'run'):
            console.print("   ✅ run 메서드 존재")
            console.print(f"   run 타입: {type(tool.run)}")
        else:
            console.print("   ❌ run 메서드 없음")
        
        console.print("\n검색 실행 중...")
        
        # 다양한 방법으로 실행 시도
        result = None
        
        # 방법 1: run 메서드
        try:
            if hasattr(tool, 'run'):
                result = tool.run(query="한국 경제 성장률 2024")
                console.print("✅ run() 메서드로 실행 성공")
        except Exception as e:
            console.print(f"   run() 실패: {e}")
        
        # 방법 2: _run 메서드
        if result is None:
            try:
                if hasattr(tool, '_run'):
                    result = tool._run(query="한국 경제 성장률 2024")
                    console.print("✅ _run() 메서드로 실행 성공")
            except Exception as e:
                console.print(f"   _run() 실패: {e}")
        
        # 방법 3: 직접 호출
        if result is None:
            try:
                result = tool(query="한국 경제 성장률 2024")
                console.print("✅ 직접 호출로 실행 성공")
            except Exception as e:
                console.print(f"   직접 호출 실패: {e}")
        
        if result:
            console.print(f"\n[green]검색 성공![/green]")
            console.print(f"결과 타입: {type(result)}")
            console.print(f"결과 길이: {len(str(result))} 자")
            console.print(f"\n미리보기 (처음 500자):")
            preview = str(result)[:500]
            console.print(preview)
        else:
            console.print("[red]모든 실행 방법 실패[/red]")
            
    except Exception as e:
        console.print(f"[red]검색 테스트 실패: {e}[/red]")
        import traceback
        traceback.print_exc()
else:
    console.print("[yellow]API 키가 없어 실제 검색은 건너뜁니다[/yellow]")

# 6. CrewAI 통합 테스트
console.print("\n[yellow]6. CrewAI와 통합 테스트[/yellow]")
try:
    from crewai import Agent, Task, Crew
    
    # 에이전트 생성
    test_agent = Agent(
        role="테스트 에이전트",
        goal="Tavily 도구 테스트",
        backstory="도구 테스트용 에이전트",
        tools=[TavilySearchTool()],
        verbose=True
    )
    console.print("✅ 에이전트에 도구 연결 성공")
    
    # Task 생성
    test_task = Task(
        description="한국의 GDP에 대해 검색하세요",
        agent=test_agent,
        expected_output="검색 결과"
    )
    console.print("✅ Task 생성 성공")
    
except Exception as e:
    console.print(f"❌ CrewAI 통합 실패: {e}")

console.print("\n" + "="*60)
console.print("[bold green]테스트 완료![/bold green]")