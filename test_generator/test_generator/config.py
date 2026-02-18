"""
Configuration for the Multi-Agent Test Generator System.

SECURITY NOTE:
- GOOGLE_API_KEY should be set as environment variable (NOT hardcoded)
- Set via: export GOOGLE_API_KEY='your-key-here' (Linux/Mac)
- Or via: $env:GOOGLE_API_KEY='your-key-here' (PowerShell)
- Or create .env file (add .env to .gitignore)
"""

import os
import sys

# LLM Configuration - API Key from Environment Variable (SECURE)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Coverage Configuration
TARGET_BRANCH_COVERAGE = 80.0  # Minimum branch coverage target (%)

# Max iterations for coverage optimization (configurable via env var)
# Valid range: 1-20 (default: 5)
try:
    MAX_OPTIMIZATION_ITERATIONS = int(os.getenv("MAX_OPTIMIZATION_ITERATIONS", "5"))
    if not (1 <= MAX_OPTIMIZATION_ITERATIONS <= 20):
        raise ValueError(
            f"MAX_OPTIMIZATION_ITERATIONS must be between 1 and 20, got {MAX_OPTIMIZATION_ITERATIONS}"
        )
except ValueError as e:
    print(f"WARNING: Invalid MAX_OPTIMIZATION_ITERATIONS - {e}", file=sys.stderr)
    print("WARNING: Using default value: 5", file=sys.stderr)
    MAX_OPTIMIZATION_ITERATIONS = 5

# Test execution timeout in seconds (configurable via env var)
# Valid range: 10-300 (default: 60)
try:
    TEST_EXECUTION_TIMEOUT = int(os.getenv("TEST_EXECUTION_TIMEOUT", "60"))
    if not (10 <= TEST_EXECUTION_TIMEOUT <= 300):
        raise ValueError(
            f"TEST_EXECUTION_TIMEOUT must be between 10 and 300 seconds, got {TEST_EXECUTION_TIMEOUT}"
        )
except ValueError as e:
    print(f"WARNING: Invalid TEST_EXECUTION_TIMEOUT - {e}", file=sys.stderr)
    print("WARNING: Using default value: 60", file=sys.stderr)
    TEST_EXECUTION_TIMEOUT = 60


# LLM Configuration
DEFAULT_LLM_TEMPERATURE = 0.2  # Temperature for LLM generation (0.0 = deterministic, 1.0 = creative)

# Retry configuration for API calls
API_RETRY_ATTEMPTS = 3  # Number of retry attempts for transient failures
API_RETRY_MIN_WAIT = 2  # Minimum wait time in seconds between retries
API_RETRY_MAX_WAIT = 10  # Maximum wait time in seconds between retries
API_RETRY_MULTIPLIER = 1  # Exponential backoff multiplier

# Code Analysis Configuration
PYTHON_INDENT_SIZE = 4  # Number of spaces per indentation level


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

import logging
import sys

def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        verbose: If True, set log level to DEBUG; otherwise INFO
        
    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logger
    logger = logging.getLogger("test_generator")
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="[%(name)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Default logger instance
logger = setup_logging()

