#!/usr/bin/env python3
"""
FactWave - Advanced Multi-Agent Fact-Checking System
Main CLI Interface with Interactive Features
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Rich for beautiful console output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import print as rprint
import logging

# Project imports
from app.core import FactWaveCrew

# Setup
load_dotenv()
console = Console()

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure API settings
def setup_api():
    """Configure API settings for Upstage Solar-pro2"""
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        console.print("[red]❌ UPSTAGE_API_KEY not found in .env file![/red]")
        console.print("[yellow]Please set up your API key first.[/yellow]")
        sys.exit(1)
    
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "solar-pro2"
    os.environ["OPENAI_BASE_URL"] = "https://api.upstage.ai/v1"


class FactWaveInterface:
    """Interactive interface for FactWave fact-checking system"""
    
    def __init__(self):
        """Initialize the interface"""
        setup_api()
        self.fact_checker = None
        self.history: List[Dict[str, Any]] = []
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    def display_banner(self):
        """Display the application banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║     ███████╗ █████╗  ██████╗████████╗██╗    ██╗ █████╗ ██╗   ██╗███████╗║
║     ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██║    ██║██╔══██╗██║   ██║██╔════╝║
║     █████╗  ███████║██║        ██║   ██║ █╗ ██║███████║██║   ██║█████╗  ║
║     ██╔══╝  ██╔══██║██║        ██║   ██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝  ║
║     ██║     ██║  ██║╚██████╗   ██║   ╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗║
║     ╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝║
║                                                                           ║
║           🔍 AI-Powered Multi-Agent Fact-Checking System v2.0            ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
        console.print(
            "[dim]5 Specialized Agents | 3-Stage Verification | 14+ Research Tools[/dim]\n",
            justify="center"
        )
    
    def display_menu(self) -> str:
        """Display the main menu and get user choice"""
        menu = Panel(
            """[bold cyan]📋 메인 메뉴[/bold cyan]
            
1. 🔍 [bold]단일 팩트체크[/bold] - 하나의 진술 검증
2. 📑 [bold]일괄 검증[/bold] - 여러 진술 검증
3. 📁 [bold]파일에서 검증[/bold] - 파일에서 진술 로드
4. 📊 [bold]기록 보기[/bold] - 과거 검증 확인
5. 💡 [bold]예시 모드[/bold] - 예시 팩트체크 실행
6. ⚙️  [bold]설정[/bold] - 옵션 구성
7. ❓ [bold]도움말[/bold] - 문서 보기
8. 🚪 [bold]종료[/bold] - 애플리케이션 종료
            """,
            title="옵션 선택",
            border_style="cyan"
        )
        console.print(menu)
        
        choice = Prompt.ask(
            "[bold]선택하세요[/bold]",
            choices=["1", "2", "3", "4", "5", "6", "7", "8"],
            default="1"
        )
        return choice
    
    def single_fact_check(self):
        """Run a single fact check"""
        console.print("\n[bold cyan]🔍 단일 팩트체크 모드[/bold cyan]")
        console.print("[dim]검증하고자 하는 진술을 입력하세요[/dim]\n")
        
        statement = Prompt.ask("[bold]검증할 진술[/bold]")
        
        if not statement.strip():
            console.print("[red]진술이 입력되지 않았습니다![/red]")
            return
        
        self._run_fact_check(statement)
    
    def batch_verification(self):
        """Run batch verification of multiple statements"""
        console.print("\n[bold cyan]📑 일괄 검증 모드[/bold cyan]")
        console.print("[dim]진술을 하나씩 입력하세요. 완료되면 'done'을 입력하세요.[/dim]\n")
        
        statements = []
        while True:
            statement = Prompt.ask(f"[bold]진술 {len(statements) + 1}[/bold]")
            
            if statement.lower() == 'done':
                break
            
            if statement.strip():
                statements.append(statement)
                console.print(f"[green]✓ 추가됨: {statement[:50]}...[/green]")
        
        if not statements:
            console.print("[red]검증할 진술이 없습니다![/red]")
            return
        
        console.print(f"\n[bold]{len(statements)}개의 진술을 검증하는 중...[/bold]")
        
        for i, statement in enumerate(statements, 1):
            console.print(f"\n[cyan]처리 중 {i}/{len(statements)}:[/cyan] {statement[:100]}...")
            self._run_fact_check(statement, save_to_history=True)
    
    def check_from_file(self):
        """Load and check statements from a file"""
        console.print("\n[bold cyan]📁 파일 모드[/bold cyan]")
        
        file_path = Prompt.ask(
            "[bold]파일 경로 입력[/bold]",
            default="statements.txt"
        )
        
        try:
            path = Path(file_path)
            if not path.exists():
                console.print(f"[red]파일을 찾을 수 없습니다: {file_path}[/red]")
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                statements = [line.strip() for line in f if line.strip()]
            
            if not statements:
                console.print("[red]파일에 진술이 없습니다![/red]")
                return
            
            console.print(f"[green]✓ {file_path}에서 {len(statements)}개의 진술을 로드했습니다[/green]")
            
            for i, statement in enumerate(statements, 1):
                console.print(f"\n[cyan]처리 중 {i}/{len(statements)}:[/cyan] {statement[:100]}...")
                self._run_fact_check(statement, save_to_history=True)
                
        except Exception as e:
            console.print(f"[red]파일 읽기 오류: {e}[/red]")
    
    def view_history(self):
        """View the history of fact checks"""
        console.print("\n[bold cyan]📊 팩트체크 기록[/bold cyan]")
        
        if not self.history:
            console.print("[yellow]아직 기록이 없습니다.[/yellow]")
            return
        
        table = Table(title="최근 팩트체크", show_lines=True)
        table.add_column("시간", style="dim", width=20)
        table.add_column("진술", width=50)
        table.add_column("판정", width=15)
        table.add_column("신뢰도", width=10)
        
        for item in self.history[-10:]:  # Show last 10
            verdict_style = self._get_verdict_style(item.get('verdict', 'Unknown'))
            table.add_row(
                item.get('timestamp', 'N/A'),
                item.get('statement', 'N/A')[:50] + "...",
                f"[{verdict_style}]{item.get('verdict', 'N/A')}[/{verdict_style}]",
                f"{item.get('confidence', 0):.1f}%"
            )
        
        console.print(table)
        
        if Confirm.ask("[bold]기록을 파일로 내보내시겠습니까?[/bold]", default=False):
            self._export_history()
    
    def example_mode(self):
        """Run example fact-checks to demonstrate the system"""
        console.print("\n[bold cyan]💡 예시 모드[/bold cyan]")
        console.print("[dim]검증할 예시를 선택하세요:[/dim]\n")
        
        examples = {
            "1": "한국의 실업률은 2024년 3.5%이다",
            "2": "서울의 인구는 1000만명을 넘는다",
            "3": "코로나19 백신은 DNA를 변형시킨다",
            "4": "지구 온난화로 북극곰이 멸종 위기이다",
            "5": "비트코인 가격이 10만 달러를 돌파했다",
            "6": "한국이 2022 월드컵에서 우승했다"
        }
        
        for key, statement in examples.items():
            console.print(f"{key}. {statement}")
        
        choice = Prompt.ask(
            "[bold]예시 선택[/bold]",
            choices=list(examples.keys()),
            default="1"
        )
        
        statement = examples[choice]
        console.print(f"\n[bold]검증 중:[/bold] {statement}")
        self._run_fact_check(statement)
    
    def settings_menu(self):
        """Display settings menu"""
        console.print("\n[bold cyan]⚙️ 설정[/bold cyan]")
        
        settings = Panel(
            """[bold]현재 구성:[/bold]
            
• Model: Upstage Solar-pro2
• Agents: 5 (Academic, News, Statistics, Logic, Social)
• Process: 3-stage verification
• Cache: Enabled (Academic: 1hr, News: 30min, Social: 15min)
• Output: Rich console with markdown
• Results: Saved to ./results/
            
[dim]설정은 .env 파일을 통해 구성됩니다[/dim]
            """,
            title="시스템 설정",
            border_style="cyan"
        )
        console.print(settings)
        
        if Confirm.ask("[bold].env 설정을 보시겠습니까?[/bold]", default=False):
            self._show_env_status()
    
    def show_help(self):
        """Display help documentation"""
        help_text = """
# 📚 FactWave Help Documentation

## 🎯 Overview
FactWave uses 5 specialized AI agents to verify statements through a 3-stage process:

### Stage 1: Independent Analysis
Each agent analyzes the statement using their specialized tools:
- **Academic Agent** (25%): Scholarly sources via Semantic Scholar, ArXiv, Wikipedia
- **News Agent** (30%): Media verification via Naver News, NewsAPI
- **Statistics Agent** (20%): Government data via KOSIS, FRED, World Bank
- **Logic Agent** (15%): Logical consistency analysis
- **Social Agent** (10%): Social trends via Twitter/X

### Stage 2: Structured Debate
Agents review each other's findings and debate without accessing tools.

### Stage 3: Final Synthesis
Super Agent creates a weighted confidence matrix and delivers the final verdict.

## 🛠 Available Tools
- **Academic**: Semantic Scholar, ArXiv, Wikipedia, OpenAlex
- **News**: Naver News, NewsAPI, Google Fact Check, GDELT
- **Statistics**: KOSIS, FRED, World Bank, OWID RAG
- **Social**: Twitter/X Scraper, YouTube Data API

## 📊 Verdict Categories
- ✅ **True**: Fully accurate with strong evidence
- ✅ **Mostly True**: Accurate with minor inaccuracies
- ⚠️ **Half True**: Partially accurate but missing context
- ❌ **Mostly False**: Contains significant errors
- ❌ **False**: Demonstrably incorrect
- ❓ **Unverifiable**: Insufficient evidence

## 💡 Tips
1. Be specific with your statements for better results
2. Include dates and locations when relevant
3. Avoid subjective or opinion-based statements
4. Check the confidence scores for reliability

## 🔧 Troubleshooting
- **API Errors**: Check your .env file for correct API keys
- **Timeout Issues**: Complex queries may take 30-60 seconds
- **No Results**: Try rephrasing with more specific terms
        """
        
        console.print(Markdown(help_text))
        
        if Confirm.ask("\n[bold]키보드 단축키를 보시겠습니까?[/bold]", default=False):
            self._show_shortcuts()
    
    def _run_fact_check(self, statement: str, save_to_history: bool = True):
        """Execute the fact-checking process"""
        # Initialize crew if not already done
        if self.fact_checker is None:
            with console.status("[bold yellow]팩트체크 팀을 초기화하는 중...[/bold yellow]"):
                self.fact_checker = FactWaveCrew()
        
        # Start fact-checking with progress indicator
        start_time = datetime.now()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                # Create progress tasks
                task1 = progress.add_task("[cyan]1단계: 독립적 분석...", total=5)
                task2 = progress.add_task("[yellow]2단계: 전문가 토론...", total=5)
                task3 = progress.add_task("[green]3단계: 최종 종합...", total=1)
                
                # Run the fact check (simulated progress updates)
                progress.update(task1, advance=5)
                progress.update(task2, advance=5)
                
                result = self.fact_checker.check_fact(statement)
                
                progress.update(task3, advance=1)
            
            # Process and display results
            self._display_results(statement, result, start_time)
            
            # Save to history
            if save_to_history:
                self._save_to_history(statement, result)
            
            # Ask to save results
            if Confirm.ask("\n[bold]상세 결과를 파일에 저장하시겠습니까?[/bold]", default=False):
                self._save_results(statement, result)
                
        except Exception as e:
            console.print(f"\n[red]❌ 팩트체크 중 오류 발생: {e}[/red]")
            logger.error(f"Fact-checking error: {e}", exc_info=True)
    
    def _display_results(self, statement: str, result: Any, start_time: datetime):
        """Display the fact-checking results"""
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Extract results based on actual structure
        if isinstance(result, dict):
            final_verdict = result.get('final_verdict', 'Unknown')
            confidence = result.get('confidence', 0)
            summary = result.get('summary', 'No summary available')
            evidence = result.get('evidence', [])
        else:
            # Handle string result from crew
            final_verdict = self._extract_verdict(str(result))
            confidence = 0
            summary = str(result)[:500]
            evidence = []
        
        # Create results panel
        verdict_style = self._get_verdict_style(final_verdict)
        
        results_panel = Panel(
            f"""[bold]📝 진술:[/bold]
{statement}

[bold]⚖️ 최종 판정:[/bold] [{verdict_style}]{final_verdict}[/{verdict_style}]
[bold]📊 신뢰도:[/bold] {confidence:.1f}%
[bold]⏱️ 처리 시간:[/bold] {elapsed:.2f}초

[bold]📋 요약:[/bold]
{summary}
            """,
            title="🏆 팩트체크 결과",
            border_style=verdict_style
        )
        
        console.print("\n")
        console.print(results_panel)
        
        # Display evidence if available
        if evidence:
            self._display_evidence(evidence)
    
    def _display_evidence(self, evidence: List[Dict[str, Any]]):
        """Display evidence in a table"""
        table = Table(title="📚 지원 증거", show_lines=True)
        table.add_column("출처", style="cyan", width=20)
        table.add_column("유형", width=15)
        table.add_column("증거", width=50)
        table.add_column("신뢰도", width=10)
        
        for item in evidence[:5]:  # Show top 5
            table.add_row(
                item.get('source', 'N/A'),
                item.get('type', 'N/A'),
                item.get('content', 'N/A')[:100] + "...",
                f"{item.get('reliability', 0):.0f}%"
            )
        
        console.print(table)
    
    def _save_to_history(self, statement: str, result: Any):
        """Save fact-check to history"""
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'statement': statement,
            'verdict': self._extract_verdict(str(result)),
            'confidence': 0,  # Extract from result if available
            'result': str(result)[:1000]
        }
        self.history.append(entry)
    
    def _save_results(self, statement: str, result: Any):
        """Save detailed results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"factcheck_{timestamp}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'statement': statement,
            'result': str(result),
            'metadata': {
                'model': 'solar-pro2',
                'agents': 5,
                'stages': 3
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        console.print(f"[green]✓ 결과가 {filename}에 저장되었습니다[/green]")
    
    def _export_history(self):
        """Export history to CSV file"""
        import csv
        
        filename = self.results_dir / f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'statement', 'verdict', 'confidence'])
            writer.writeheader()
            writer.writerows(self.history)
        
        console.print(f"[green]✓ 기록이 {filename}으로 내보내졌습니다[/green]")
    
    def _extract_verdict(self, result_text: str) -> str:
        """Extract verdict from result text"""
        verdicts = ['True', 'Mostly True', 'Half True', 'Mostly False', 'False', 'Unverifiable']
        result_lower = result_text.lower()
        
        for verdict in verdicts:
            if verdict.lower() in result_lower:
                return verdict
        
        return 'Unknown'
    
    def _get_verdict_style(self, verdict: str) -> str:
        """Get style for verdict display"""
        styles = {
            'True': 'green',
            'Mostly True': 'green',
            'Half True': 'yellow',
            'Mostly False': 'red',
            'False': 'red',
            'Unverifiable': 'dim',
            'Unknown': 'dim'
        }
        return styles.get(verdict, 'white')
    
    def _show_env_status(self):
        """Show environment variable status"""
        env_vars = [
            'UPSTAGE_API_KEY',
            'NAVER_CLIENT_ID',
            'NAVER_CLIENT_SECRET',
            'NEWSAPI_KEY',
            'GOOGLE_FACT_CHECK_API_KEY',
            'FRED_API_KEY',
            'KOSIS_API_KEY',
            'YOUTUBE_API_KEY'
        ]
        
        table = Table(title="API 구성 상태")
        table.add_column("API", style="cyan")
        table.add_column("상태", style="green")
        
        for var in env_vars:
            status = "✅ 구성됨" if os.getenv(var) else "❌ 미설정"
            table.add_row(var, status)
        
        console.print(table)
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts = Panel(
            """[bold]키보드 단축키:[/bold]
            
• Ctrl+C: 현재 작업 취소
• Ctrl+D: 애플리케이션 종료
• Tab: 자동 완성
• ↑/↓: 기록 탐색
• Enter: 선택 확인
            """,
            title="단축키",
            border_style="cyan"
        )
        console.print(shortcuts)
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        
        while True:
            try:
                choice = self.display_menu()
                
                if choice == "1":
                    self.single_fact_check()
                elif choice == "2":
                    self.batch_verification()
                elif choice == "3":
                    self.check_from_file()
                elif choice == "4":
                    self.view_history()
                elif choice == "5":
                    self.example_mode()
                elif choice == "6":
                    self.settings_menu()
                elif choice == "7":
                    self.show_help()
                elif choice == "8":
                    if Confirm.ask("\n[bold]정말 종료하시겠습니까?[/bold]", default=False):
                        console.print("\n[bold cyan]FactWave를 이용해 주셔서 감사합니다! 👋[/bold cyan]")
                        break
                
                if choice != "8":
                    input("\n[dim]계속하려면 Enter를 누르세요...[/dim]")
                    console.clear()
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]작업이 취소되었습니다.[/yellow]")
                if Confirm.ask("[bold]애플리케이션을 종료하시겠습니까?[/bold]", default=False):
                    break
            except Exception as e:
                console.print(f"\n[red]예상치 못한 오류: {e}[/red]")
                logger.error(f"Application error: {e}", exc_info=True)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="FactWave - AI 기반 다중 에이전트 팩트체크 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "statement",
        nargs="?",
        help="검증할 진술 (선택사항 - 제공되지 않으면 대화형 모드 실행)"
    )
    
    parser.add_argument(
        "-b", "--batch",
        action="store_true",
        help="일괄 모드로 실행"
    )
    
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="파일에서 진술 로드"
    )
    
    parser.add_argument(
        "-e", "--example",
        action="store_true",
        help="예시 팩트체크 실행"
    )
    
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="결과를 파일에 저장"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="최소 출력 모드"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="상세 출력 모드"
    )
    
    args = parser.parse_args()
    
    # Create interface
    interface = FactWaveInterface()
    
    try:
        if args.statement:
            # Direct fact-check mode
            console.print(f"[bold]검증 중:[/bold] {args.statement}")
            interface._run_fact_check(args.statement)
        elif args.batch:
            # Batch mode
            interface.batch_verification()
        elif args.file:
            # File mode
            interface.check_from_file()
        elif args.example:
            # Example mode
            interface.example_mode()
        else:
            # Interactive mode
            interface.run()
            
    except KeyboardInterrupt:
        console.print("\n[yellow]사용자에 의해 중단되었습니다.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]치명적 오류: {e}[/red]")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()