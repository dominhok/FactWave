#!/usr/bin/env python3
"""통합 테스트 - 도구 호출 및 에이전트 테스트"""

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
import sys

# Load environment variables
load_dotenv()

# Setup console
console = Console()

# Setup OpenAI client
api_key = os.getenv("UPSTAGE_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "solar-pro2"
os.environ["OPENAI_BASE_URL"] = "https://api.upstage.ai/v1"


def test_individual_tools():
    """개별 도구 테스트"""
    console.print("\n[bold cyan]🔧 개별 도구 테스트[/bold cyan]\n")
    
    from app.services.tools import WikipediaSearchTool, ArxivSearchTool, NaverNewsTool, OpenAlexTool
    
    # Test Wikipedia
    console.print("[bold]1. Wikipedia Search Tool[/bold]")
    try:
        wiki_tool = WikipediaSearchTool()
        wiki_result = wiki_tool._run("artificial intelligence", lang="en")
        console.print(Panel(wiki_result, title="Wikipedia Result", border_style="green"))
    except Exception as e:
        console.print(f"[red]❌ Wikipedia 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test OpenAlex (Semantic Scholar 대체)
    console.print("[bold]2. OpenAlex Academic Search[/bold]")
    try:
        oa_tool = OpenAlexTool()
        oa_result = oa_tool._run("GPT-4", limit=2)
        console.print(Panel(oa_result, title="OpenAlex Result", border_style="blue"))
    except Exception as e:
        console.print(f"[red]❌ OpenAlex 오류: {e}[/red]")
    
    
    console.print("\n" + "="*80 + "\n")
    
    # Test ArXiv
    console.print("[bold]3. ArXiv Search Tool[/bold]")
    try:
        arxiv_tool = ArxivSearchTool()
        arxiv_result = arxiv_tool._run("transformer", max_results=2)
        console.print(Panel(arxiv_result, title="ArXiv Result", border_style="yellow"))
    except Exception as e:
        console.print(f"[red]❌ ArXiv 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test Naver News
    console.print("[bold]4. Naver News Tool[/bold]")
    try:
        naver_tool = NaverNewsTool()
        naver_result = naver_tool._run("인공지능", sort="date", display=3)
        console.print(Panel(naver_result, title="Naver News Result", border_style="red"))
    except Exception as e:
        console.print(f"[red]❌ Naver News 오류: {e}[/red]")


def test_crew_with_tools():
    """Crew 테스트 (도구 사용 포함)"""
    console.print("\n[bold cyan]🤖 Crew 도구 사용 테스트[/bold cyan]\n")
    
    from app.core.crew import FactWaveCrew
    
    crew = FactWaveCrew()
    test_statement = "GPT-4는 2023년 3월에 출시되었다"
    
    console.print(f"[yellow]테스트 주장:[/yellow] {test_statement}\n")
    result = crew.check_fact(test_statement)


def main():
    """메인 테스트 실행"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "tools":
            test_individual_tools()
        elif sys.argv[1] == "crew":
            test_crew_with_tools()
        else:
            console.print("[red]사용법: uv run python test_integrated.py [tools|crew][/red]")
    else:
        console.print("[bold green]통합 테스트[/bold green]\n")
        console.print("1. 개별 도구 테스트: uv run python test_integrated.py tools")
        console.print("2. Crew 테스트: uv run python test_integrated.py crew")


if __name__ == "__main__":
    main()