"""Base agent class with common functionality"""

from crewai import Agent
from typing import Dict, Any, List, Optional
from ..utils.llm_config import StructuredLLM
from rich.console import Console
import logging

logger = logging.getLogger(__name__)
console = Console()


class FactWaveAgent:
    """Base class for all FactWave agents"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools: List[Any] = []  # 도구 목록
        self.agent = None  # 나중에 생성
    
    def _create_agent(self, step: str = "step1") -> Agent:
        """Create the CrewAI agent instance with step-specific LLM"""
        # Step에 따라 적절한 LLM 선택
        if step == "step1":
            from ..utils.llm_config import get_step1_llm
            llm = get_step1_llm()
        elif step == "step2":
            from ..utils.llm_config import get_step2_llm
            llm = get_step2_llm()
        elif step == "step3":
            from ..utils.llm_config import get_step3_llm
            llm = get_step3_llm()
        else:
            llm = StructuredLLM.get_default_llm()
        
        # 도구에 로깅 래퍼 추가
        logged_tools = []
        for tool in self.tools:
            original_run = tool._run
            tool_name = tool.name
            
            def make_logged_run(orig_run, t_name):
                def logged_run(*args, **kwargs):
                    # 도구 호출 시작 로그
                    console.print(f"\n[bold yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold yellow]")
                    console.print(f"[bold cyan]🔧 {self.role} → {t_name}[/bold cyan]")
                    console.print(f"[dim]입력: {str(kwargs)[:200]}...[/dim]")
                    console.print(f"[bold yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold yellow]")
                    
                    # 실제 도구 실행
                    result = orig_run(*args, **kwargs)
                    
                    # 도구 결과 로그
                    console.print(f"[green]✅ 결과 ({len(str(result))}자):[/green]")
                    preview = str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
                    console.print(f"[dim]{preview}[/dim]")
                    console.print(f"[bold yellow]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold yellow]\n")
                    
                    return result
                return logged_run
            
            tool._run = make_logged_run(original_run, tool_name)
            logged_tools.append(tool)
        
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=logged_tools,  # 로깅 래퍼가 추가된 도구 전달
            verbose=True,
            allow_delegation=False,
            llm=llm,
            # tool_callback=log_tool_usage  # 도구 사용 로깅
        )
    
    def get_agent(self, step: str = "step1") -> Agent:
        """Return the CrewAI agent instance"""
        # Step이 바뀌면 새로운 agent 생성 (LLM이 달라지므로)
        self.agent = self._create_agent(step)
        return self.agent