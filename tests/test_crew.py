#!/usr/bin/env python
"""FactWave Crew 통합 테스트"""

import sys
import asyncio
from app.core import FactWaveCrew
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def test_factcheck():
    """팩트체크 테스트 실행"""
    
    # 테스트 케이스들
    test_cases = [
        "한국의 실업률은 3%이다",
        "AI가 인간의 일자리를 모두 대체할 것이다",
        "지구 온난화는 거짓이다"
    ]
    
    console.print("\n[bold cyan]🚀 FactWave 통합 테스트[/bold cyan]")
    console.print("=" * 60)
    
    # 사용자 입력 또는 테스트 케이스 선택
    console.print("\n테스트 옵션:")
    console.print("1. 예제 테스트 케이스 사용")
    console.print("2. 직접 입력")
    
    choice = Prompt.ask("선택", choices=["1", "2"], default="1")
    
    if choice == "1":
        console.print("\n테스트 케이스:")
        for i, case in enumerate(test_cases, 1):
            console.print(f"{i}. {case}")
        
        case_num = Prompt.ask("케이스 번호", default="1")
        statement = test_cases[int(case_num) - 1]
    else:
        statement = Prompt.ask("\n검증할 주장을 입력하세요")
    
    console.print(f"\n[bold yellow]검증 주장: {statement}[/bold yellow]\n")
    
    # FactWave Crew 실행
    try:
        crew = FactWaveCrew()
        result = crew.check_fact(statement)
        
        console.print("\n[bold green]✅ 팩트체크 완료![/bold green]")
        console.print("=" * 60)
        
        # 결과 출력
        if result:
            console.print("\n[bold]최종 판정:[/bold]")
            console.print(result.get("final_verdict", "판정 없음"))
            
            console.print("\n[bold]신뢰도 매트릭스:[/bold]")
            if "confidence_matrix" in result:
                for agent, data in result["confidence_matrix"].items():
                    console.print(f"  • {agent}: {data.get('verdict', 'N/A')} (신뢰도: {data.get('confidence', 0)}%)")
            
            console.print("\n[bold]상세 분석:[/bold]")
            console.print(result.get("detailed_analysis", "분석 없음"))
        
    except Exception as e:
        console.print(f"[red]❌ 오류 발생: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    test_factcheck()