"""
Orchestrator for the Multi-Agent Test Generator System.
Coordinates agents to generate tests with >= 80% branch coverage.
"""
from .agents import (
    CodeAnalyzerAgent,
    UnitTestGeneratorAgent,
    CoverageOptimizerAgent,
    TestValidatorAgent
)
from .llm_client import MockLLMClient, RealLLMClient, GitHubModelsClient, OllamaClient
from .coverage_calculator import CoverageCalculator
from . import config


class Orchestrator:
    """
    Main orchestrator that coordinates all agents to generate tests.
    """
    
    def __init__(self, use_mock: bool = None, api_key: str = None, github_token: str = None, use_ollama: bool = False, verbose: bool = False):
        """
        Initialize the Orchestrator.
        
        Args:
            use_mock: If True, use MockLLMClient. If None, use config.USE_MOCK
            api_key: API key for OpenAI
            github_token: GitHub Personal Access Token for GitHub Models
            use_ollama: If True, use local Ollama
            verbose: If True, show detailed debug output
        """
        self.verbose = verbose
        if use_mock is None:
            use_mock = config.USE_MOCK
        
        if use_mock:
            if self.verbose:
                print("[Orchestrator] Using MOCK LLM")
            self.client = MockLLMClient(verbose=self.verbose)
        elif use_ollama:
            if self.verbose:
                print("[Orchestrator] Using OLLAMA (Local LLM)")
            self.client = OllamaClient()
        elif github_token:
            if self.verbose:
                print("[Orchestrator] Using GITHUB MODELS API")
            self.client = GitHubModelsClient(github_token=github_token)
        else:
            if self.verbose:
                print("[Orchestrator] Using REAL LLM (OpenAI)")
            key = api_key or config.OPENAI_API_KEY
            if not key:
                raise ValueError("OpenAI API key not found")
            self.client = RealLLMClient(api_key=key)
        
        # Initialize agents
        self.code_analyzer = CodeAnalyzerAgent(self.client)
        self.test_generator = UnitTestGeneratorAgent(self.client)
        self.coverage_optimizer = CoverageOptimizerAgent(self.client)
        self.test_validator = TestValidatorAgent(self.client)
        
        # Initialize coverage calculator
        self.coverage_calc = CoverageCalculator()
    
    def generate_tests(
        self,
        code: str,
        module_name: str = "code_to_test",
        target_coverage: float = None,
        file_path: str = None
    ) -> dict:
        """
        Main workflow: Generate tests with target branch coverage.
        
        Args:
            code: Python source code to generate tests for
            module_name: Name of the module being tested
            target_coverage: Target branch coverage % (default from config)
            file_path: Optional absolute path to the file being tested (for repo scanning)
            
        Returns:
            Dictionary with final tests, coverage results, and metadata
        """
        if target_coverage is None:
            target_coverage = config.TARGET_BRANCH_COVERAGE
        
        if self.verbose:
            print(f"\n[Orchestrator] Starting test generation for module: {module_name}")
            print(f"[Orchestrator] Target branch coverage: {target_coverage}%\n")
        
        # Step 1: Analyze code and detect branches
        if self.verbose:
            print("=" * 60)
            print("STEP 1: CODE ANALYSIS")
            print("=" * 60)
        branch_map = self.code_analyzer.analyze(code)
        
        if not branch_map.get("functions"):
            print("[Orchestrator] ERROR: No functions found in code")
            return {
                "success": False,
                "error": "No functions found to test",
                "tests": "",
                "coverage": 0.0
            }
        
        total_branches = branch_map.get("total_branches_in_file", 0)
        print(f">> Analyzing: {len(branch_map['functions'])} function(s), {total_branches} branch(es)")
        
        # Step 2: Generate initial test suite
        if self.verbose:
            print("\n" + "=" * 60)
            print("STEP 2: INITIAL TEST GENERATION")
            print("=" * 60)
        tests = self.test_generator.generate_tests(code, branch_map, module_name, verbose=self.verbose)
        
        # Step 3: Measure initial coverage
        if self.verbose:
            print("\n" + "=" * 60)
            print("STEP 3: COVERAGE MEASUREMENT")
            print("=" * 60)
        # Pass existing file path if enabled
        coverage_result = self.coverage_calc.run_with_coverage(code, tests, module_name, existing_file_path=file_path)
        
        if not coverage_result.success and self.verbose:
            print(f">> WARNING: Tests failed to execute")
            print(f"   Error: {coverage_result.error}")
        
        current_coverage = coverage_result.branch_coverage
        initial_test_count = tests.count('def test_')
        print(f">> Generated {initial_test_count} test(s) -> Coverage: {current_coverage:.1f}% (target: {target_coverage}%)")
        
        # Step 4: Iterative coverage optimization
        iteration = 0
        max_iterations = config.MAX_OPTIMIZATION_ITERATIONS
        
        while current_coverage < target_coverage and iteration < max_iterations:
            iteration += 1
            if self.verbose:
                print("\n" + "=" * 60)
                print(f"OPTIMIZATION ITERATION {iteration}/{max_iterations}")
                print("=" * 60)
            else:
                print(">> Optimization iteration {}/{}: gap {:.1f}%".format(iteration, max_iterations, target_coverage - current_coverage))
            
            # Generate additional tests
            additional_tests = self.coverage_optimizer.optimize_coverage(
                code=code,
                current_tests=tests,
                coverage_result={
                    "branch_coverage": current_coverage,
                    "total_coverage": coverage_result.total_coverage,
                    "uncovered_branches": coverage_result.uncovered_branches
                },
                branch_map=branch_map,
                module_name=module_name,
                verbose=self.verbose
            )
            
            # Merge tests
            tests = tests + "\n\n" + additional_tests
            
            # Re-measure coverage
            coverage_result = self.coverage_calc.run_with_coverage(code, tests, module_name, existing_file_path=file_path)
            new_coverage = coverage_result.branch_coverage
            
            improvement = new_coverage - current_coverage
            if self.verbose:
                print(f"   Coverage: {new_coverage:.1f}% (+{improvement:.1f}%)")
            
            # Check for stagnation
            if improvement <= 0.1:
                if self.verbose:
                    print("   Coverage stagnated, stopping optimization")
                break
            
            current_coverage = new_coverage
            
            # Check if target reached
            if current_coverage >= target_coverage:
                break
        
        # Step 5: Validate test quality
        if self.verbose:
            print("\n" + "=" * 60)
            print("STEP 5: TEST QUALITY VALIDATION")
            print("=" * 60)
        validation = self.test_validator.validate(
            tests=tests,
            code=code,
            coverage_result={
                "branch_coverage": current_coverage,
                "total_coverage": coverage_result.total_coverage,
                "tests_run": coverage_result.tests_run
            },
            verbose=self.verbose
        )
        
        # Final results
        success = current_coverage >= target_coverage
        final_test_count = tests.count('def test_')
        quality_score = validation.get('quality_score', 0)
        
        print(f"\n>> {'SUCCESS' if success else 'FAILED'}: {final_test_count} tests, {current_coverage:.1f}% coverage, quality {quality_score}/10")
        
        if self.verbose:
            print("\n" + "=" * 60)
            print("DETAILED RESULTS")
            print("=" * 60)
            print(f"Status: {'SUCCESS' if success else 'FAILED'}")
            print(f"Branch Coverage: {current_coverage:.1f}% (target: {target_coverage}%)")
            print(f"Statement Coverage: {coverage_result.total_coverage:.1f}%")
            print(f"Tests Generated: {final_test_count}")
            print(f"Quality Score: {quality_score}/10")
            print(f"Optimization Iterations: {iteration}")
            print("=" * 60)
        
        return {
            "success": success,
            "tests": tests,
            "branch_coverage": current_coverage,
            "total_coverage": coverage_result.total_coverage,
            "tests_count": tests.count('def test_'),
            "quality_score": validation.get('quality_score', 0),
            "iterations": iteration,
            "branch_map": branch_map,
            "validation": validation,
            "coverage_output": coverage_result.output
        }


def main():
    """Demo run with simple example."""
    # Sample code to test
    sample_code = """
def calculate_discount(price: float, customer_type: str) -> float:
    \"\"\"Calculate discount based on price and customer type.\"\"\"
    discount = 0.0
    
    if price > 100:
        discount += 0.05  # 5% for orders over 100
    
    if customer_type == 'vip':
        discount += 0.20  # 20% for VIP
    elif customer_type == 'member':
        discount += 0.10  # 10% for members
    else:
        discount += 0.0   # No discount for regular
    
    return price * (1 - discount)
"""
    
    # Create orchestrator with Mock LLM
    orchestrator = Orchestrator(use_mock=True)
    
    # Generate tests
    result = orchestrator.generate_tests(
        code=sample_code,
        module_name="code_to_test",
        target_coverage=80.0
    )
    
    # Print results
    if result["success"]:
        print("\n✓ Test generation succeeded!")
        print(f"\nGenerated Tests:\n{result['tests']}")
    else:
        print("\n✗ Test generation failed")
        if "error" in result:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
