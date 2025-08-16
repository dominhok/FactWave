"""FactWave Agents Module"""

from .academic_agent import AcademicAgent
from .news_agent import NewsAgent
from .social_agent import SocialAgent
from .logic_agent import LogicAgent
from .statistics_agent import StatisticsAgent
from .super_agent import SuperAgent

__all__ = [
    "AcademicAgent",
    "NewsAgent", 
    "SocialAgent",
    "LogicAgent",
    "StatisticsAgent",
    "SuperAgent"
]