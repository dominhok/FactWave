"""
Streaming FactWave Crew - WebSocket 스트리밍을 지원하는 팩트체킹 시스템
실제 FactWaveCrew와 연동하여 실시간 스트리밍 제공
"""

import asyncio
import json
import logging
import concurrent.futures
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from crewai import Agent, Task, Crew, Process

from ..agents import (
    AcademicAgent, NewsAgent, SocialAgent, 
    LogicAgent, StatisticsAgent, SuperAgent
)
from ..utils.websocket_manager import WebSocketManager, StreamingCallback
from ..utils.prompt_loader import PromptLoader
from .crew import FactWaveCrew

logger = logging.getLogger(__name__)


class StreamingFactWaveCrew:
    """WebSocket 스트리밍을 지원하는 3단계 팩트체킹 프로세스"""
    
    def __init__(self, websocket_callback: Optional[Callable] = None):
        """
        Args:
            websocket_callback: WebSocket으로 메시지를 보낼 콜백 함수
        """
        # 프롬프트 로더 초기화
        self.prompt_loader = PromptLoader()
        
        # YAML에서 설정 로드
        self.VERDICT_OPTIONS = self.prompt_loader.get_verdict_options()
        self.AGENT_WEIGHTS = self.prompt_loader.get_agent_weights()
        
        # WebSocket 관리자 설정
        self.ws_manager = WebSocketManager(callback=websocket_callback)
        self.streaming_callback = StreamingCallback(self.ws_manager)
        
        # Task 콜백 생성 (동기 함수로 래핑)
        def task_callback(task_event):
            # Task 이벤트를 WebSocket으로 전송
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self._handle_task_event(task_event))
                else:
                    loop.run_until_complete(self._handle_task_event(task_event))
            except RuntimeError:
                # 루프가 없거나 실행 중이 아닌 경우 새 스레드에서 실행
                import threading
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(self._handle_task_event(task_event))
                    new_loop.close()
                thread = threading.Thread(target=run_async)
                thread.start()
        
        # 실제 FactWaveCrew 인스턴스 사용 (task_callback 전달)
        self.fact_crew = FactWaveCrew(task_callback=task_callback)
        
        # FactWaveCrew의 콜백을 WebSocket 스트리밍으로 대체
        self.fact_crew._step_callback = self._websocket_step_callback
        
        # 현재 상태 추적
        self.current_step = None
        self.current_agent = None
        self.step_start_times = {}
        self.last_agent_outputs = {}
        
        # executor for async operations
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    
    async def _handle_task_event(self, task_event: Dict[str, Any]):
        """
        Task 이벤트 처리 (Task 시작/완료 시 즉시 전송)
        """
        try:
            event_type = task_event.get("type")
            status = task_event.get("status")
            agent = task_event.get("agent")
            step = task_event.get("step")
            
            if event_type == "task_status":
                if status == "started":
                    # Task 시작 즉시 알림
                    await self.ws_manager.emit({
                        "type": "task_started",
                        "step": step,
                        "agent": agent,
                        "content": {
                            "message": f"{self.fact_crew.agents[agent].role} 작업 시작",
                            "task_id": str(task_event.get("task_id", ""))[:8],
                            "role": self.fact_crew.agents[agent].role
                        }
                    })
                    logger.info(f"Task started: {agent} in {step}")
                    
                elif status == "completed":
                    # Task 완료 즉시 알림
                    output = task_event.get("output", "")
                    
                    # 분석 결과 추출
                    analysis = self._extract_full_answer(output) if output else "완료"
                    verdict = self._extract_verdict(output) if output else "분석중"
                    confidence = self._extract_confidence(output) if output else 0.5
                    
                    await self.ws_manager.emit({
                        "type": "task_completed",
                        "step": step,
                        "agent": agent,
                        "content": {
                            "message": f"{self.fact_crew.agents[agent].role} 작업 완료",
                            "analysis": analysis,  # 전체 JSON 응답 전송
                            "verdict": verdict,
                            "confidence": confidence,
                            "role": self.fact_crew.agents[agent].role
                        }
                    })
                    logger.info(f"Task completed: {agent} in {step}")
                    
                    # 에이전트 완료 상태 업데이트
                    if agent not in self.fact_crew.completed_agents[step]:
                        self.fact_crew.completed_agents[step].append(agent)
                    
                    # 단계 완료 체크
                    if self._is_step_complete(step):
                        await self._handle_step_completion(step)
        
        except Exception as e:
            logger.error(f"Task event handling error: {e}")
            await self.ws_manager.emit_error(str(e), {"task_event": task_event})
    
    def _websocket_step_callback(self, agent_output: Any):
        """FactWaveCrew의 step_callback을 WebSocket 스트리밍으로 대체 (동기 버전)"""
        try:
            # 비동기 함수를 동기적으로 실행
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 이미 실행중인 루프가 있는 경우, 태스크를 스케줄링
                    asyncio.create_task(self._async_websocket_step_callback(agent_output))
                else:
                    # 루프가 없는 경우, 새로 실행
                    loop.run_until_complete(self._async_websocket_step_callback(agent_output))
            except RuntimeError:
                # 루프가 실행중이지만 create_task가 실패한 경우, 새 스레드에서 실행
                import threading
                def run_async():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    new_loop.run_until_complete(self._async_websocket_step_callback(agent_output))
                    new_loop.close()
                
                thread = threading.Thread(target=run_async)
                thread.start()
                # 메인 스레드는 계속 진행 (non-blocking)
                
        except Exception as e:
            logger.error(f"WebSocket callback error: {e}")
    
    async def _async_websocket_step_callback(self, agent_output: Any):
        """실제 비동기 WebSocket 콜백 처리"""
        try:
            output_str = str(agent_output)
            
            # Task Completion 감지 (✅ Completed 패턴 또는 Task Completed)
            if ("✅ Completed" in output_str or "Task Completed" in output_str) and "Task:" in output_str:
                # Task 정보 추출
                import re
                task_match = re.search(r'Task:\s*([a-f0-9-]+)', output_str)
                agent_match = re.search(r'Assigned to:\s*([^\n]+)', output_str)
                
                if task_match and agent_match:
                    task_id = task_match.group(1)
                    agent_role = agent_match.group(1).strip()
                    
                    # 에이전트 이름 매핑
                    agent_name = self._get_agent_name_from_role(agent_role)
                    if agent_name:
                        step_info = self._identify_current_step()
                        if step_info:
                            step_key, step_name = step_info
                            
                            # Task 완료 즉시 전송 (이벤트 기반)
                            await self._handle_task_event({
                                "type": "task_status",
                                "step": step_key,
                                "agent": agent_name,
                                "status": "completed",
                                "output": output_str
                            })
                            logger.info(f"Task completion detected for {agent_name} in {step_key}")
            
            # Agent Final Answer 감지
            if "Agent Final Answer" in output_str or "✅ Agent Final Answer" in output_str:
                # 에이전트와 답변 추출
                agent_match = re.search(r'Agent:\s*([^\n]+)', output_str)
                if agent_match:
                    agent_role = agent_match.group(1).strip()
                    agent_name = self._get_agent_name_from_role(agent_role)
                    
                    if agent_name:
                        step_info = self._identify_current_step()
                        if step_info:
                            step_key, step_name = step_info
                            
                            # Final Answer 내용 추출
                            answer_start = output_str.find("Final Answer:")
                            if answer_start == -1:
                                answer_start = output_str.find("최종 답변:")
                            
                            if answer_start != -1:
                                answer_content = output_str[answer_start:]
                                
                                # 에이전트 완료 메시지 전송
                                await self.streaming_callback.on_task_complete(
                                    agent_name,
                                    {
                                        "analysis": self._extract_full_answer(answer_content),
                                        "verdict": self._extract_verdict(answer_content),
                                        "confidence": self._extract_confidence(answer_content)
                                    },
                                    step_key
                                )
                                
                                # 완료 상태 업데이트
                                if agent_name not in self.fact_crew.completed_agents[step_key]:
                                    self.fact_crew.completed_agents[step_key].append(agent_name)
                                
                                # 단계 완료 체크
                                if self._is_step_complete(step_key):
                                    await self._handle_step_completion(step_key)
                                return
            
            # 기존 로직 (현재 에이전트 파악)
            current_agent = self._identify_current_agent(output_str)
            if not current_agent:
                return
            
            # 단계 파악 및 업데이트
            step_info = self._identify_current_step()
            if not step_info:
                return
            
            step_key, step_name = step_info
            self.current_step = step_key
            self.current_agent = current_agent
            
            # 에이전트 시작 알림 (처음 시작하는 경우)
            agent_key = f"{current_agent}_{step_key}"
            if agent_key not in self.last_agent_outputs:
                await self.streaming_callback.on_task_start(
                    current_agent,
                    f"{self.fact_crew.agents[current_agent].role}가 분석을 시작합니다",
                    step_key
                )
                self.last_agent_outputs[agent_key] = ""
            
            # 도구 호출 감지 및 스트리밍
            await self._detect_and_stream_tool_calls(output_str, current_agent, step_key)
            
            # 에이전트 분석 내용 스트리밍 (변경된 부분만)
            await self._stream_agent_analysis(output_str, current_agent, step_key)
            
            # 마지막 출력 저장
            self.last_agent_outputs[agent_key] = output_str
                    
        except Exception as e:
            logger.error(f"Async WebSocket callback error: {e}")
            await self.ws_manager.emit_error(str(e), {"step": self.current_step})
    
    def _identify_current_agent(self, output_str: str) -> Optional[str]:
        """출력에서 현재 에이전트 식별"""
        for agent_name, agent_instance in self.fact_crew.agents.items():
            if hasattr(agent_instance, 'role') and agent_instance.role in output_str:
                return agent_name
            elif agent_name.lower() in output_str.lower():
                return agent_name
        return None
    
    def _identify_current_step(self) -> Optional[tuple]:
        """현재 실행 중인 단계 식별"""
        total_completed = sum(len(agents) for agents in self.fact_crew.completed_agents.values())
        
        if total_completed < 5:  # Step 1
            return ("step1", "Step 1: 초기 분석")
        elif total_completed < 10:  # Step 2
            return ("step2", "Step 2: 토론")
        else:  # Step 3
            return ("step3", "Step 3: 최종 종합")
    
    async def _detect_and_stream_tool_calls(self, output_str: str, agent_name: str, step_key: str):
        """도구 호출 감지 및 스트리밍"""
        if "Action:" in output_str and "Action Input:" in output_str:
            lines = output_str.split('\n')
            tool_name = None
            tool_input = None
            tool_output = None
            
            for i, line in enumerate(lines):
                if "Action:" in line:
                    tool_name = line.split("Action:")[-1].strip()
                elif "Action Input:" in line:
                    tool_input = line.split("Action Input:")[-1].strip()
            
            if tool_name and tool_input:
                # 도구 호출 시작 알림
                await self.streaming_callback.on_tool_use(
                    agent_name, tool_name, 
                    {"input": tool_input}, 
                    None
                )
                
                # 도구 결과 추출
                if "Observation:" in output_str:
                    obs_start = output_str.find("Observation:")
                    obs_end = output_str.find("Thought:", obs_start) if "Thought:" in output_str[obs_start:] else len(output_str)
                    tool_output = output_str[obs_start + len("Observation:"):obs_end].strip()
                    
                    # 도구 결과 스트리밍
                    await self.streaming_callback.on_tool_use(
                        agent_name, tool_name,
                        {"input": tool_input},
                        tool_output[:500] if tool_output else "결과 처리 중..."
                    )
    
    async def _stream_agent_analysis(self, output_str: str, agent_name: str, step_key: str):
        """에이전트 분석 내용 스트리밍"""
        # 주요 분석 내용이 있는 경우만 스트리밍
        if any(keyword in output_str for keyword in ["판정:", "결론:", "분석:", "핵심", "요약"]):
            analysis_summary = self._extract_analysis_summary(output_str)
            
            # 이전 출력과 다른 경우만 전송
            agent_key = f"{agent_name}_{step_key}"
            if agent_key in self.last_agent_outputs:
                if analysis_summary in self.last_agent_outputs[agent_key]:
                    return  # 중복 전송 방지
            
            await self.ws_manager.emit({
                "type": "agent_analysis",
                "step": step_key,
                "agent": agent_name,
                "content": {
                    "analysis": analysis_summary,
                    "progress": f"{agent_name} 에이전트 분석 중..."
                }
            })
    
    def _is_agent_complete(self, output_str: str) -> bool:
        """에이전트 작업 완료 여부 확인"""
        completion_indicators = [
            "분석 완료", "완료했습니다", "최종", "결론:", "판정:",
            "Final Answer:", "분석을 마치겠습니다", "종료",
            "✅ Completed", "Task Completed", "Agent Final Answer",
            "### 판정:", "## 판정:", "최종 판정:"
        ]
        return any(indicator in output_str for indicator in completion_indicators)
    
    def _is_step_complete(self, step_key: str) -> bool:
        """단계 완료 여부 확인"""
        if step_key == "step1":
            return len(self.fact_crew.completed_agents["step1"]) >= 5
        elif step_key == "step2":
            return len(self.fact_crew.completed_agents["step2"]) >= 5
        elif step_key == "step3":
            return len(self.fact_crew.completed_agents["step3"]) >= 1
        return False
    
    async def _handle_step_completion(self, step_key: str):
        """단계 완료 처리"""
        step_results = {}
        
        if step_key == "step1":
            step_results = {name: "초기 분석 완료" for name in self.fact_crew.completed_agents["step1"]}
            await self.streaming_callback.on_step_complete("step1", step_results)
            
            # Step 2 시작 알림
            await self.streaming_callback.on_step_change(
                "step2",
                "전문가들이 서로의 분석을 검토하고 토론합니다"
            )
            
        elif step_key == "step2":
            step_results = {name: "토론 완료" for name in self.fact_crew.completed_agents["step2"]}
            await self.streaming_callback.on_step_complete("step2", step_results)
            
            # Step 3 시작 알림
            await self.streaming_callback.on_step_change(
                "step3",
                "총괄 코디네이터가 최종 판정을 내립니다"
            )
    
    def _get_agent_name_from_role(self, role: str) -> Optional[str]:
        """역할명으로부터 에이전트 이름 추출"""
        role_mapping = {
            "학술 연구 전문가": "academic",
            "뉴스 검증 전문가": "news",
            "사회 맥락 분석가": "social",
            "논리 및 추론 전문가": "logic",
            "통계 및 데이터 전문가": "statistics",
            "팩트체크 총괄 코디네이터": "super"
        }
        return role_mapping.get(role)
    
    def _extract_full_answer(self, output_str: str) -> str:
        """전체 Final Answer 추출"""
        # Final Answer: 이후의 모든 내용 추출
        if "Final Answer:" in output_str:
            answer_part = output_str.split("Final Answer:", 1)[1]
        elif "최종 답변:" in output_str:
            answer_part = output_str.split("최종 답변:", 1)[1]
        else:
            answer_part = output_str
        
        # 첫 500자 또는 주요 내용 반환
        return answer_part.strip()[:1000] if len(answer_part) > 1000 else answer_part.strip()
    
    def _extract_analysis_summary(self, output_str: str) -> str:
        """분석 요약 추출"""
        lines = output_str.split('\n')
        summary_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ["판정:", "결론:", "분석:", "핵심", "요약"]):
                summary_lines.append(line.strip())
        
        return "\n".join(summary_lines[:5]) if summary_lines else output_str[:500] + "..."
    
    def _extract_verdict(self, output_str: str) -> str:
        """판정 추출"""
        for verdict in self.VERDICT_OPTIONS.keys():
            if verdict in output_str:
                return verdict
        return "분석중"
    
    def _extract_confidence(self, output_str: str) -> float:
        """신뢰도 추출"""
        confidence_match = re.search(r'신뢰도[:\s]*([0-9.]+)', output_str)
        if confidence_match:
            try:
                return float(confidence_match.group(1)) / 100.0
            except:
                pass
        return 0.75  # 기본값
    
    def _structure_final_result(self, statement: str, crew_result: Any) -> Dict[str, Any]:
        """최종 결과 구조화"""
        result_str = str(crew_result)
        
        return {
            "statement": statement,
            "final_verdict": self._extract_verdict(result_str),
            "confidence": self._calculate_weighted_confidence(),
            "verdict_korean": self.VERDICT_OPTIONS.get(self._extract_verdict(result_str), "분석 완료"),
            "summary": result_str,  # 전체 응답 포함
            "agent_verdicts": self._get_agent_verdicts(),
            "evidence_summary": self._get_evidence_summary(),
            "tool_usage_stats": self._get_tool_usage_stats(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_agent_verdicts(self) -> Dict[str, Any]:
        """각 에이전트의 판정 요약"""
        verdicts = {}
        for agent_name in ["academic", "news", "logic", "social", "statistics"]:
            agent_key = f"{agent_name}_step1"
            if agent_key in self.fact_crew.agent_outputs:
                output = self.fact_crew.agent_outputs[agent_key]
                verdicts[agent_name] = {
                    "verdict": self._extract_verdict(output),
                    "confidence": self._extract_confidence(output)
                }
        return verdicts
    
    def _get_evidence_summary(self) -> Dict[str, str]:
        """증거 요약"""
        return {
            "academic": "학술 자료 검토 완료",
            "news": "언론 보도 확인 완료",
            "statistics": "통계 데이터 분석 완료",
            "logic": "논리적 일관성 검토 완료",
            "social": "사회적 맥락 분석 완료"
        }
    
    def _get_tool_usage_stats(self) -> Dict[str, int]:
        """도구 사용 통계"""
        stats = {}
        
        for step in ["step1", "step2", "step3"]:
            if step in self.fact_crew.tool_calls:
                for agent_name, calls in self.fact_crew.tool_calls[step].items():
                    for call in calls:
                        tool = call.get("tool", "unknown")
                        stats[tool] = stats.get(tool, 0) + 1
        
        return stats
    
    def _calculate_weighted_confidence(self) -> float:
        """가중치를 적용한 신뢰도 계산"""
        total_confidence = 0.0
        total_weight = 0.0
        
        for agent_name, weight in self.AGENT_WEIGHTS.items():
            agent_key = f"{agent_name}_step1"
            if agent_key in self.fact_crew.agent_outputs:
                agent_output = self.fact_crew.agent_outputs[agent_key]
                agent_confidence = self._extract_confidence(agent_output)
                total_confidence += agent_confidence * weight
                total_weight += weight
        
        return round(total_confidence / total_weight if total_weight > 0 else 0.75, 2)
    
    async def check_fact_async(self, statement: str) -> Dict[str, Any]:
        """비동기 팩트체킹 실행 (WebSocket 스트리밍 지원)"""
        try:
            # 시작 알림
            await self.ws_manager.emit_progress("init", 0.0, "팩트체킹을 시작합니다...")
            
            # FactWaveCrew의 check_fact를 별도 스레드에서 실행
            # (CrewAI는 동기적으로 실행되므로)
            loop = asyncio.get_event_loop()
            
            # 실행 전 초기화
            await self.streaming_callback.on_step_change(
                "step1", 
                "각 전문가가 독립적으로 진술을 분석합니다"
            )
            
            # FactWaveCrew.check_fact를 비동기로 실행
            result = await loop.run_in_executor(
                self.executor,
                self.fact_crew.check_fact,
                statement
            )
            
            # 최종 결과 구조화
            final_result = self._structure_final_result(statement, result)
            
            # 최종 결과 전송
            await self.streaming_callback.on_final_result(
                final_result["final_verdict"],
                final_result["confidence"],
                final_result
            )
            
            # 완료 알림
            await self.ws_manager.emit_progress("complete", 1.0, "팩트체킹이 완료되었습니다")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Fact-checking error: {e}")
            await self.ws_manager.emit_error(str(e), {"step": self.current_step})
            raise
    
    def __del__(self):
        """정리"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)