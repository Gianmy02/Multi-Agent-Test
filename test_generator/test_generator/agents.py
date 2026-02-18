"""
Specialized agents for test generation system.
Each agent has a specific role in the test generation workflow.
"""

from typing import Dict, Any
import ast
import os
from lark import Lark, UnexpectedInput
from lark.indenter import Indenter
from .llm_client import BaseLLMClient
from .prompts import UNIT_TEST_GENERATOR_SYSTEM_PROMPT, COVERAGE_OPTIMIZER_SYSTEM_PROMPT
from .code_analysis import CodeAnalyzer
from . import config


class Agent:
    """Base class for all agents."""
    def __init__(self, client: BaseLLMClient) -> None:
        self.client = client
        self.logger = config.setup_logging(getattr(client, "verbose", False))

    @staticmethod
    def _count_tests(test_code: str) -> int:
        """Count number of test functions in code using AST.
        
        Args:
            test_code: Python test code
            
        Returns:
            Number of test functions found
        """
        try:
            tree = ast.parse(test_code)
            count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    count += 1
            return count
        except SyntaxError:
            # Fallback to textual parsing if AST parsing fails
            return test_code.count("def test_")

    def _extract_code(self, response: str) -> str:
        """Extract Python code from response, removing markdown formatting.
        
        Args:
            response: LLM response potentially containing code blocks
            
        Returns:
            Extracted Python code
        """
        # Clean up potential markdown formatting
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0].strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0].strip()
        else:
            code = response.strip()

        return code


class PythonIndenter(Indenter):
    """Custom indenter for Lark Python grammar parsing.
    Handles Python's significant whitespace with 4-space indentation."""
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = config.PYTHON_INDENT_SIZE  # Use config constant instead of magic number


# Module-level cache for Lark parser (optimization: load grammar only once)
_LARK_PARSER_CACHE = None


class CodeAnalyzerAgent(Agent):
    """
    Analyzes Python code to identify functions and branch points.
    Uses Lark for syntax validation and AST for structure extraction.
    """

    def __init__(self, client: BaseLLMClient) -> None:
        super().__init__(client)
        
        # Use module-level cache to avoid reloading grammar on every instantiation
        global _LARK_PARSER_CACHE
        
        if _LARK_PARSER_CACHE is None:
            # Load Lark grammar only once
            try:
                grammar_path = os.path.join(os.path.dirname(__file__), "python_subset.lark")
                with open(grammar_path, "r", encoding="utf-8") as f:
                    grammar = f.read()
                _LARK_PARSER_CACHE = Lark(grammar, start="start", parser="lalr", postlex=PythonIndenter())
                self.lark_enabled = True
            except Exception as e:
                self.logger.warning(f"Could not load Lark grammar: {e}")
                _LARK_PARSER_CACHE = None
                self.lark_enabled = False
        else:
            # Use cached parser
            self.lark_enabled = _LARK_PARSER_CACHE is not None
        
        self.parser = _LARK_PARSER_CACHE

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
        self.logger.info("Analyzing code...")

        # Step 1: MANDATORY Lark Validation (Academic Requirement)
        if not self.lark_enabled:
            raise RuntimeError(
                "[CodeAnalyzer] ERROR: Lark parser not available. "
                "Cannot validate code against defined grammar subset."
            )

        self.logger.info("Validating syntax with Lark Parser (STRICT MODE)...")
        try:
            self.parser.parse(code.strip())
            self.logger.info("[PASS] Lark Validation: Code conforms to Language Subset")
        except UnexpectedInput as e:
            error_msg = (
                f"Grammar validation FAILED! Code contains unsupported constructs.\n"
                f"Error at line {e.line}, column {e.column}\n"
                f"Expected: {e.expected}\n\n"
                f"Supported Python subset: functions, if/else, basic operators.\n"
                f"NOT supported: classes, for/while, elif, try/except, decorators, etc."
            )
            self.logger.error(error_msg)
            raise SyntaxError(error_msg) from e
        except Exception as e:
            raise RuntimeError(f"[CodeAnalyzer] Lark parsing error: {e}") from e

        # Step 2: AST analysis
        analysis = CodeAnalyzer.analyze_file(code)
        
        if "error" not in analysis:
            self.logger.info(f"Found {len(analysis['functions'])} functions")
            self.logger.info(f"Total branches: {analysis['total_branches_in_file']}")
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

    def generate_tests(
        self, 
        code: str, 
        branch_map: Dict[str, Any], 
        module_name: str = "code_to_test", 
        verbose: bool = False
    ) -> str:
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
            self.logger.info("Generating tests...")
        
        # Use prompts module for prompt construction (DRY principle)
        from .prompts import build_test_generation_prompt
        prompt = build_test_generation_prompt(code, branch_map, module_name)

        response = self.client.generate(prompt=prompt, system_prompt=UNIT_TEST_GENERATOR_SYSTEM_PROMPT)

        tests = self._extract_code(response)

        test_count = self._count_tests(tests)
        if verbose:
            self.logger.info(f"Generated {test_count} tests")

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
        verbose: bool = False,
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
            self.logger.info(f"Current coverage: {coverage_result.get('branch_coverage', 0):.1f}%")
            self.logger.info("Generating additional tests...")
        
        # Use prompts module for prompt construction (DRY principle)
        from .prompts import build_coverage_optimization_prompt
        prompt = build_coverage_optimization_prompt(
            code, current_tests, coverage_result, branch_map, module_name
        )

        response = self.client.generate(prompt=prompt, system_prompt=COVERAGE_OPTIMIZER_SYSTEM_PROMPT)

        additional_tests = self._extract_code(response)

        new_test_count = self._count_tests(additional_tests)
        if verbose:
            self.logger.info(f"Generated {new_test_count} additional tests")

        return additional_tests
