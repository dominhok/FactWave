"""
WebSocket Manager for FactWave
실시간 통신 관리 유틸리티
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    """스트리밍 이벤트 데이터 클래스"""
    type: str  # agent_start, agent_complete, tool_call, step_complete, etc.
    step: Optional[str] = None  # step1, step2, step3
    agent: Optional[str] = None  # academic, news, logic, social, statistics, super
    tool: Optional[str] = None  # 사용된 도구 이름
    content: Any = None  # 실제 컨텐츠
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {k: v for k, v in asdict(self).items() if v is not None}


class WebSocketManager:
    """WebSocket 통신 관리자"""
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Args:
            callback: WebSocket으로 메시지를 보낼 콜백 함수
        """
        self.callback = callback
        self.event_queue: List[StreamEvent] = []
        self.is_streaming = False
        
    async def emit(self, event_data):
        """이벤트 발생 (StreamEvent 또는 dict 모두 지원)"""
        # dict가 직접 전달되는 경우 처리
        if isinstance(event_data, dict):
            event = StreamEvent(
                type=event_data.get("type", "update"),
                step=event_data.get("step"),
                agent=event_data.get("agent"),
                tool=event_data.get("tool"),
                content=event_data.get("content"),
                metadata=event_data.get("metadata")
            )
        else:
            event = event_data
        
        self.event_queue.append(event)
        
        if self.callback:
            try:
                await self.callback(event.to_dict())
            except Exception as e:
                logger.error(f"Error emitting event: {e}")
    
    async def emit_agent_start(self, step: str, agent: str, task: str):
        """에이전트 시작 이벤트"""
        await self.emit(StreamEvent(
            type="agent_start",
            step=step,
            agent=agent,
            content={
                "message": f"{agent} 에이전트가 분석을 시작합니다",
                "task": task
            }
        ))
    
    async def emit_agent_complete(self, step: str, agent: str, result: Any):
        """에이전트 완료 이벤트"""
        await self.emit(StreamEvent(
            type="agent_complete",
            step=step,
            agent=agent,
            content={
                "message": f"{agent} 에이전트가 분석을 완료했습니다",
                "result": result
            }
        ))
    
    async def emit_tool_call(self, step: str, agent: str, tool: str, 
                            tool_input: Any, tool_output: Any):
        """도구 호출 이벤트"""
        await self.emit(StreamEvent(
            type="tool_call",
            step=step,
            agent=agent,
            tool=tool,
            content={
                "input": tool_input,
                "output": tool_output
            }
        ))
    
    async def emit_step_start(self, step: str, description: str):
        """단계 시작 이벤트"""
        step_names = {
            "step1": "독립적 분석",
            "step2": "전문가 토론",
            "step3": "최종 종합"
        }
        
        await self.emit(StreamEvent(
            type="step_start",
            step=step,
            content={
                "name": step_names.get(step, step),
                "description": description
            }
        ))
    
    async def emit_step_complete(self, step: str, summary: Dict[str, Any]):
        """단계 완료 이벤트"""
        await self.emit(StreamEvent(
            type="step_complete",
            step=step,
            content={
                "summary": summary
            }
        ))
    
    async def emit_final_result(self, verdict: str, confidence: float, 
                               analysis: Dict[str, Any]):
        """최종 결과 이벤트"""
        await self.emit(StreamEvent(
            type="final_result",
            content={
                "verdict": verdict,
                "confidence": confidence,
                "analysis": analysis
            }
        ))
    
    async def emit_error(self, error: str, details: Optional[Dict[str, Any]] = None):
        """에러 이벤트"""
        await self.emit(StreamEvent(
            type="error",
            content={
                "error": error,
                "details": details or {}
            }
        ))
    
    async def emit_progress(self, step: str, progress: float, message: str):
        """진행 상황 업데이트"""
        await self.emit(StreamEvent(
            type="progress",
            step=step,
            content={
                "progress": progress,  # 0.0 ~ 1.0
                "message": message
            }
        ))
    
    def get_event_history(self) -> List[Dict[str, Any]]:
        """이벤트 히스토리 반환"""
        return [event.to_dict() for event in self.event_queue]
    
    def clear_history(self):
        """이벤트 히스토리 초기화"""
        self.event_queue.clear()


class StreamingCallback:
    """CrewAI와 WebSocket을 연결하는 콜백 클래스"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.manager = websocket_manager
        self.current_step = None
        self.current_agent = None
        
    async def on_task_start(self, agent: str, task: str, step: str):
        """Task 시작 시 호출"""
        self.current_step = step
        self.current_agent = agent
        await self.manager.emit_agent_start(step, agent, task)
    
    async def on_task_complete(self, agent: str, result: Any, step: str):
        """Task 완료 시 호출"""
        await self.manager.emit_agent_complete(step, agent, result)
    
    async def on_tool_use(self, agent: str, tool_name: str, 
                          tool_input: Any, tool_output: Any):
        """도구 사용 시 호출"""
        if self.current_step and self.current_agent:
            await self.manager.emit_tool_call(
                self.current_step, 
                agent, 
                tool_name, 
                tool_input, 
                tool_output
            )
    
    async def on_step_change(self, step: str, description: str):
        """단계 변경 시 호출"""
        self.current_step = step
        await self.manager.emit_step_start(step, description)
    
    async def on_step_complete(self, step: str, results: Dict[str, Any]):
        """단계 완료 시 호출"""
        await self.manager.emit_step_complete(step, results)
    
    async def on_final_result(self, verdict: str, confidence: float, 
                             full_analysis: Dict[str, Any]):
        """최종 결과 생성 시 호출"""
        await self.manager.emit_final_result(verdict, confidence, full_analysis)
    
    async def on_error(self, error: Exception, context: Dict[str, Any]):
        """에러 발생 시 호출"""
        await self.manager.emit_error(str(error), context)