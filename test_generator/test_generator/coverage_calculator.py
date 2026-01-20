"""
Coverage calculation module.
Executes tests with coverage measurement and analyzes results.
"""
import subprocess
import tempfile
import os
import sys
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CoverageResult:
    """Result of coverage analysis."""
    success: bool
    total_coverage: float  # Statement coverage %
    branch_coverage: float  # Branch coverage %
    uncovered_branches: List[Dict[str, Any]]
    tests_run: int
    tests_passed: int
    output: str
    error: Optional[str] = None


class CoverageCalculator:
    """
    Runs tests with coverage and analyzes branch coverage.
    """
    
    def __init__(self, work_dir: str = "."):
        self.work_dir = work_dir
    
    def run_with_coverage(self, code: str, tests: str, module_name: str = "code_to_test", existing_file_path: str = None) -> CoverageResult:
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
        # Create temporary files
        if existing_file_path:
            # If testing existing file, don't write generic code file.
            # Use the existing file's directory as PYTHONPATH base
            code_file = existing_file_path
            # We still need to write the test file, but maybe in a temp location or same dir
            test_file = os.path.join(self.work_dir, "test_generated.py")
            # If module is inside a package, we need to be careful with imports
            # But coverage calculator assumes flat structure for now.
            # For GitHub repos, we rely on PYTHONPATH being set correctly by caller.
        else:
            code_file = os.path.join(self.work_dir, f"{module_name}.py")
            test_file = os.path.join(self.work_dir, "test_generated.py")
            
            # Write code file
            with open(code_file, "w") as f:
                f.write(code)
        
        # Write test file
        with open(test_file, "w") as f:
            f.write(tests)
        
        try:
            # Run pytest with coverage
            # Use sys.executable to ensure we use the correct Python interpreter
            # This is especially important on Windows where "pytest" might not be in PATH
            # Prepare environment
            env = os.environ.copy()
            cwd = self.work_dir
            
            if existing_file_path:
                # Add the project root (or file parent) to PYTHONPATH
                # Assuming existing_file_path is like /tmp/repo/module/file.py
                # We want /tmp/repo in pythonpath so 'import module.file' works
                # Or if it's flat, just parent.
                
                # Best guess: use the CWD passed by caller or file's directory
                file_dir = os.path.dirname(existing_file_path)
                
                # If we are in a repo, specific logic might be needed, but adding file_dir is a good start
                env["PYTHONPATH"] = file_dir + os.pathsep + env.get("PYTHONPATH", "")
                
                # Update cwd to be where the test is (work_dir) or where the code is?
                # Keeping execution in work_dir is safer for cleanup
            
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
                    "-v"
                ],
                capture_output=True,
                text=True,
                cwd=cwd,
                env=env,
                timeout=30
            )
            
            output = result.stdout + "\n" + result.stderr
            success = result.returncode == 0
            
            # Parse coverage report
            coverage_data = self._parse_coverage_json()
            
            if coverage_data:
                return CoverageResult(
                    success=success,
                    total_coverage=coverage_data["total_coverage"],
                    branch_coverage=coverage_data["branch_coverage"],
                    uncovered_branches=coverage_data["uncovered_branches"],
                    tests_run=coverage_data["tests_run"],
                    tests_passed=coverage_data["tests_passed"],
                    output=output
                )
            else:
                # Fallback if JSON parsing fails
                return self._parse_coverage_from_text(output, success)
                
        except subprocess.TimeoutExpired:
            return CoverageResult(
                success=False,
                total_coverage=0.0,
                branch_coverage=0.0,
                uncovered_branches=[],
                tests_run=0,
                tests_passed=0,
                output="",
                error="Test execution timeout"
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
                error=str(e)
            )
        finally:
            # Cleanup
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
            with open(coverage_file, "r") as f:
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
                    uncovered_branches.append({
                        "file": filename,
                        "line": branch
                    })
            
            # Count tests (simplified - would need pytest-json-report for accurate count)
            tests_run = 0
            tests_passed = 0
            
            return {
                "total_coverage": total_coverage,
                "branch_coverage": branch_coverage,
                "uncovered_branches": uncovered_branches,
                "tests_run": tests_run,
                "tests_passed": tests_passed
            }
            
        except Exception as e:
            print(f"[CoverageCalculator] Error parsing coverage JSON: {e}")
            return None
        finally:
            # Cleanup coverage files
            if os.path.exists(coverage_file):
                os.remove(coverage_file)
            coverage_html_dir = os.path.join(self.work_dir, "htmlcov")
            if os.path.exists(coverage_html_dir):
                import shutil
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
                            tests_passed = int(parts[i-1])
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
            output=output
        )


if __name__ == "__main__":
    # Test
    calc = CoverageCalculator()
    
    code = """
def is_positive(n):
    if n > 0:
        return True
    return False
"""
    
    tests = """
import pytest

def test_positive():
    from code_to_test import is_positive
    assert is_positive(5) == True

def test_negative():
    from code_to_test import is_positive
    assert is_positive(-5) == False
"""
    
    result = calc.run_with_coverage(code, tests)
    print(f"Branch Coverage: {result.branch_coverage}%")
    print(f"Tests: {result.tests_passed}/{result.tests_run} passed")
