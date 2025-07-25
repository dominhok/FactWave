#!/usr/bin/env python3
"""
FactWave Prototype - Simple multi-agent fact-checking system using CrewAI
"""

import os
import yaml
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

load_dotenv()

# Setup console for pretty output
console = Console()

# Setup OpenAI client for Upstage Solar-pro2
api_key = os.getenv("UPSTAGE_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key  # CrewAI expects this env var
os.environ["OPENAI_API_BASE"] = "https://api.upstage.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "solar-pro2"

# LiteLLM settings for custom OpenAI-compatible endpoint
os.environ["OPENAI_BASE_URL"] = "https://api.upstage.ai/v1"
os.environ["LITELLM_LOG"] = "DEBUG"  # For debugging

# Load configuration from YAML
with open("agents_config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

VERDICT_OPTIONS = config["verdict_options"]
AGENT_WEIGHTS = config["agent_weights"]
AGENTS_CONFIG = config["agents"]
TASK_PROMPTS = config["task_prompts"]
EXPECTED_OUTPUTS = config["expected_outputs"]


class FactWaveAgents:
    """Factory class for creating specialized fact-checking agents"""
    
    @staticmethod
    def create_agent(agent_type: str):
        """Create an agent based on the configuration"""
        agent_config = AGENTS_CONFIG[agent_type]
        return Agent(
            role=agent_config["role"],
            goal=agent_config["goal"],
            backstory=agent_config["backstory"],
            verbose=True,
            allow_delegation=False,
            llm="openai/solar-pro2"  # LiteLLM format
        )
    
    @staticmethod
    def create_academic_agent():
        return FactWaveAgents.create_agent("academic")
    
    @staticmethod
    def create_news_agent():
        return FactWaveAgents.create_agent("news")
    
    @staticmethod
    def create_logic_agent():
        return FactWaveAgents.create_agent("logic")
    
    @staticmethod
    def create_social_agent():
        return FactWaveAgents.create_agent("social")
    
    @staticmethod
    def create_super_agent():
        return FactWaveAgents.create_agent("super")


class FactWaveCrew:
    """Main orchestrator for the fact-checking process"""
    
    def __init__(self):
        self.agents = {
            "academic": FactWaveAgents.create_academic_agent(),
            "news": FactWaveAgents.create_news_agent(),
            "logic": FactWaveAgents.create_logic_agent(),
            "social": FactWaveAgents.create_social_agent(),
            "super": FactWaveAgents.create_super_agent()
        }
    
    def check_fact(self, statement: str):
        """Run the fact-checking process on a given statement"""
        
        console.print(f"\n[bold cyan]팩트체크 중:[/bold cyan] {statement}\n")
        
        # Phase 1: Initial Analysis Tasks
        initial_tasks = []
        
        for agent_name, agent in self.agents.items():
            if agent_name != "super":  # Super agent comes later
                task = Task(
                    description=TASK_PROMPTS["initial_analysis"].format(statement=statement),
                    agent=agent,
                    expected_output=EXPECTED_OUTPUTS["initial_analysis"]
                )
                initial_tasks.append(task)
        
        # Phase 2: Debate Task (agents review each other's work)
        debate_task = Task(
            description=TASK_PROMPTS["debate"].format(statement=statement),
            agent=self.agents["academic"],  # All agents participate, starting with academic
            expected_output=EXPECTED_OUTPUTS["debate"]
        )
        
        # Phase 3: Final Synthesis Task
        verdict_options_str = "\n".join([f"- {k}: {v}" for k, v in VERDICT_OPTIONS.items()])
        synthesis_task = Task(
            description=TASK_PROMPTS["synthesis"].format(
                statement=statement,
                verdict_options=verdict_options_str
            ),
            agent=self.agents["super"],
            expected_output=EXPECTED_OUTPUTS["synthesis"]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=initial_tasks + [debate_task, synthesis_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Show progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("팩트체크 분석 실행 중...", total=None)
            
            result = crew.kickoff()
            
            progress.update(task, completed=True)
        
        return result


def display_results(result):
    """Display the fact-checking results in a nice format"""
    console.print("\n[bold green]✓ 팩트체크 완료![/bold green]\n")
    
    # Create a panel with the final verdict
    panel = Panel(
        str(result),
        title="[bold]최종 팩트체크 보고서[/bold]",
        border_style="green",
        padding=(1, 2)
    )
    console.print(panel)


def main():
    """Main CLI interface"""
    console.print("""
[bold cyan]🔍 FactWave 프로토타입[/bold cyan]
[dim]Solar-pro2 기반 다중 에이전트 팩트체킹 시스템[/dim]
    """)
    
    # Initialize the crew
    fact_checker = FactWaveCrew()
    
    while True:
        console.print("\n[bold]팩트체크할 문장을 입력하세요[/bold] ('quit'로 종료):")
        statement = input("> ").strip()
        
        if statement.lower() in ['quit', 'exit', 'q']:
            console.print("\n[dim]안녕히 가세요! 👋[/dim]")
            break
        
        if not statement:
            console.print("[red]확인할 문장을 입력해주세요.[/red]")
            continue
        
        try:
            # Run fact-check
            result = fact_checker.check_fact(statement)
            
            # Display results
            display_results(result)
            
        except Exception as e:
            console.print(f"\n[red]팩트체킹 중 오류 발생: {e}[/red]")
            console.print("[dim]다른 문장으로 다시 시도해주세요.[/dim]")


if __name__ == "__main__":
    main()