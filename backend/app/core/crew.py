"""FactWave Crew - 3단계 팩트체킹 프로세스 구현"""

from typing import Dict, List, Any
from crewai import Agent, Task, Crew, Process
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
import time

from ..agents import AcademicAgent, NewsAgent, SocialAgent, LogicAgent, StatisticsAgent, SuperAgent
from ..utils.prompt_loader import PromptLoader


console = Console()


class FactWaveCrew:
    """3단계 팩트체킹 프로세스를 관리하는 메인 클래스"""
    
    def __init__(self, task_callback=None):
        """
        Args:
            task_callback: Task 상태 변경 시 호출될 콜백 함수
        """
        # 프롬프트 로더 초기화
        self.prompt_loader = PromptLoader()
        
        # YAML에서 설정 로드
        self.VERDICT_OPTIONS = self.prompt_loader.get_verdict_options()
        self.AGENT_WEIGHTS = self.prompt_loader.get_agent_weights()
    
        # Initialize agents
        self.agents = {
            "academic": AcademicAgent(),
            "news": NewsAgent(),
            "social": SocialAgent(),
            "logic": LogicAgent(),
            "statistics": StatisticsAgent(),
            "super": SuperAgent()
        }
        
        # Store tasks for result access
        self.step1_tasks = {}
        self.step2_tasks = {}
        self.step3_task = None
        
        # Track current progress
        self.completed_agents = {"step1": [], "step2": [], "step3": []}
        self.agent_outputs = {}
        
        # 도구 호출 결과 저장 (websocket을 위해)
        self.tool_calls = {
            "step1": {},  # {agent_name: [{tool: name, input: input, output: output}, ...]}
            "step2": {},
            "step3": {}
        }
        self.current_step = None
        self.current_agent = None
        self.task_callback = task_callback  # Task 레벨 콜백
    
    def create_step1_tasks(self, statement: str) -> List[Task]:
        """Step 1: 각 에이전트가 독립적으로 초기 분석 수행"""
        tasks = []
        
        console.print("\n[bold cyan]🔍 Step 1: 초기 분석 단계[/bold cyan]")
        console.print("각 전문가가 독립적으로 주장을 분석합니다...\n")
        
        for agent_name, agent_instance in self.agents.items():
            if agent_name != "super":  # Super agent는 Step 3에서만 활동
                if agent_name == "logic":
                    # 논리 전문가용 프롬프트
                    description = self.prompt_loader.get_step1_prompt('logic', statement, agent_name=agent_name)
                else:
                    # 일반 에이전트용 프롬프트
                    description = self.prompt_loader.get_step1_prompt('general', statement, agent_instance.role, agent_name)
                # Task 콜백 생성
                if self.task_callback:
                    def make_task_callback(agent_n, step):
                        def callback(output):
                            self.task_callback({
                                "type": "task_status",
                                "step": step,
                                "agent": agent_n,
                                "status": "completed",
                                "output": str(output)
                            })
                        return callback
                    task_callback_func = make_task_callback(agent_name, "step1")
                else:
                    task_callback_func = None
                
                task = Task(
                    description=description,
                    agent=agent_instance.get_agent("step1"),
                    expected_output="판정, 근거, 신뢰도를 포함한 구조화된 분석",
                    callback=task_callback_func  # callback 필드 사용
                )
                tasks.append(task)
                self.step1_tasks[agent_name] = task
                
                # Task 시작 알림
                if self.task_callback:
                    self.task_callback({
                        "type": "task_status",
                        "step": "step1",
                        "agent": agent_name,
                        "status": "started",
                        "task_id": str(task.id)
                    })
        
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
                
                # Step 2 토론 프롬프트
                description = self.prompt_loader.get_step2_prompt(statement, agent_instance.role, agent_name)
                
                # Task 콜백 생성
                if self.task_callback:
                    def make_task_callback(agent_n, step):
                        def callback(output):
                            self.task_callback({
                                "type": "task_status",
                                "step": step,
                                "agent": agent_n,
                                "status": "completed",
                                "output": str(output)
                            })
                        return callback
                    task_callback_func = make_task_callback(agent_name, "step2")
                else:
                    task_callback_func = None
                
                task = Task(
                    description=description,
                    agent=agent_instance.get_agent("step2"),
                    expected_output="다른 에이전트의 의견을 고려한 개선된 분석",
                    context=context_tasks,  # 다른 에이전트들의 Step 1 결과를 참조
                    callback=task_callback_func  # callback 필드 사용
                )
                tasks.append(task)
                self.step2_tasks[agent_name] = task
                
                # Task 시작 알림
                if self.task_callback:
                    self.task_callback({
                        "type": "task_status",
                        "step": "step2",
                        "agent": agent_name,
                        "status": "started",
                        "task_id": str(task.id)
                    })
        
        return tasks
    
    def create_step3_task(self, statement: str) -> Task:
        """Step 3: Super Agent가 모든 분석을 종합하여 최종 판정"""
        console.print("\n[bold cyan]📊 Step 3: 최종 종합 단계[/bold cyan]")
        console.print("총괄 코디네이터가 모든 분석을 종합합니다...\n")
        
        # 모든 Step 1과 Step 2의 결과를 context로 전달
        all_context_tasks = list(self.step1_tasks.values()) + list(self.step2_tasks.values())
        
        # Step 3 최종 종합 프롬프트
        description = self.prompt_loader.get_step3_prompt(statement, self.AGENT_WEIGHTS)
        
        # 판정 옵션 추가
        verdict_options_str = self.prompt_loader.format_verdict_options_string()
        description = description.replace("[선택]", f"[다음 중 선택:\n{verdict_options_str}]")
        
        # Task 콜백 생성
        if self.task_callback:
            def callback(output):
                self.task_callback({
                    "type": "task_status",
                    "step": "step3",
                    "agent": "super",
                    "status": "completed",
                    "output": str(output)
                })
            task_callback_func = callback
        else:
            task_callback_func = None
        
        self.step3_task = Task(
            description=description,
            agent=self.agents["super"].get_agent("step3"),
            expected_output="신뢰도 매트릭스와 함께 종합적인 팩트체크 판정",
            context=all_context_tasks,  # 모든 이전 단계의 결과를 참조
            callback=task_callback_func  # callback 필드 사용
        )
        
        # Task 시작 알림
        if self.task_callback:
            self.task_callback({
                "type": "task_status",
                "step": "step3",
                "agent": "super",
                "status": "started",
                "task_id": str(self.step3_task.id)
            })
        
        return self.step3_task
    
    def create_progress_table(self) -> Table:
        """진행 상황을 표시하는 테이블 생성"""
        table = Table(title="팩트체크 진행 상황", show_header=True, header_style="bold magenta")
        table.add_column("단계", style="cyan", width=20)
        table.add_column("에이전트", style="yellow", width=25)
        table.add_column("상태", style="green", width=15)
        
        # Step 1
        for agent_name in ["academic", "news", "social", "logic", "statistics"]:
            status = "✅ 완료" if agent_name in self.completed_agents["step1"] else "⏳ 진행중..." if len(self.completed_agents["step1"]) < 5 else "⏸️  대기중"
            table.add_row(
                "Step 1: 초기 분석" if agent_name == "academic" else "",
                self.agents[agent_name].role,
                status
            )
        
        # 구분선
        table.add_row("", "", "")
        
        # Step 2
        for agent_name in ["academic", "news", "social", "logic", "statistics"]:
            status = "✅ 완료" if agent_name in self.completed_agents["step2"] else "⏳ 진행중..." if len(self.completed_agents["step1"]) == 5 and len(self.completed_agents["step2"]) < 5 else "⏸️  대기중"
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
        
        if total_completed < 5:  # Step 1 (5개 에이전트)
            if current_agent not in self.completed_agents["step1"]:
                self.completed_agents["step1"].append(current_agent)
            step_name = "Step 1: 초기 분석"
            step_key = "step1"
            color = "blue"
        elif total_completed < 10:  # Step 2 (5개 에이전트)
            if current_agent not in self.completed_agents["step2"]:
                self.completed_agents["step2"].append(current_agent)
            step_name = "Step 2: 토론"
            step_key = "step2"
            color = "yellow"
        else:  # Step 3
            if current_agent not in self.completed_agents["step3"]:
                self.completed_agents["step3"].append(current_agent)
            step_name = "Step 3: 최종 종합"
            step_key = "step3"
            color = "green"
        
        # 에이전트 출력 저장
        key = f"{current_agent}_{step_key}"
        self.agent_outputs[key] = output_str
        
        # 도구 사용 감지 및 저장
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
                # 도구 호출 정보 즉시 출력 (websocket 실시간 전송을 위해)
                console.print(f"\n[bold {color}]📡 {step_name} - {self.agents[current_agent].role}[/bold {color}]")
                console.print(f"[yellow]🔧 도구 호출: {tool_name}[/yellow]")
                console.print(f"[dim]입력: {tool_input}[/dim]")
                
                # 도구 결과 추출
                if "Observation:" in output_str:
                    obs_start = output_str.find("Observation:")
                    obs_end = output_str.find("Thought:", obs_start) if "Thought:" in output_str[obs_start:] else len(output_str)
                    tool_output = output_str[obs_start + len("Observation:"):obs_end].strip()
                    
                    # 결과 즉시 출력
                    if len(tool_output) > 500:
                        display_output = tool_output[:500] + "\n[dim]... (더 많은 결과가 있습니다)[/dim]"
                    else:
                        display_output = tool_output
                    console.print(f"[green]🔍 결과:[/green]")
                    console.print(Panel(display_output, border_style="green"))
                
                # 도구 호출 결과 저장 (websocket으로 전송할 데이터)
                if step_key not in self.tool_calls:
                    self.tool_calls[step_key] = {}
                if current_agent not in self.tool_calls[step_key]:
                    self.tool_calls[step_key][current_agent] = []
                    
                self.tool_calls[step_key][current_agent].append({
                    "tool": tool_name,
                    "input": tool_input,
                    "output": tool_output if tool_output else "(waiting for result...)",
                    "timestamp": time.time()
                })
    
    def check_fact(self, statement: str):
        """3단계 팩트체킹 프로세스 실행"""
        console.print(f"\n[bold green]📋 팩트체크 시작:[/bold green] {statement}\n")
        
        # Reset tracking
        self.completed_agents = {"step1": [], "step2": [], "step3": []}
        self.agent_outputs = {}
        self.tool_calls = {"step1": {}, "step2": {}, "step3": {}}
        
        # 초기 진행 상황 표시
        console.print(self.create_progress_table())
        console.print("\n[bold cyan]🚀 팩트체크 프로세스를 시작합니다...[/bold cyan]")
        console.print("[dim]각 전문가의 분석이 완료되면 실시간으로 알려드립니다.[/dim]\n")
        
        # Step 1: 초기 분석 (독립적 실행을 위해 개별 crew 사용)
        console.print("[bold blue]🔍 Step 1: 독립적 초기 분석[/bold blue]")
        console.print("[dim]각 전문가가 독립적으로 분석을 시작합니다...[/dim]\n")
        
        step1_tasks = self.create_step1_tasks(statement)
        
        # Step 1: 각 에이전트를 개별 crew로 실행하여 독립성 보장
        step1_results = {}
        for i, (agent_name, agent_instance) in enumerate([("academic", self.agents["academic"]),
                                                          ("news", self.agents["news"]),
                                                          ("social", self.agents["social"]),
                                                          ("logic", self.agents["logic"]),
                                                          ("statistics", self.agents["statistics"])]):
            console.print(f"[cyan]🔸 {agent_instance.role} 분석 시작...[/cyan]")
            
            # 개별 crew로 각 에이전트 실행
            individual_crew = Crew(
                agents=[agent_instance.get_agent("step1")],
                tasks=[step1_tasks[i]],
                process=Process.sequential,
                verbose=True,
                step_callback=self._step_callback
            )
            
            result = individual_crew.kickoff()
            step1_results[agent_name] = result
            
            # 결과 즉시 출력
            console.print(f"\n[bold green]✅ {agent_instance.role} 분석 완료![/bold green]")
            
            # 도구 호출 요약 표시
            if "step1" in self.tool_calls and agent_name in self.tool_calls["step1"]:
                console.print(f"\n[bold]🔧 {agent_instance.role} 도구 사용 요약:[/bold]")
                for tool_call in self.tool_calls["step1"][agent_name]:
                    console.print(f"  • {tool_call['tool']}: {tool_call['input'][:50]}...")
            
            console.print(Panel(str(result), title=f"{agent_instance.role} 초기 분석", border_style="cyan"))
        
        console.print("\n[yellow]⚡ Step 1 완료: 5명의 전문가가 독립적으로 분석을 완료했습니다.[/yellow]")
        
        # Step 1 도구 호출 종합 요약
        if "step1" in self.tool_calls:
            console.print("\n[bold cyan]📈 Step 1 도구 호출 종합:[/bold cyan]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("에이전트", style="cyan")
            table.add_column("도구 호출 회수", style="yellow")
            table.add_column("사용된 도구", style="green")
            
            for agent_name, tool_calls in self.tool_calls["step1"].items():
                tools_used = list(set([tc["tool"] for tc in tool_calls]))
                table.add_row(
                    self.agents[agent_name].role,
                    str(len(tool_calls)),
                    ", ".join(tools_used)
                )
            console.print(table)
        
        step1_crew = None  # 개별 crew 사용으로 변경
        
        # Step 1 결과 정리 및 출력
        console.print("\n[bold green]✅ Step 1 완료: 초기 분석 결과[/bold green]")
        for agent_name in ["academic", "news", "social", "logic"]:
            if agent_name in self.agent_outputs:
                console.print(f"\n[bold]{self.agents[agent_name].role}:[/bold]")
                console.print(Panel(self.agent_outputs[agent_name], border_style="cyan"))
        
        # Step 2: 토론
        console.print("\n[bold blue]💬 Step 2: 전문가 토론[/bold blue]")
        console.print("[dim]각 전문가가 다른 전문가의 의견을 검토하고 토론합니다...[/dim]\n")
        
        # Step 1 결과를 문자열로 정리
        step1_summary = "\n".join([
            f"[{self.agents[name].role}]\n{str(step1_results[name])}\n"
            for name in ["academic", "news", "social", "logic", "statistics"]
        ])
        
        console.print(Panel(
            "[bold yellow]📢 토론 시작: 모든 전문가들이 초기 분석을 공유하고 토론을 시작합니다![/bold yellow]",
            title="Step 2: 토론 단계",
            border_style="yellow"
        ))
        
        step2_tasks = self.create_step2_tasks(statement)
        
        # Step 2는 순차적으로 (서로의 의견을 참조해야 하므로)
        step2_agents = [self.agents[name].get_agent("step2") for name in ["academic", "news", "social", "logic", "statistics"]]
        
        step2_crew = Crew(
            agents=step2_agents,
            tasks=step2_tasks,
            process=Process.sequential,
            verbose=True,  # 토론 과정 보기
            step_callback=self._step_callback
        )
        
        console.print("\n[cyan]🎯 토론 순서: 학술 → 뉴스 → 사회 → 논리 → 통계[/cyan]")
        console.print("[dim]각 전문가는 이전 전문가들의 의견을 참고하여 토론합니다.[/dim]\n")
        
        step2_results = step2_crew.kickoff()
        
        # Step 2 토론 결과 정리
        console.print("\n[bold yellow]📝 Step 2 토론 요약[/bold yellow]")
        for agent_name in ["academic", "news", "social", "logic", "statistics"]:
            key = f"{agent_name}_step2"
            if key in self.agent_outputs:
                console.print(f"\n[bold]{self.agents[agent_name].role} 토론 의견:[/bold]")
                output = self.agent_outputs[key]
                # 토론 부분만 추출
                if "동의하는 점:" in output or "반박하는 점:" in output:
                    console.print(Panel(output, border_style="yellow"))
                else:
                    console.print(Panel(output[:500] + "...", border_style="yellow"))
        
        # Step 3: 최종 종합
        console.print("\n[bold blue]📊 Step 3: 최종 종합[/bold blue]")
        
        step3_task = self.create_step3_task(statement)
        
        step3_crew = Crew(
            agents=[self.agents["super"].get_agent("step3")],
            tasks=[step3_task],
            process=Process.sequential,
            verbose=True,
            step_callback=self._step_callback
        )
        
        # 실행
        result = step3_crew.kickoff()
        
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
            
            # 도구 사용 통계
            console.print("\n[bold]📊 도구 사용 통계:[/bold]")
            total_tool_calls = 0
            tool_usage = {}
            
            for step in ["step1", "step2", "step3"]:
                if step in self.tool_calls:
                    for agent_name, calls in self.tool_calls[step].items():
                        total_tool_calls += len(calls)
                        for call in calls:
                            tool = call["tool"]
                            if tool not in tool_usage:
                                tool_usage[tool] = 0
                            tool_usage[tool] += 1
            
            if tool_usage:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("도구 이름", style="cyan")
                table.add_column("호출 횟수", style="yellow")
                
                for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
                    table.add_row(tool, str(count))
                
                console.print(table)
                console.print(f"[dim]총 도구 호출 횟수: {total_tool_calls}회[/dim]")
            
            # 간단한 진행 요약
            console.print("\n[bold]📋 진행 요약:[/bold]")
            console.print(f"• Step 1: 5명의 전문가 초기 분석 완료")
            console.print(f"• Step 2: 전문가 간 토론 완료")
            console.print(f"• Step 3: 최종 종합 판정 완료")
            console.print(f"\n[dim]총 11개의 분석 단계를 거쳤습니다.[/dim]")