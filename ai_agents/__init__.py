"""
AI Agents for Enhanced Ethical AI Development and Bias Detection

This package provides AI agent capabilities for the watching_u_watching project,
designed to automate and enhance various aspects of ethical AI development,
bias detection, and overall project management.

Core Principles:
- NO HARM above else
- Human oversight required for all critical decisions
- Transparent and auditable operations
- Ethical compliance verification at every step
"""

__version__ = "0.1.0"

from .core import EthicalAIAgent
from .research import ResearchAgent
from .compliance import ComplianceAgent
from .monitoring import BiasMonitoringAgent

__all__ = [
    "EthicalAIAgent",
    "ResearchAgent", 
    "ComplianceAgent",
    "BiasMonitoringAgent"
]