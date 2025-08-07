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
    from app.services.tools.owid_rag_tool import OWIDRAGTool
    
    # Test Wikipedia
    console.print("[bold]1. Wikipedia Search Tool[/bold]")
    try:
        wiki_tool = WikipediaSearchTool()
        wiki_result = wiki_tool._run("artificial intelligence", lang="en")
        console.print(Panel(wiki_result[:500], title="Wikipedia Result", border_style="green"))
    except Exception as e:
        console.print(f"[red]❌ Wikipedia 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test OpenAlex (Semantic Scholar 대체)
    console.print("[bold]2. OpenAlex Academic Search[/bold]")
    try:
        oa_tool = OpenAlexTool()
        oa_result = oa_tool._run("GPT-4", limit=2)
        console.print(Panel(oa_result[:500], title="OpenAlex Result", border_style="blue"))
    except Exception as e:
        console.print(f"[red]❌ OpenAlex 오류: {e}[/red]")
    
    
    console.print("\n" + "="*80 + "\n")
    
    # Test ArXiv
    console.print("[bold]3. ArXiv Search Tool[/bold]")
    try:
        arxiv_tool = ArxivSearchTool()
        arxiv_result = arxiv_tool._run("transformer", max_results=2)
        console.print(Panel(arxiv_result[:500], title="ArXiv Result", border_style="yellow"))
    except Exception as e:
        console.print(f"[red]❌ ArXiv 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test Naver News
    console.print("[bold]4. Naver News Tool[/bold]")
    try:
        naver_tool = NaverNewsTool()
        naver_result = naver_tool._run("인공지능", sort="date", display=3)
        console.print(Panel(naver_result[:500], title="Naver News Result", border_style="red"))
    except Exception as e:
        console.print(f"[red]❌ Naver News 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test OWID RAG Tool
    console.print("[bold]5. OWID Statistics RAG Tool[/bold]")
    try:
        owid_tool = OWIDRAGTool()
        
        # Test Korean query
        console.print("[yellow]Testing Korean query: '한국 CO2 배출량'[/yellow]")
        owid_result_kr = owid_tool._run("한국 CO2 배출량", n_results=2, use_reranker=True)
        console.print(Panel(owid_result_kr[:500], title="OWID Korean Query", border_style="magenta"))
        
        # Test English query
        console.print("\n[yellow]Testing English query: 'Brazil GDP growth'[/yellow]")
        owid_result_en = owid_tool._run("Brazil GDP growth", n_results=2, use_reranker=False)
        console.print(Panel(owid_result_en[:500], title="OWID English Query", border_style="cyan"))
        
    except Exception as e:
        console.print(f"[red]❌ OWID RAG 오류: {e}[/red]")


def test_individual_agents():
    """개별 에이전트 테스트"""
    console.print("\n[bold cyan]🤖 개별 에이전트 테스트[/bold cyan]\n")
    
    from app.agents.academic_agent import AcademicAgent
    from app.agents.news_agent import NewsAgent
    from app.agents.statistics_agent import StatisticsAgent
    from crewai import Task
    
    # Test Academic Agent
    console.print("[bold]1. Academic Agent Test[/bold]")
    try:
        academic_agent = AcademicAgent()
        academic_task = Task(
            description="Research about GPT-4 release date and technical specifications",
            expected_output="Academic findings about GPT-4",
            agent=academic_agent.agent
        )
        console.print("[green]✅ Academic Agent initialized with tools[/green]")
        console.print(f"   Tools: {[tool.name for tool in academic_agent.tools]}")
    except Exception as e:
        console.print(f"[red]❌ Academic Agent 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test News Agent
    console.print("[bold]2. News Agent Test[/bold]")
    try:
        news_agent = NewsAgent()
        news_task = Task(
            description="최근 AI 관련 뉴스를 검색하세요",
            expected_output="Latest AI news findings",
            agent=news_agent.agent
        )
        console.print("[green]✅ News Agent initialized with tools[/green]")
        console.print(f"   Tools: {[tool.name for tool in news_agent.tools]}")
    except Exception as e:
        console.print(f"[red]❌ News Agent 오류: {e}[/red]")
    
    console.print("\n" + "="*80 + "\n")
    
    # Test Statistics Agent
    console.print("[bold]3. Statistics Agent Test[/bold]")
    try:
        stats_agent = StatisticsAgent()
        stats_task = Task(
            description="한국의 CO2 배출량 통계를 찾아주세요",
            expected_output="Statistical data about Korea's CO2 emissions",
            agent=stats_agent.agent
        )
        console.print("[green]✅ Statistics Agent initialized with OWID RAG[/green]")
        console.print(f"   Tools: {[tool.name for tool in stats_agent.tools]}")
    except Exception as e:
        console.print(f"[red]❌ Statistics Agent 오류: {e}[/red]")


def test_crew_with_tools():
    """Crew 테스트 (도구 사용 포함)"""
    console.print("\n[bold cyan]🚀 Full Crew 통합 테스트[/bold cyan]\n")
    
    from app.core.crew import FactWaveCrew
    
    # Test different types of claims
    test_statements = [
        ("GPT-4는 2023년 3월에 출시되었다", "AI/Tech claim"),
        ("한국의 재생에너지 비율이 10%를 넘었다", "Statistics claim"),
        ("브라질의 GDP 성장률이 5%를 초과했다", "Economic claim")
    ]
    
    crew = FactWaveCrew()
    
    for statement, category in test_statements:
        console.print(f"\n[yellow]테스트 주장 ({category}):[/yellow] {statement}")
        console.print("[dim]Processing...[/dim]\n")
        
        try:
            result = crew.check_fact(statement)
            if result:
                console.print("[green]✅ Fact-checking completed[/green]")
            else:
                console.print("[yellow]⚠️ No result returned[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
        
        console.print("\n" + "-"*60)


def main():
    """메인 테스트 실행"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "tools":
            test_individual_tools()
        elif sys.argv[1] == "agents":
            test_individual_agents()
        elif sys.argv[1] == "crew":
            test_crew_with_tools()
        elif sys.argv[1] == "all":
            test_individual_tools()
            test_individual_agents()
            test_crew_with_tools()
        else:
            console.print("[red]사용법: uv run python test_integrated.py [tools|agents|crew|all][/red]")
    else:
        console.print("[bold green]🧪 FactWave 통합 테스트[/bold green]\n")
        console.print("1. 개별 도구 테스트: [cyan]uv run python test_integrated.py tools[/cyan]")
        console.print("2. 개별 에이전트 테스트: [cyan]uv run python test_integrated.py agents[/cyan]")
        console.print("3. Crew 통합 테스트: [cyan]uv run python test_integrated.py crew[/cyan]")
        console.print("4. 전체 테스트: [cyan]uv run python test_integrated.py all[/cyan]")


if __name__ == "__main__":
    main()