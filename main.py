#!/usr/bin/env python3
"""
FactWave - 3단계 멀티에이전트 팩트체킹 시스템
"""

import os
from dotenv import load_dotenv
from rich.console import Console
from app.core import FactWaveCrew

# Load environment variables
load_dotenv()

# Setup console
console = Console()

# Setup OpenAI client for Upstage Solar-pro2
api_key = os.getenv("UPSTAGE_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "solar-pro2"
os.environ["OPENAI_BASE_URL"] = "https://api.upstage.ai/v1"


def main():
    """Main CLI interface"""
    console.print("""
[bold cyan]🔍 FactWave - 3단계 팩트체킹 시스템[/bold cyan]
[dim]다중 AI 에이전트가 협력하여 사실을 검증합니다[/dim]

[bold]프로세스:[/bold]
1️⃣  Step 1: 각 전문가가 독립적으로 분석
2️⃣  Step 2: 전문가들 간의 토론과 의견 교환
3️⃣  Step 3: 총괄 코디네이터의 최종 종합 판정
    """)
    
    # Initialize the crew
    fact_checker = FactWaveCrew()
    
    while True:
        console.print("\n[bold]팩트체크할 문장을 입력하세요[/bold] ('quit'로 종료):")
        statement = input("> ").strip()
        
        if statement.lower() in ['quit', 'exit', 'q']:
            console.print("\n[dim]감사합니다! 다음에 또 이용해주세요 👋[/dim]")
            break
        
        if not statement:
            console.print("[red]확인할 문장을 입력해주세요.[/red]")
            continue
        
        try:
            # Run 3-stage fact-check
            result = fact_checker.check_fact(statement)
            
        except Exception as e:
            console.print(f"\n[red]팩트체킹 중 오류 발생: {e}[/red]")
            console.print("[dim]다른 문장으로 다시 시도해주세요.[/dim]")


if __name__ == "__main__":
    main()