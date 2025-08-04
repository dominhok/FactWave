"""FactWave Crew - 3단계 팩트체킹 프로세스 구현"""

from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
import time

from ..agents import AcademicAgent, NewsAgent, SocialAgent, LogicAgent, SuperAgent


console = Console()


class FactWaveCrew:
    """3단계 팩트체킹 프로세스를 관리하는 메인 클래스"""
    
    # 판정 옵션
    VERDICT_OPTIONS = {
        "참": "명백히 사실임",
        "대체로_참": "대체로 사실임",
        "부분적_참": "부분적으로 사실임",
        "불확실": "판단하기 어려움",
        "정보부족": "정보가 부족함",
        "논란중": "논란이 있음",
        "부분적_거짓": "부분적으로 거짓임",
        "대체로_거짓": "대체로 거짓임",
        "거짓": "명백히 거짓임",
        "과장됨": "과장된 표현임",
        "오해소지": "오해의 소지가 있는 표현임",
        "시대착오": "시대에 맞지 않음(과거에는 맞았으나 지금은 아님)"
    }
    
    # 에이전트 가중치
    AGENT_WEIGHTS = {
        "academic": 0.30,
        "news": 0.35,
        "logic": 0.20,
        "social": 0.15
    }
    
    def __init__(self):
        # Initialize agents
        self.agents = {
            "academic": AcademicAgent(),
            "news": NewsAgent(),
            "social": SocialAgent(),
            "logic": LogicAgent(),
            "super": SuperAgent()
        }
        
        # Store tasks for result access
        self.step1_tasks = {}
        self.step2_tasks = {}
        self.step3_task = None
        
        # Track current progress
        self.completed_agents = {"step1": [], "step2": [], "step3": []}
        self.agent_outputs = {}
    
    def create_step1_tasks(self, statement: str) -> List[Task]:
        """Step 1: 각 에이전트가 독립적으로 초기 분석 수행"""
        tasks = []
        
        console.print("\n[bold cyan]🔍 Step 1: 초기 분석 단계[/bold cyan]")
        console.print("각 전문가가 독립적으로 주장을 분석합니다...\n")
        
        for agent_name, agent_instance in self.agents.items():
            if agent_name != "super":  # Super agent는 Step 3에서만 활동
                description = f"""
다음 주장을 분석하세요: "{statement}"

전문가 분석을 제공해주세요:
1. 초기 평가 (참/거짓/불확실 등)
2. 주요 근거나 추론
3. 신뢰도 수준 (0-100%)
4. 주의사항이나 고려사항

간결하지만 철저하게 답변해주세요.
"""
                task = Task(
                    description=description,
                    agent=agent_instance.get_agent(),
                    expected_output="판정, 근거, 신뢰도를 포함한 구조화된 분석"
                )
                tasks.append(task)
                self.step1_tasks[agent_name] = task
        
        return tasks
    
    def create_step2_tasks(self, statement: str) -> List[Task]:
        """Step 2: 에이전트들이 서로의 분석을 검토하고 토론"""
        tasks = []
        
        console.print("\n[bold cyan]💬 Step 2: 토론 단계[/bold cyan]")
        console.print("전문가들이 서로의 의견을 검토하고 토론합니다...\n")
        
        # 각 에이전트는 다른 모든 에이전트의 초기 분석을 context로 받음
        for agent_name, agent_instance in self.agents.items():
            if agent_name != "super":
                # 다른 에이전트들의 초기 분석을 context로 전달
                context_tasks = [task for name, task in self.step1_tasks.items() if name != agent_name]
                
                description = f"""
다른 모든 에이전트의 분석을 검토하세요: "{statement}"

그들의 관점을 고려하여 필요시 당신의 입장을 수정하세요.
동의하는 부분과 동의하지 않는 부분을 강조하세요.
추론과 함께 업데이트된 판정을 제공하세요.

다른 에이전트들의 분석 결과를 검토하고, 당신의 전문 분야 관점에서 
동의하는 부분과 동의하지 않는 부분을 명확히 표현하세요.
필요하다면 당신의 초기 판단을 수정하세요.
"""
                
                task = Task(
                    description=description,
                    agent=agent_instance.get_agent(),
                    expected_output="다른 에이전트의 의견을 고려한 개선된 분석",
                    context=context_tasks  # 다른 에이전트들의 Step 1 결과를 참조
                )
                tasks.append(task)
                self.step2_tasks[agent_name] = task
        
        return tasks
    
    def create_step3_task(self, statement: str) -> Task:
        """Step 3: Super Agent가 모든 분석을 종합하여 최종 판정"""
        console.print("\n[bold cyan]📊 Step 3: 최종 종합 단계[/bold cyan]")
        console.print("총괄 코디네이터가 모든 분석을 종합합니다...\n")
        
        # 모든 Step 1과 Step 2의 결과를 context로 전달
        all_context_tasks = list(self.step1_tasks.values()) + list(self.step2_tasks.values())
        
        verdict_options_str = "\n".join([f"- {k}: {v}" for k, v in self.VERDICT_OPTIONS.items()])
        
        description = f"""
수석 코디네이터로서 모든 에이전트의 분석을 종합하세요: "{statement}"

다음을 포함한 최종 팩트체크 보고서를 작성하세요:
1. 전체 판정 - 반드시 다음 중 하나를 선택:
{verdict_options_str}

2. 각 에이전트의 평가를 보여주는 신뢰도 매트릭스
3. 주요 합의점
4. 주요 불일치점
5. 최종 신뢰도 점수 (가중 평균)
6. 판정에 대한 간단한 설명

에이전트 가중치: 학술(30%), 뉴스(35%), 논리(20%), 사회(15%)

모든 에이전트의 초기 분석(Step 1)과 토론 결과(Step 2)를 종합적으로 검토하세요.
각 에이전트의 가중치를 고려하여 최종 신뢰도를 계산하세요.

에이전트 가중치:
- Academic Agent: {self.AGENT_WEIGHTS['academic']}
- News Agent: {self.AGENT_WEIGHTS['news']}  
- Logic Agent: {self.AGENT_WEIGHTS['logic']}
- Social Agent: {self.AGENT_WEIGHTS['social']}
"""
        
        self.step3_task = Task(
            description=description,
            agent=self.agents["super"].get_agent(),
            expected_output="신뢰도 매트릭스와 함께 종합적인 팩트체크 판정",
            context=all_context_tasks  # 모든 이전 단계의 결과를 참조
        )
        
        return self.step3_task
    
    def create_progress_table(self) -> Table:
        """진행 상황을 표시하는 테이블 생성"""
        table = Table(title="팩트체크 진행 상황", show_header=True, header_style="bold magenta")
        table.add_column("단계", style="cyan", width=20)
        table.add_column("에이전트", style="yellow", width=25)
        table.add_column("상태", style="green", width=15)
        
        # Step 1
        for agent_name in ["academic", "news", "social", "logic"]:
            status = "✅ 완료" if agent_name in self.completed_agents["step1"] else "⏳ 진행중..." if len(self.completed_agents["step1"]) < 4 else "⏸️  대기중"
            table.add_row(
                "Step 1: 초기 분석" if agent_name == "academic" else "",
                self.agents[agent_name].role,
                status
            )
        
        # 구분선
        table.add_row("", "", "")
        
        # Step 2
        for agent_name in ["academic", "news", "social", "logic"]:
            status = "✅ 완료" if agent_name in self.completed_agents["step2"] else "⏳ 진행중..." if len(self.completed_agents["step1"]) == 4 and len(self.completed_agents["step2"]) < 4 else "⏸️  대기중"
            table.add_row(
                "Step 2: 토론" if agent_name == "academic" else "",
                self.agents[agent_name].role,
                status
            )
        
        # 구분선
        table.add_row("", "", "")
        
        # Step 3
        status = "✅ 완료" if "super" in self.completed_agents["step3"] else "⏳ 진행중..." if len(self.completed_agents["step2"]) == 4 else "⏸️  대기중"
        table.add_row(
            "Step 3: 최종 종합",
            self.agents["super"].role,
            status
        )
        
        return table
    
    def _step_callback(self, agent_output: Any):
        """각 에이전트의 작업이 완료될 때마다 호출되는 콜백"""
        output_str = str(agent_output)
        
        # 현재 어떤 에이전트가 작업했는지 파악
        current_agent = None
        for agent_name, agent in self.agents.items():
            if agent.role in output_str:
                current_agent = agent_name
                break
        
        if not current_agent:
            return
        
        # 단계 판별 및 업데이트
        total_completed = sum(len(agents) for agents in self.completed_agents.values())
        
        if total_completed < 4:  # Step 1
            self.completed_agents["step1"].append(current_agent)
            step_name = "Step 1: 초기 분석"
            color = "blue"
        elif total_completed < 8:  # Step 2
            self.completed_agents["step2"].append(current_agent)
            step_name = "Step 2: 토론"
            color = "yellow"
        else:  # Step 3
            self.completed_agents["step3"].append(current_agent)
            step_name = "Step 3: 최종 종합"
            color = "green"
        
        # 에이전트 출력 저장
        self.agent_outputs[f"{step_name}_{current_agent}"] = output_str
        
        # 콘솔 클리어 (선택적)
        # console.clear()  # 전체 로그를 보기 위해 클리어 비활성화
        
        # 진행 상황 테이블 표시
        console.print("\n" + "="*80 + "\n")
        console.print(self.create_progress_table())
        console.print("\n" + "="*80 + "\n")
        
        # 실시간 알림
        console.print(f"[bold {color}]🔔 {step_name} - {self.agents[current_agent].role} 완료![/bold {color}]\n")
        
        # 도구 사용 감지 및 표시
        if "Action:" in output_str and "Action Input:" in output_str:
            lines = output_str.split('\n')
            tool_name = None
            tool_input = None
            
            for i, line in enumerate(lines):
                if "Action:" in line:
                    tool_name = line.split("Action:")[-1].strip()
                elif "Action Input:" in line:
                    tool_input = line.split("Action Input:")[-1].strip()
                    
            if tool_name and tool_input:
                console.print(f"[yellow]🔧 도구 사용: {tool_name}[/yellow]")
                console.print(f"[dim]입력: {tool_input}[/dim]\n")
        
        # 미리보기 표시 (처음 5줄로 확장)
        preview_lines = output_str.split('\n')[:5]
        preview = '\n'.join(preview_lines)
        if len(output_str.split('\n')) > 5:
            preview += "\n[dim]... (더 많은 내용이 있습니다)[/dim]"
        
        panel = Panel(
            preview,
            title=f"[bold]{self.agents[current_agent].role}[/bold]",
            border_style=color,
            padding=(1, 1)
        )
        console.print(panel)
    
    def check_fact(self, statement: str):
        """3단계 팩트체킹 프로세스 실행"""
        console.print(f"\n[bold green]📋 팩트체크 시작:[/bold green] {statement}\n")
        
        # Reset tracking
        self.completed_agents = {"step1": [], "step2": [], "step3": []}
        self.agent_outputs = {}
        
        # 초기 진행 상황 표시
        console.print(self.create_progress_table())
        console.print("\n[bold cyan]🚀 팩트체크 프로세스를 시작합니다...[/bold cyan]")
        console.print("[dim]각 전문가의 분석이 완료되면 실시간으로 알려드립니다.[/dim]\n")
        
        # Step 1: 초기 분석
        step1_tasks = self.create_step1_tasks(statement)
        
        # Step 2: 토론
        step2_tasks = self.create_step2_tasks(statement)
        
        # Step 3: 최종 종합
        step3_task = self.create_step3_task(statement)
        
        # 모든 태스크를 순차적으로 실행
        all_tasks = step1_tasks + step2_tasks + [step3_task]
        
        # 모든 에이전트 목록
        all_agents = [agent.get_agent() for agent in self.agents.values()]
        
        # Crew 생성 및 실행
        crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            process=Process.sequential,
            verbose=False,  # verbose를 False로 설정하여 중복 출력 방지
            step_callback=self._step_callback  # 콜백 추가
        )
        
        # 실행
        result = crew.kickoff()
        
        # 최종 결과 표시
        console.clear()
        console.print("\n" + "="*80 + "\n")
        console.print("[bold green]✅ 모든 분석이 완료되었습니다![/bold green]\n")
        
        # 전체 결과 요약 표시
        self.display_final_summary(statement)
        
        return result
    
    def display_final_summary(self, statement: str):
        """최종 요약만 간단히 표시"""
        # 최종 판정 결과만 크게 표시
        if self.step3_task and self.step3_task.output:
            console.print("[bold]📊 최종 팩트체크 결과[/bold]\n")
            final_panel = Panel(
                str(self.step3_task.output),
                title="[bold]팩트체크 최종 보고서[/bold]",
                border_style="green",
                padding=(1, 2)
            )
            console.print(final_panel)
            
            # 간단한 진행 요약
            console.print("\n[bold]📋 진행 요약:[/bold]")
            console.print(f"• Step 1: 4명의 전문가 초기 분석 완료")
            console.print(f"• Step 2: 전문가 간 토론 완료")
            console.print(f"• Step 3: 최종 종합 판정 완료")
            console.print(f"\n[dim]총 9개의 분석 단계를 거쳤습니다.[/dim]")