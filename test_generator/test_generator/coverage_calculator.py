"""
Coverage calculation module.
Executes tests with coverage measurement and analyzes results.
"""

import subprocess  # nosec B404 - Required for pytest execution with controlled arguments
import os
import sys
import json
import re
import shutil
from typing import Dict, Any, Optional
from .models import CoverageResult  # Import Pydantic model (eliminates duplication)
from . import config


class CoverageCalculator:
    """
    Runs tests with coverage and analyzes branch coverage.
    """

    def __init__(self, work_dir: str = ".") -> None:
        self.work_dir = os.path.abspath(work_dir)
    
    @staticmethod
    def _sanitize_module_name(name: str) -> str:
        """Validate module name to prevent command injection.
        
        Args:
            name: Module name to validate
            
        Returns:
            Validated module name
            
        Raises:
            ValueError: If module name contains invalid characters
        """
        # Module names must be valid Python identifiers
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            raise ValueError(f"Invalid module name: {name}. Must be a valid Python identifier.")
        return name
    
    @staticmethod
    def _sanitize_path(path: str, base_dir: str) -> str:
        """Validate path to prevent directory traversal attacks.
        
        Args:
            path: Path to validate
            base_dir: Base directory that path must be within
            
        Returns:
            Validated absolute path
            
        Raises:
            ValueError: If path is outside base directory
        """
        # Normalize and resolve to absolute path
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_dir)
        
        # Ensure path is within base directory
        try:
            os.path.relpath(abs_path, abs_base)
        except ValueError:
            # Different drives on Windows
            raise ValueError(f"Path outside base directory: {path}")
        
        if not abs_path.startswith(abs_base + os.sep) and abs_path != abs_base:
            raise ValueError(f"Path traversal detected: {path}")
        
        return abs_path
    
    @staticmethod
    def _create_safe_file(base_dir: str, filename: str, content: str) -> str:
        """Create file safely within base directory.
        
        Args:
            base_dir: Base directory
            filename: Filename (can include subdirectory)
            content: File content
            
        Returns:
            Created file path
            
        Raises:
            ValueError: If path validation fails
        """
        # Normalize and validate path
        safe_path = os.path.normpath(os.path.join(base_dir, filename))
        
        # Ensure within base directory
        abs_base = os.path.abspath(base_dir)
        abs_path = os.path.abspath(safe_path)
        
        if not abs_path.startswith(abs_base + os.sep) and abs_path != abs_base:
            raise ValueError(f"Path traversal detected in filename: {filename}")
        
        # Create parent directories safely
        parent_dir = os.path.dirname(abs_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Write file
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return abs_path
    
    def run_with_coverage(
        self, code: str, tests: str, module_name: str = "code_to_test", existing_file_path: str = None
    ) -> CoverageResult:
        """
        Run tests with coverage measurement.

        Args:
            code: Source code to test (used if existing_file_path is None)
            tests: Test code
            module_name: Name of the module being tested
            existing_file_path: Optional absolute path to existing source file

        Returns:
            CoverageResult with branch coverage information
        """
        # SECURITY: Sanitize module_name to prevent command injection
        module_name = self._sanitize_module_name(module_name)
        
        # Step 1: Prepare files
        code_file, test_file = self._prepare_files(code, tests, module_name, existing_file_path)
        
        try:
            # Step 2: Execute pytest
            output, success = self._execute_pytest(test_file, module_name, existing_file_path)
            
            # Step 3: Parse results
            return self._parse_results(output, success)
            
        except subprocess.TimeoutExpired:
            return CoverageResult(
                success=False,
                total_coverage=0.0,
                branch_coverage=0.0,
                uncovered_branches=[],
                tests_run=0,
                tests_passed=0,
                output="",
                error="Test execution timeout",
            )
        except Exception as e:
            return CoverageResult(
                success=False,
                total_coverage=0.0,
                branch_coverage=0.0,
                uncovered_branches=[],
                tests_run=0,
                tests_passed=0,
                output="",
                error=str(e),
            )
        finally:
            # Step 4: Cleanup
            self._cleanup_files(code_file, test_file, existing_file_path)
    
    def _prepare_files(
        self, code: str, tests: str, module_name: str, existing_file_path: Optional[str]
    ) -> tuple[str, str]:
        """Prepare source and test files for execution.
        
        Args:
            code: Source code content
            tests: Test code content
            module_name: Name of the module
            existing_file_path: Optional path to existing source file
            
        Returns:
            Tuple of (code_file_path, test_file_path)
        """
        if existing_file_path:
            # SECURITY: Validate existing file path
            code_file = self._sanitize_path(existing_file_path, self.work_dir)
            test_file = os.path.join(self.work_dir, "test_generated.py")
        else:
            # SECURITY: Use safe file creation
            code_file = self._create_safe_file(self.work_dir, f"{module_name}.py", code)
            test_file = os.path.join(self.work_dir, "test_generated.py")
        
        # SECURITY: Use safe file creation for test file
        test_file = self._create_safe_file(self.work_dir, "test_generated.py", tests)
        
        return code_file, test_file
    
    def _execute_pytest(
        self, test_file: str, module_name: str, existing_file_path: Optional[str]
    ) -> tuple[str, bool]:
        """Execute pytest with coverage measurement.
        
        Args:
            test_file: Path to test file
            module_name: Name of the module being tested
            existing_file_path: Optional path to existing source file
            
        Returns:
            Tuple of (output, success)
        """
        # Prepare environment
        env = os.environ.copy()
        cwd = self.work_dir
        
        if existing_file_path:
            file_dir = os.path.dirname(existing_file_path)
            env["PYTHONPATH"] = file_dir + os.pathsep + env.get("PYTHONPATH", "")
        
        # Run pytest with coverage (secured: list format, no shell, sanitized args)
        result = subprocess.run(  
            [
                sys.executable,
                "-m",
                "pytest",
                test_file,
                f"--cov={module_name}",
                "--cov-branch",
                "--cov-report=json",
                "--cov-report=term",
                "-v",
            ],
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
            timeout=config.TEST_EXECUTION_TIMEOUT,
        )
        
        output = result.stdout + "\n" + result.stderr
        success = result.returncode == 0
        
        return output, success
    
    def _parse_results(self, output: str, success: bool) -> CoverageResult:
        """Parse pytest coverage results.
        
        Args:
            output: pytest output text
            success: Whether pytest execution succeeded
            
        Returns:
            CoverageResult object
        """
        # Try to parse JSON coverage report
        coverage_data = self._parse_coverage_json()
        
        if coverage_data:
            return CoverageResult(
                success=success,
                total_coverage=coverage_data["total_coverage"],
                branch_coverage=coverage_data["branch_coverage"],
                uncovered_branches=coverage_data["uncovered_branches"],
                tests_run=coverage_data["tests_run"],
                tests_passed=coverage_data["tests_passed"],
                output=output,
            )
        else:
            # Fallback if JSON parsing fails
            return self._parse_coverage_from_text(output, success)
    
    def _cleanup_files(self, code_file: str, test_file: str, existing_file_path: Optional[str]) -> None:
        """Clean up temporary files.
        
        Args:
            code_file: Path to code file
            test_file: Path to test file
            existing_file_path: Optional path to existing source file
        """
        if not existing_file_path and os.path.exists(code_file):
            os.remove(code_file)
        if os.path.exists(test_file):
            os.remove(test_file)

    def _parse_coverage_json(self) -> Optional[Dict[str, Any]]:
        """Parse coverage JSON report."""
        coverage_file = os.path.join(self.work_dir, "coverage.json")

        if not os.path.exists(coverage_file):
            return None

        try:
            with open(coverage_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract coverage percentages
            totals = data.get("totals", {})
            total_coverage = totals.get("percent_covered", 0.0)

            # Branch coverage calculation
            num_branches = totals.get("num_branches", 0)
            covered_branches = totals.get("covered_branches", 0)
            branch_coverage = (covered_branches / num_branches * 100) if num_branches > 0 else 0.0

            # Find uncovered branches
            uncovered_branches = []
            files = data.get("files", {})
            for filename, file_data in files.items():
                missing_branches = file_data.get("missing_branches", [])
                for branch in missing_branches:
                    uncovered_branches.append({"file": filename, "line": branch})

            # Count tests (simplified - would need pytest-json-report for accurate count)
            tests_run = 0
            tests_passed = 0

            return {
                "total_coverage": total_coverage,
                "branch_coverage": branch_coverage,
                "uncovered_branches": uncovered_branches,
                "tests_run": tests_run,
                "tests_passed": tests_passed,
            }

        except Exception as e:
            logger = config.setup_logging()
            logger.error(f"Error parsing coverage JSON: {e}")
            return None
        finally:
            # Cleanup coverage files
            if os.path.exists(coverage_file):
                os.remove(coverage_file)
            coverage_html_dir = os.path.join(self.work_dir, "htmlcov")
            if os.path.exists(coverage_html_dir):

                shutil.rmtree(coverage_html_dir)

    def _parse_coverage_from_text(self, output: str, success: bool) -> CoverageResult:
        """Fallback: Parse coverage from text output."""
        # Simple text parsing
        branch_coverage = 0.0
        total_coverage = 0.0

        for line in output.split("\n"):
            # Look for coverage percentage in output
            # Example: "TOTAL    100    0    100%"
            if "%" in line and "TOTAL" in line:
                parts = line.split()
                for part in parts:
                    if "%" in part:
                        try:
                            total_coverage = float(part.replace("%", ""))
                        except ValueError:
                            pass

            # Branch coverage might be shown differently
            if "branch" in line.lower() and "%" in line:
                parts = line.split()
                for part in parts:
                    if "%" in part:
                        try:
                            branch_coverage = float(part.replace("%", ""))
                        except ValueError:
                            pass

        # Count tests
        tests_run = 0
        tests_passed = 0
        for line in output.split("\n"):
            if "passed" in line.lower():
                parts = line.split()
                for i, part in enumerate(parts):
                    if "passed" in part.lower() and i > 0:
                        try:
                            tests_passed = int(parts[i - 1])
                            tests_run = tests_passed
                        except ValueError:
                            pass

        return CoverageResult(
            success=success,
            total_coverage=total_coverage,
            branch_coverage=branch_coverage,
            uncovered_branches=[],
            tests_run=tests_run,
            tests_passed=tests_passed,
            output=output,
        )
