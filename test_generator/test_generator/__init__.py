"""
Multi-Agent Test Generator System

Automatically generates pytest tests with 80%+ branch coverage using specialized AI agents.
"""

__version__ = "1.0.0"
__author__ = "Multi-Agent System"

from .orchestrator import Orchestrator
from .agents import (
    CodeAnalyzerAgent,
    UnitTestGeneratorAgent,
    CoverageOptimizerAgent,
    TestValidatorAgent
)
from .llm_client import MockLLMClient, RealLLMClient, GitHubModelsClient, OllamaClient

__all__ = [
    "Orchestrator",
    "CodeAnalyzerAgent",
    "UnitTestGeneratorAgent",
    "CoverageOptimizerAgent",
    "TestValidatorAgent",
    "MockLLMClient",
    "RealLLMClient",
    "GitHubModelsClient",
    "OllamaClient",
]
