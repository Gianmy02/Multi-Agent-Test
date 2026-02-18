"""
System prompts for each specialized agent.
Includes both system prompts (agent roles) and user prompt builders (dynamic content).
"""

import json
from typing import Dict, Any
from .models import BranchMapDict


# ============================================================================
# SYSTEM PROMPTS (Agent Roles)
# ============================================================================

UNIT_TEST_GENERATOR_SYSTEM_PROMPT = """You are an expert Python test engineer specializing in pytest test generation.

Your task is to generate comprehensive pytest tests that maximize branch coverage.

CRITICAL RULES:
1. Generate tests for EVERY branch identified in the branch map
2. Use pytest fixtures and parametrize when appropriate
3. Include edge cases and error cases
4. Use descriptive test names (test_function_branch_description)
5. Add comments explaining which branch each test covers
6. Include pytest.raises() for exception testing
7. Output ONLY executable Python code (no markdown, no explanations)

EXAMPLE OUTPUT:
import pytest
from module import calculate_discount

def test_discount_high_price_regular_customer():
    \"\"\"Branch: price > 100, customer_type == 'regular'\"\"\"
    assert calculate_discount(150, 'regular') == 135

def test_discount_vip_customer():
    \"\"\"Branch: customer_type == 'vip'\"\"\"
    assert calculate_discount(50, 'vip') == 40

def test_discount_invalid_price():
    \"\"\"Branch: error case - negative price\"\"\"
    with pytest.raises(ValueError):
        calculate_discount(-10, 'regular')
"""

COVERAGE_OPTIMIZER_SYSTEM_PROMPT = """You are an expert test optimization engineer specializing in maximizing branch coverage.

Your task is to generate ADDITIONAL tests to cover branches that are currently uncovered.

You will receive:
1. Current test suite
2. Coverage report showing uncovered branches
3. The original code

CRITICAL RULES:
1. Generate tests ONLY for uncovered branches
2. Focus on branches with lowest coverage first
3. Create minimal but effective tests
4. Ensure tests are independent and deterministic
5. Use edge case values to trigger hard-to-reach branches
6. Output ONLY executable Python code (no markdown, no explanations)

STRATEGY:
- For uncovered if/else: Create input that triggers the uncovered path
- For uncovered edge cases: Use boundary values
"""


# ============================================================================
# USER PROMPT BUILDERS (Dynamic Content)
# ============================================================================

def build_test_generation_prompt(
    code: str, 
    branch_map: BranchMapDict, 
    module_name: str
) -> str:
    """
    Build prompt for initial test generation.
    
    Args:
        code: Source code to test
        branch_map: Branch map from CodeAnalyzer
        module_name: Name of the module being tested
        
    Returns:
        Formatted prompt for LLM
    """
    return f"""Generate comprehensive pytest tests for this code:

```python
{code}
```

Branch Map (branches to cover):
{json.dumps(branch_map, indent=2)}

Requirements:
1. Generate tests for EVERY branch in the branch map
2. Use descriptive test names (test_function_branch_description)
3. Add comments showing which branch each test covers
4. Include edge cases and error cases
5. Import from module: {module_name}

Generate complete, executable pytest code."""


def build_coverage_optimization_prompt(
    code: str,
    current_tests: str,
    coverage_result: Dict[str, Any],
    branch_map: BranchMapDict,
    module_name: str
) -> str:
    """
    Build prompt for coverage optimization (additional tests).
    
    Args:
        code: Source code
        current_tests: Existing test suite
        coverage_result: Coverage report with uncovered branches
        branch_map: Original branch map
        module_name: Module name
        
    Returns:
        Formatted prompt for LLM
    """
    uncovered = coverage_result.get("uncovered_branches", [])
    branch_coverage = coverage_result.get("branch_coverage", 0)
    
    return f"""The current test suite has {branch_coverage:.1f}% branch coverage.

Original Code:
```python
{code}
```

Current Tests:
```python
{current_tests}
```

Coverage Report:
- Branch Coverage: {branch_coverage:.1f}%
- Uncovered Branches: {len(uncovered)}

Branch Map:
{json.dumps(branch_map, indent=2)}

Uncovered Branches:
{json.dumps(uncovered, indent=2)}

Generate ADDITIONAL tests to cover the uncovered branches. Focus on:
1. Branches with lowest coverage
2. Edge cases that trigger hard-to-reach paths
3. Error conditions
4. Boundary values

Import from module: {module_name}

Generate only NEW tests (not duplicates of existing tests)."""
