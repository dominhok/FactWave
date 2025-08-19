"""
FactWave FastAPI Backend Server
실시간 WebSocket 스트리밍을 통한 팩트체킹 API
"""

import os
import sys

# UTF-8 인코딩 강제 설정
if os.name == 'nt':  # Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Windows 콘솔에서 유니코드 지원
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Korean_Korea.65001')
        except:
            pass
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 프로젝트 imports
from app.core.streaming_crew import StreamingFactWaveCrew
from app.utils.websocket_manager import WebSocketManager

# 환경 설정
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 설정 - OpenAI GPT-4.1-mini 사용
# OPENAI_API_KEY는 .env에서 직접 로드됨


# ==================== 데이터 모델 ====================

class FactCheckRequest(BaseModel):
    """팩트체킹 요청 모델"""
    statement: str = Field(..., description="검증할 진술", min_length=5, max_length=1000)
    language: str = Field(default="ko", description="언어 설정 (ko/en)")
    session_id: Optional[str] = Field(default=None, description="세션 ID (재연결용)")


class FactCheckResponse(BaseModel):
    """팩트체킹 응답 모델"""
    request_id: str = Field(..., description="요청 ID")
    status: str = Field(..., description="처리 상태")
    message: str = Field(..., description="상태 메시지")
    session_id: Optional[str] = Field(None, description="WebSocket 세션 ID")


class WebSocketMessage(BaseModel):
    """WebSocket 메시지 포맷"""
    type: str = Field(..., description="메시지 타입")
    step: Optional[str] = Field(None, description="현재 단계 (step1/step2/step3)")
    agent: Optional[str] = Field(None, description="현재 에이전트")
    content: Any = Field(..., description="메시지 내용")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = Field(default={})


# ==================== WebSocket 매니저 ====================

class ConnectionManager:
    """WebSocket 연결 관리"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.fact_checkers: Dict[str, StreamingFactWaveCrew] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """WebSocket 연결"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_data[session_id] = {
            "connected_at": datetime.now().isoformat(),
            "status": "connected"
        }
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """WebSocket 연결 해제"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_data:
            self.session_data[session_id]["status"] = "disconnected"
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: WebSocketMessage):
        """특정 세션에 메시지 전송"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message.dict())
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_to_session(self, session_id: str, data: Dict[str, Any]):
        """세션에 브로드캐스트"""
        message = WebSocketMessage(
            type=data.get("type", "update"),
            step=data.get("step"),
            agent=data.get("agent"),
            content=data.get("content", {}),
            metadata=data.get("metadata", {})
        )
        await self.send_message(session_id, message)
    
    def get_or_create_checker(self, session_id: str) -> StreamingFactWaveCrew:
        """팩트체커 인스턴스 가져오기 또는 생성"""
        if session_id not in self.fact_checkers:
            self.fact_checkers[session_id] = StreamingFactWaveCrew(
                websocket_callback=lambda data: asyncio.create_task(
                    self.broadcast_to_session(session_id, data)
                )
            )
        return self.fact_checkers[session_id]
    
    def cleanup_session(self, session_id: str):
        """세션 정리"""
        if session_id in self.fact_checkers:
            del self.fact_checkers[session_id]
        if session_id in self.session_data:
            del self.session_data[session_id]


# ==================== FastAPI 앱 설정 ====================

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    logger.info("FactWave API 서버 시작")
    yield
    logger.info("FactWave API 서버 종료")


app = FastAPI(
    title="FactWave API",
    description="AI 기반 다중 에이전트 팩트체킹 시스템 API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 설정 (크롬 익스텐션 연결용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",  # 크롬 익스텐션
        "http://localhost:*",    # 로컬 개발
        "http://127.0.0.1:*",    # 로컬 개발
        "*"  # 개발 중에는 모든 origin 허용 (프로덕션에서는 제한 필요)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HTTP 엔드포인트 ====================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "FactWave API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "websocket": "/ws/{session_id}",
            "fact_check": "/api/fact-check",
            "health": "/health",
            "sessions": "/api/sessions"
        }
    }


@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(manager.active_connections),
        "uptime": "running"
    }


@app.post("/api/fact-check", response_model=FactCheckResponse)
async def initiate_fact_check(request: FactCheckRequest):
    """팩트체킹 요청 시작 (WebSocket 연결 필요)"""
    request_id = str(uuid4())
    session_id = request.session_id or str(uuid4())
    
    return FactCheckResponse(
        request_id=request_id,
        status="pending",
        message=f"WebSocket 연결이 필요합니다. /ws/{session_id} 에 연결하세요.",
        session_id=session_id
    )


@app.get("/api/sessions")
async def get_active_sessions():
    """활성 세션 목록"""
    return {
        "active_sessions": list(manager.active_connections.keys()),
        "total": len(manager.active_connections),
        "details": {
            sid: data for sid, data in manager.session_data.items()
            if data.get("status") == "connected"
        }
    }


@app.delete("/api/sessions/{session_id}")
async def close_session(session_id: str):
    """세션 종료"""
    if session_id in manager.active_connections:
        manager.disconnect(session_id)
        manager.cleanup_session(session_id)
        return {"status": "closed", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


# ==================== WebSocket 엔드포인트 ====================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket 엔드포인트 - 실시간 팩트체킹 스트리밍
    
    메시지 프로토콜:
    - Client -> Server: {"action": "start", "statement": "검증할 문장"}
    - Server -> Client: {
        "type": "agent_start|agent_complete|tool_call|step_complete|final_result|error",
        "step": "step1|step2|step3",
        "agent": "academic|news|logic|social|statistics|super",
        "content": {...},
        "timestamp": "ISO 8601"
    }
    """
    await manager.connect(websocket, session_id)
    
    try:
        # 연결 확인 메시지
        await manager.send_message(session_id, WebSocketMessage(
            type="connection_established",
            content={"session_id": session_id, "status": "ready"},
            metadata={"version": "2.0.0"}
        ))
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "start":
                # 팩트체킹 시작
                statement = data.get("statement")
                if not statement:
                    await manager.send_message(session_id, WebSocketMessage(
                        type="error",
                        content={"error": "No statement provided"}
                    ))
                    continue
                
                # 시작 메시지
                await manager.send_message(session_id, WebSocketMessage(
                    type="fact_check_started",
                    content={
                        "statement": statement,
                        "timestamp": datetime.now().isoformat()
                    }
                ))
                
                # 팩트체커 가져오기
                fact_checker = manager.get_or_create_checker(session_id)
                
                # 비동기로 팩트체킹 실행
                try:
                    # 팩트체킹 실행 (스트리밍 콜백과 함께)
                    result = await asyncio.create_task(
                        fact_checker.check_fact_async(statement)
                    )
                    
                    # 최종 결과 전송
                    await manager.send_message(session_id, WebSocketMessage(
                        type="final_result",
                        content=result,
                        metadata={"completed_at": datetime.now().isoformat()}
                    ))
                    
                except Exception as e:
                    logger.error(f"Fact-checking error: {e}")
                    await manager.send_message(session_id, WebSocketMessage(
                        type="error",
                        content={"error": str(e), "details": "팩트체킹 중 오류가 발생했습니다."}
                    ))
            
            elif action == "ping":
                # 연결 유지용 ping
                await manager.send_message(session_id, WebSocketMessage(
                    type="pong",
                    content={"timestamp": datetime.now().isoformat()}
                ))
            
            elif action == "stop":
                # 현재 작업 중단
                if session_id in manager.fact_checkers:
                    # TODO: 작업 중단 로직 구현
                    await manager.send_message(session_id, WebSocketMessage(
                        type="stopped",
                        content={"message": "Fact-checking stopped"}
                    ))
            
            else:
                # 알 수 없는 액션
                await manager.send_message(session_id, WebSocketMessage(
                    type="error",
                    content={"error": f"Unknown action: {action}"}
                ))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)
    finally:
        # 연결 종료 시 정리
        if session_id in manager.active_connections:
            manager.disconnect(session_id)


# ==================== 에러 핸들러 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.api.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )