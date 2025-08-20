"""YouTube Video Analyzer 테스트 스크립트"""

import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 경로에 추가
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from app.services.tools.verification.youtube_video_analyzer import YouTubeVideoAnalyzer

console = Console()


async def test_video_analysis():
    """YouTube 영상 분석 테스트"""
    
    # API 키 확인
    if not os.getenv('GOOGLE_API_KEY') and not os.getenv('GEMINI_API_KEY'):
        console.print("[red]❌ GOOGLE_API_KEY 또는 GEMINI_API_KEY가 설정되지 않았습니다.[/red]")
        console.print("[yellow]📌 .env 파일에 API 키를 추가해주세요:[/yellow]")
        console.print("   GOOGLE_API_KEY=your_key_here")
        return
    
    try:
        # 분석기 초기화
        console.print("\n[blue]🎬 YouTube Video Analyzer 초기화 중...[/blue]")
        analyzer = YouTubeVideoAnalyzer()
        
        # 테스트할 YouTube URL들
        test_videos = [
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "description": "Rick Astley - Never Gonna Give You Up (테스트용 짧은 영상)"
            },
            {
                "url": "https://youtu.be/9bZkp7q19f0",
                "description": "PSY - GANGNAM STYLE (다른 URL 형식 테스트)"
            }
        ]
        
        for video in test_videos:
            console.print(f"\n[yellow]📹 분석 중: {video['description']}[/yellow]")
            console.print(f"   URL: {video['url']}")
            
            # 1. 종합 분석
            console.print("\n[green]1️⃣ 종합 분석 (Comprehensive Analysis)[/green]")
            result = await analyzer.analyze_video(video['url'], "comprehensive")
            
            if result["status"] == "success":
                console.print(Panel(
                    result["content"],
                    title="📊 영상 분석 결과",
                    border_style="green"
                ))
            else:
                console.print(f"[red]❌ 분석 실패: {result['error']}[/red]")
                continue
            
            # 2. 팩트체킹용 주장 추출
            console.print("\n[green]2️⃣ 팩트체킹용 주장 추출[/green]")
            claims_result = await analyzer.extract_claims_for_factcheck(video['url'])
            
            if claims_result["status"] == "success":
                console.print(f"[cyan]📝 추출된 주장 수: {claims_result['claims_count']}개[/cyan]")
                
                if claims_result.get("extracted_claims"):
                    console.print("\n[bold]주요 주장들:[/bold]")
                    for i, claim in enumerate(claims_result["extracted_claims"][:5], 1):
                        console.print(f"  {i}. {claim}")
                
                if claims_result.get("factcheck_statement"):
                    console.print(Panel(
                        claims_result["factcheck_statement"],
                        title="🔍 팩트체킹할 문장",
                        border_style="cyan"
                    ))
            else:
                console.print(f"[red]❌ 주장 추출 실패: {claims_result.get('error', 'Unknown error')}[/red]")
            
            # 잠시 대기 (API 레이트 리밋 고려)
            await asyncio.sleep(2)
        
        console.print("\n[green]✅ 모든 테스트 완료![/green]")
        
    except Exception as e:
        console.print(f"\n[red]❌ 테스트 중 오류 발생: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())


async def test_websocket_integration():
    """WebSocket 통합 테스트"""
    
    console.print("\n[blue]🌐 WebSocket 통합 테스트[/blue]")
    console.print("[yellow]📌 이 테스트를 실행하려면 먼저 API 서버를 시작해야 합니다:[/yellow]")
    console.print("   cd backend && python -m app.api.server")
    
    import websockets
    import json
    
    try:
        # WebSocket 연결
        uri = "ws://localhost:8000/ws/test_youtube_session"
        
        async with websockets.connect(uri) as websocket:
            console.print("[green]✅ WebSocket 연결 성공[/green]")
            
            # 연결 확인 메시지 수신
            response = await websocket.recv()
            console.print(f"[cyan]서버 응답: {response}[/cyan]")
            
            # YouTube 분석 요청
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            request = {
                "action": "analyze_youtube",
                "url": test_url
            }
            
            console.print(f"\n[yellow]📤 YouTube 분석 요청 전송:[/yellow]")
            console.print(f"   URL: {test_url}")
            
            await websocket.send(json.dumps(request))
            
            # 응답 수신
            console.print("\n[blue]📥 서버 응답 수신 중...[/blue]")
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "youtube_analysis_started":
                        console.print("[yellow]🎬 YouTube 영상 분석 시작[/yellow]")
                    
                    elif data.get("type") == "youtube_analysis_complete":
                        console.print("[green]✅ YouTube 영상 분석 완료[/green]")
                        if data.get("content", {}).get("claims"):
                            console.print(f"   추출된 주장: {data['content']['claims_count']}개")
                    
                    elif data.get("type") == "fact_check_started":
                        console.print("[yellow]🔍 팩트체킹 시작[/yellow]")
                        console.print(f"   검증 문장: {data.get('content', {}).get('statement', '')[:100]}...")
                    
                    elif data.get("type") == "final_result":
                        console.print("[green]✅ 팩트체킹 완료![/green]")
                        result = data.get("content", {})
                        if result.get("final_verdict"):
                            console.print(f"   최종 판정: {result['final_verdict']}")
                        break
                    
                    elif data.get("type") == "error":
                        console.print(f"[red]❌ 오류: {data.get('content', {}).get('error')}[/red]")
                        break
                    
                    else:
                        console.print(f"[dim]   {data.get('type', 'unknown')}: 처리 중...[/dim]")
                
                except asyncio.TimeoutError:
                    console.print("[yellow]⏱️ 응답 시간 초과[/yellow]")
                    break
            
    except Exception as e:
        console.print(f"[red]❌ WebSocket 테스트 실패: {str(e)}[/red]")
        console.print("[yellow]💡 API 서버가 실행 중인지 확인하세요[/yellow]")


async def main():
    """메인 테스트 함수"""
    
    console.print(Panel(
        "🎥 YouTube Video Analyzer 테스트 스크립트",
        style="bold blue"
    ))
    
    console.print("\n테스트 옵션:")
    console.print("1. YouTube 영상 분석 테스트 (Gemini API)")
    console.print("2. WebSocket 통합 테스트")
    console.print("3. 모든 테스트 실행")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        await test_video_analysis()
    elif choice == "2":
        await test_websocket_integration()
    elif choice == "3":
        await test_video_analysis()
        console.print("\n" + "="*50 + "\n")
        await test_websocket_integration()
    else:
        console.print("[red]잘못된 선택입니다.[/red]")


if __name__ == "__main__":
    asyncio.run(main())