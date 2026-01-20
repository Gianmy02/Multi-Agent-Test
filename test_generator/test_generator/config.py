"""
Configuration for the Multi-Agent Test Generator System.
"""
import os

# LLM Configuration
USE_MOCK = True  # Set to False to use real LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Coverage Configuration
TARGET_BRANCH_COVERAGE = 80.0  # Minimum branch coverage target (%)
MAX_OPTIMIZATION_ITERATIONS = 5  # Max iterations for coverage optimization

# Test Generation Configuration
MAX_TESTS_PER_FUNCTION = 10 
INCLUDE_EDGE_CASES = True
INCLUDE_ERROR_CASES = True

# Quality Gates
MIN_TEST_QUALITY_SCORE = 7.0  # Out of 10
REQUIRE_MEANINGFUL_ASSERTIONS = True

# Logging
LOG_LEVEL = "INFO"
SAVE_CONVERSATION_LOGS = True
