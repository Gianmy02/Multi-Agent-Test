"""
Specialized agents for test generation system.
Each agent has a specific role in the test generation workflow.
"""
from typing import Dict, Any, Tuple, List
import json
import os
from .llm_client import LLMClient
from .prompts import (
    CODE_ANALYZER_SYSTEM_PROMPT,
    UNIT_TEST_GENERATOR_SYSTEM_PROMPT,
    COVERAGE_OPTIMIZER_SYSTEM_PROMPT,
    TEST_VALIDATOR_SYSTEM_PROMPT
)
from .code_analysis import CodeAnalyzer


class Agent:
    """Base agent class."""
    def __init__(self, client: LLMClient):
        self.client = client

    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Robustly extracts JSON from a string."""
        # Try direct parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
            
        # Try extracting from markdown code blocks
        try:
            if "```json" in response:
                block = response.split("```json")[1].split("```")[0].strip()
                return json.loads(block)
            elif "```" in response:
                block = response.split("```")[1].split("```")[0].strip()
                return json.loads(block)
        except json.JSONDecodeError:
            pass
            
        # Try finding the first '{' and last '}'
        try:
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1:
                json_str = response[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        raise json.JSONDecodeError("Could not extract JSON from response", response, 0)
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, removing markdown formatting."""
        # Clean up potential markdown formatting
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()
        
        return code


from lark import Lark, UnexpectedInput
from lark.indenter import Indenter

class PythonIndenter(Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

class CodeAnalyzerAgent(Agent):
    """
    Analyzes Python code to identify functions and branch points.
    Uses Lark for syntax validation and AST for structure extraction.
    """
    def __init__(self, client: LLMClient):
        super().__init__(client)
        # Load Lark grammar
        try:
            grammar_path = os.path.join(os.path.dirname(__file__), "python_subset.lark")
            with open(grammar_path, "r") as f:
                self.grammar = f.read()
            self.parser = Lark(
                self.grammar, 
                start='start', 
                parser='lalr',
                postlex=PythonIndenter()
            )
            self.lark_enabled = True
        except Exception as e:
            print(f"[CodeAnalyzer] WARNING: Could not load Lark grammar: {e}")
            self.lark_enabled = False

    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code and return branch map.
        
        STRICT MODE: Code MUST conform to the defined Lark grammar.
        If validation fails, an error is raised.
        
        Args:
            code: Python source code to analyze (must conform to python_subset.lark)
            
        Returns:
            Dictionary with functions and branch information
            
        Raises:
            SyntaxError: If code does not conform to the defined grammar subset
            RuntimeError: If Lark parser is not available
        """
        if self.client.verbose:
            print(f"[CodeAnalyzer] Analyzing code...")
        
        # Step 1: MANDATORY Lark Validation (Academic Requirement)
        if not self.lark_enabled:
            raise RuntimeError(
                "[CodeAnalyzer] ERROR: Lark parser not available. "
                "Cannot validate code against defined grammar subset."
            )
        
        print("[CodeAnalyzer] Validating syntax with Lark Parser (STRICT MODE)...")
        try:
            parse_tree = self.parser.parse(code.strip())
            print("[CodeAnalyzer] [PASS] Lark Validation: Code conforms to Language Subset")
        except UnexpectedInput as e:
            error_msg = (
                f"\n{'='*70}\n"
                f"[CodeAnalyzer] [FAIL] VALIDATION FAILED\n"
                f"{'='*70}\n"
                f"The input code does NOT conform to the defined grammar subset.\n"
                f"\nGrammar File: python_subset.lark\n"
                f"Allowed constructs:\n"
                f"  - Function definitions (def)\n"
                f"  - Control flow (if/elif/else)\n"
                f"  - Basic assignments and expressions\n"
                f"\nNOT allowed:\n"
                f"  - Classes (class)\n"
                f"  - Decorators (@)\n"
                f"  - List comprehensions\n"
                f"  - Advanced Python features\n"
                f"\nParser Error Details:\n"
                f"  {e}\n"
                f"{'='*70}\n"
            )
            print(error_msg)
            raise SyntaxError(
                "Code validation failed: Input code exceeds the defined language subset. "
                "Please ensure your code only uses functions and basic control flow."
            ) from e
        except Exception as e:
            raise RuntimeError(f"[CodeAnalyzer] Lark parsing error: {e}") from e

        # Step 2: Use AST-based analyzer for detailed extraction
        # (AST is used only for extracting details, Lark already validated syntax)
        analysis = CodeAnalyzer.analyze_file(code)
        
        if "error" not in analysis:
            if self.client.verbose:
                print(f"[CodeAnalyzer] Found {len(analysis['functions'])} functions")
                print(f"[CodeAnalyzer] Total branches: {analysis['total_branches_in_file']}")
            return analysis
        
        # If AST fails (shouldn't happen if Lark passed), report error
        raise RuntimeError(
            f"[CodeAnalyzer] AST analysis failed after successful Lark validation. "
            f"This indicates an internal error: {analysis.get('error', 'Unknown error')}"
        )


class UnitTestGeneratorAgent(Agent):
    """
    Generates pytest unit tests based on branch map.
    """
    def generate_tests(self, code: str, branch_map: Dict[str, Any], module_name: str = "code_to_test", verbose: bool = False) -> str:
        """
        Generate comprehensive unit tests.
        
        Args:
            code: Source code to test
            branch_map: Branch map from CodeAnalyzer
            module_name: Name of the module being tested
            verbose: If True, print debug messages
            
        Returns:
            Generated pytest test code
        """
        if verbose:
            print(f"[UnitTestGenerator] Generating tests...")
        
        prompt = f"""Generate comprehensive pytest tests for this code:

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

        response = self.client.generate(
            prompt=prompt,
            system_prompt=UNIT_TEST_GENERATOR_SYSTEM_PROMPT
        )
        
        tests = self._extract_code(response)
        
        # Count generated tests
        test_count = tests.count("def test_")
        if verbose:
            print(f"[UnitTestGenerator] Generated {test_count} tests")
        
        return tests


class CoverageOptimizerAgent(Agent):
    """
    Generates additional tests to cover uncovered branches.
    """
    def optimize_coverage(
        self,
        code: str,
        current_tests: str,
        coverage_result: Dict[str, Any],
        branch_map: Dict[str, Any],
        module_name: str = "code_to_test",
        verbose: bool = False
    ) -> str:
        """
        Generate additional tests to improve coverage.
        
        Args:
            code: Source code
            current_tests: Existing test suite
            coverage_result: Coverage report with uncovered branches
            branch_map: Original branch map
            module_name: Module name
            
        Returns:
            Additional test code to append
        """
        if verbose:
            print(f"[CoverageOptimizer] Current coverage: {coverage_result.get('branch_coverage', 0):.1f}%")
            print(f"[CoverageOptimizer] Generating additional tests...")
        
        uncovered = coverage_result.get('uncovered_branches', [])
        
        prompt = f"""The current test suite has {coverage_result.get('branch_coverage', 0):.1f}% branch coverage.

Original Code:
```python
{code}
```

Current Tests:
```python
{current_tests}
```

Coverage Report:
- Branch Coverage: {coverage_result.get('branch_coverage', 0):.1f}%
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

        response = self.client.generate(
            prompt=prompt,
            system_prompt=COVERAGE_OPTIMIZER_SYSTEM_PROMPT
        )
        
        additional_tests = self._extract_code(response)
        
        # Count new tests
        new_test_count = additional_tests.count("def test_")
        if verbose:
            print(f"[CoverageOptimizer] Generated {new_test_count} additional tests")
        
        return additional_tests


class TestValidatorAgent(Agent):
    """
    Validates test quality and provides quality score.
    """
    def validate(self, tests: str, code: str, coverage_result: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
        """
        Validate test suite quality.
        
        Args:
            tests: Test suite code
            code: Source code being tested
            coverage_result: Coverage results
            verbose: If True, print debug messages
            
        Returns:
            Validation result with quality score
        """
        if verbose:
            print(f"[TestValidator] Validating test quality...")
        
        prompt = f"""Evaluate the quality of this test suite:

Tests:
```python
{tests}
```

Code Under Test:
```python
{code}
```

Coverage Results:
- Branch Coverage: {coverage_result.get('branch_coverage', 0):.1f}%
- Total Coverage: {coverage_result.get('total_coverage', 0):.1f}%
- Tests Run: {coverage_result.get('tests_run', 0)}

Evaluate based on:
1. Meaningful assertions (not just assert True)
2. Branch coverage completeness
3. Test independence
4. Clear naming and comments
5. Edge case coverage
6. Error handling tests
7. No duplicate tests

Provide quality score (0-10) and detailed feedback."""

        response = self.client.generate(
            prompt=prompt,
            system_prompt=TEST_VALIDATOR_SYSTEM_PROMPT
        )
        
        try:
            validation = self._extract_json(response)
            score = validation.get("quality_score", 0)
            passed = validation.get("passed_quality_gate", False)
            
            if verbose:
                print(f"[TestValidator] Quality Score: {score}/10")
                print(f"[TestValidator] Quality Gate: {'PASSED' if passed else 'FAILED'}")
            
            return validation
        except json.JSONDecodeError as e:
            print(f"[TestValidator] Error parsing validation: {e}")
            return {
                "quality_score": 5.0,
                "issues": ["Could not parse validation response"],
                "suggestions": [],
                "passed_quality_gate": False
            }
