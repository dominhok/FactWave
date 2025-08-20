dk#!/usr/bin/env python3
"""
FactWave API Server Runner
실행: python run_server.py 또는 uv run python run_server.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 환경 변수 로드 - 루트 디렉토리의 .env 파일
from pathlib import Path
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

def main():
    """메인 서버 실행 함수"""
    
    # 서버 설정
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "development") == "development"
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                     🌊 FactWave API Server                       ║
║                                                                   ║
║  AI-Powered Multi-Agent Fact-Checking System                     ║
║  WebSocket Streaming API for Real-time Analysis                  ║
╚═══════════════════════════════════════════════════════════════════╝

📡 서버 시작 중...
🌐 Host: {host}
🔌 Port: {port}
🔄 Auto-reload: {'활성화' if reload else '비활성화'}

📚 API 문서:
   - Swagger UI: http://localhost:{port}/docs
   - ReDoc: http://localhost:{port}/redoc
   - WebSocket: ws://localhost:{port}/ws/{{session_id}}

🎯 테스트 페이지: http://localhost:{port}/test

Ctrl+C를 눌러 서버를 종료할 수 있습니다.
""")
    
    try:
        # Uvicorn 서버 실행
        uvicorn.run(
            "app.api.server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 서버를 종료합니다...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()