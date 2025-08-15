#!/usr/bin/env python
"""FactWave Crew 자동 통합 테스트"""

import sys
from app.core import FactWaveCrew
from rich.console import Console

console = Console()

def test_factcheck():
    """팩트체크 자동 테스트"""
    
    # 간단한 테스트 케이스
    statement = "한국의 실업률은 현재 3%이다"
    
    console.print("\n[bold cyan]🚀 FactWave 자동 통합 테스트[/bold cyan]")
    console.print("=" * 60)
    console.print(f"\n[bold yellow]검증 주장: {statement}[/bold yellow]\n")
    
    # FactWave Crew 실행
    try:
        crew = FactWaveCrew()
        
        console.print("🔄 팩트체크 프로세스 시작...\n")
        
        # 타임아웃 설정하여 실행
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("팩트체크 타임아웃 (60초)")
        
        # 60초 타임아웃 설정
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)
        
        try:
            result = crew.check_fact(statement)
            signal.alarm(0)  # 타임아웃 해제
        except TimeoutError as e:
            console.print(f"[yellow]⏱️ {str(e)}[/yellow]")
            return
        
        console.print("\n[bold green]✅ 팩트체크 완료![/bold green]")
        console.print("=" * 60)
        
        # 결과 출력
        if result:
            console.print("\n[bold]📊 최종 결과:[/bold]")
            
            # 최종 판정
            verdict = result.get("final_verdict", "판정 없음")
            console.print(f"\n🏆 최종 판정: [bold]{verdict}[/bold]")
            
            # 신뢰도 매트릭스
            if "confidence_matrix" in result:
                console.print("\n📈 에이전트별 판정:")
                for agent, data in result["confidence_matrix"].items():
                    verdict = data.get('verdict', 'N/A')
                    confidence = data.get('confidence', 0)
                    console.print(f"  • {agent:15} : {verdict:15} (신뢰도: {confidence}%)")
            
            # 합의점
            if "consensus" in result:
                console.print(f"\n✅ 합의점: {result['consensus']}")
            
            # 불일치점
            if "disagreements" in result:
                console.print(f"\n⚠️ 불일치점: {result['disagreements']}")
            
            # 상세 분석 (처음 500자만)
            if "detailed_analysis" in result:
                analysis = result["detailed_analysis"]
                if len(analysis) > 500:
                    analysis = analysis[:500] + "..."
                console.print(f"\n📝 상세 분석:\n{analysis}")
        else:
            console.print("[yellow]결과가 없습니다.[/yellow]")
        
    except Exception as e:
        console.print(f"\n[red]❌ 오류 발생: {str(e)}[/red]")
        
        # 간단한 오류 정보만 출력
        import traceback
        tb = traceback.format_exc()
        # 마지막 몇 줄만 출력
        lines = tb.split('\n')
        for line in lines[-5:]:
            if line.strip():
                console.print(f"[dim]{line}[/dim]")

if __name__ == "__main__":
    test_factcheck()