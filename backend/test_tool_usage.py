#!/usr/bin/env python3
"""
Tool Usage Test - 도구 호출 로깅 테스트
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import time

# 환경 설정
load_dotenv()
console = Console()

# API 설정
def setup_api():
    """Configure API settings"""
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        console.print("[red]❌ UPSTAGE_API_KEY not found in .env file![/red]")
        sys.exit(1)
    
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "solar-pro2"

setup_api()

# CrewAI 로깅 설정
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('crewai')
logger.setLevel(logging.DEBUG)

# 도구 호출 추적을 위한 핸들러
class ToolCallHandler(logging.Handler):
    def emit(self, record):
        if 'tool' in record.getMessage().lower() or 'calling' in record.getMessage().lower():
            console.print(f"[bold magenta]🔍 {record.getMessage()}[/bold magenta]")

tool_handler = ToolCallHandler()
logger.addHandler(tool_handler)

console.print(Panel.fit("🧪 [bold cyan]도구 호출 테스트[/bold cyan]", border_style="cyan"))

# 에이전트 임포트
from app.agents import AcademicAgent, NewsAgent

def test_single_agent():
    """단일 에이전트 도구 호출 테스트"""
    console.print("\n[bold yellow]1. Academic Agent 테스트[/bold yellow]")
    
    # Academic Agent 생성
    academic = AcademicAgent()
    agent = academic.get_agent("step1")
    
    console.print(f"[dim]사용 가능한 도구: {[tool.__class__.__name__ for tool in academic.tools]}[/dim]")
    
    # Task 생성 및 실행
    from crewai import Task
    
    task = Task(
        description="""
        다음 주장을 검증하세요: "한국의 출산율은 2023년 세계 최저 수준이다"
        
        반드시 도구를 사용하여 실제 데이터를 조사하세요:
        1. TavilySearchTool을 사용하여 웹에서 관련 정보를 검색하세요
        2. Wikipedia Search를 사용하여 한국 출산율 관련 배경 정보를 찾으세요
        
        도구를 최소 2개 이상 사용하세요.
        """,
        agent=agent,
        expected_output="도구를 사용한 검증 결과"
    )
    
    console.print("\n[green]Task 실행 중...[/green]\n")
    
    # Crew 생성 및 실행
    from crewai import Crew, Process
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    
    console.print("\n[bold green]✅ 결과:[/bold green]")
    console.print(result)

def test_news_agent():
    """News Agent 도구 호출 테스트"""
    console.print("\n[bold yellow]2. News Agent 테스트[/bold yellow]")
    
    # News Agent 생성
    news = NewsAgent()
    agent = news.get_agent("step1")
    
    console.print(f"[dim]사용 가능한 도구: {[tool.__class__.__name__ for tool in news.tools]}[/dim]")
    
    # Task 생성 및 실행
    from crewai import Task
    
    task = Task(
        description="""
        다음 주장을 검증하세요: "2024년 한국 대통령이 미국을 방문했다"
        
        반드시 도구를 사용하여 뉴스를 조사하세요:
        1. TavilySearchTool을 사용하여 최신 뉴스를 검색하세요 (topic='news')
        2. Naver News Search를 사용하여 한국 언론 보도를 확인하세요
        
        각 도구의 결과를 명시적으로 언급하세요.
        """,
        agent=agent,
        expected_output="도구를 사용한 뉴스 검증 결과"
    )
    
    console.print("\n[green]Task 실행 중...[/green]\n")
    
    # Crew 생성 및 실행
    from crewai import Crew, Process
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    
    console.print("\n[bold green]✅ 결과:[/bold green]")
    console.print(result)

if __name__ == "__main__":
    try:
        console.print("\n[cyan]테스트를 선택하세요:[/cyan]")
        console.print("1. Academic Agent 테스트")
        console.print("2. News Agent 테스트")
        console.print("3. 모두 테스트")
        
        choice = input("\n선택 (1/2/3): ")
        
        if choice == "1":
            test_single_agent()
        elif choice == "2":
            test_news_agent()
        elif choice == "3":
            test_single_agent()
            test_news_agent()
        else:
            console.print("[red]잘못된 선택입니다.[/red]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]테스트 중단[/yellow]")
    except Exception as e:
        console.print(f"\n[red]오류 발생: {e}[/red]")
        import traceback
        traceback.print_exc()