"""
Multi-Agent Test Generator System

Automatically generates pytest tests with 80%+ branch coverage using specialized AI agents.
"""

import os
import glob

__version__ = "1.0.0"
__author__ = "Gianmarco Riviello"

# Clean up old test files from output directory on import
def _cleanup_output_directory():
    """Clean up old test files from output directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, '..', 'output')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Remove all test_*.py files in output directory
    test_files = glob.glob(os.path.join(output_dir, 'test_*.py'))
    for test_file in test_files:
        try:
            os.remove(test_file)
        except (OSError, PermissionError):
            # Cleanup is best-effort - file may be in use or already deleted
            # This is intentionally non-fatal as it's just housekeeping
            continue

# Execute cleanup on import
_cleanup_output_directory()

from .orchestrator import LangGraphOrchestrator
from .agents import CodeAnalyzerAgent, UnitTestGeneratorAgent, CoverageOptimizerAgent
from .llm_client import BaseLLMClient, LangChainLLMClient

__all__ = [
    "LangGraphOrchestrator",
    "CodeAnalyzerAgent",
    "UnitTestGeneratorAgent",
    "CoverageOptimizerAgent",
    "BaseLLMClient",
    "LangChainLLMClient",
]
