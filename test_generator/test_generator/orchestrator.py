"""
LangGraph-based orchestrator for multi-agent test generation.
Replaces sequential workflow with state machine for better control flow.
"""

from typing import Literal
from langgraph.graph import StateGraph, END
from .models import AgentState, BranchMap, CoverageResult
from .agents import CodeAnalyzerAgent, UnitTestGeneratorAgent, CoverageOptimizerAgent
from .llm_client import LangChainLLMClient
from .coverage_calculator import CoverageCalculator
from . import config


class LangGraphOrchestrator:
    """Graph-based orchestrator using LangGraph state machine."""
    
    def __init__(
        self,
        provider: str = None,
        api_key: str = None,
        verbose: bool = False,
    ) -> None:
        """Initialize orchestrator with LangGraph workflow.
        
        Args:
            provider: LLM provider (must be 'google', default)
            api_key: Google API key. Uses GOOGLE_API_KEY env var if None.
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.logger = config.setup_logging(verbose)
        
        # Provider must be google (only supported provider)
        if provider is None:
            provider = "google"
        elif provider != "google":
            raise ValueError(
                f"Only 'google' provider is supported. Got: {provider}"
            )
        
        # Get Google API key from config if not provided
        if api_key is None:
            api_key = config.GOOGLE_API_KEY
        
        if not api_key:
            raise ValueError(
                "Google API key not found. "
                "Set GOOGLE_API_KEY environment variable."
            )
        
        if self.verbose:
            self.logger.info("Using GOOGLE GEMINI provider")
        
        # Initialize LangChain client (Google Gemini only)
        self.client = LangChainLLMClient(
            provider=provider,
            api_key=api_key,
            verbose=verbose
        )
        
        # Initialize agents
        self.code_analyzer = CodeAnalyzerAgent(self.client)
        self.test_generator = UnitTestGeneratorAgent(self.client)
        self.coverage_optimizer = CoverageOptimizerAgent(self.client)
        self.coverage_calc = CoverageCalculator()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph state machine.
        
        Workflow:
        1. analyze: Validate with Lark and extract branches
        2. generate: Create initial test suite
        3. measure: Run tests and calculate coverage
        4. Decision: optimize (if coverage < target) or end
        5. optimize: Generate additional tests for uncovered branches
        6. Loop back to measure
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("measure", self._measure_node)
        workflow.add_node("optimize", self._optimize_node)
        
        # Add edges
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "generate")
        workflow.add_edge("generate", "measure")
        workflow.add_conditional_edges(
            "measure",
            self._should_optimize,
            {
                "optimize": "optimize",
                "end": END,
            }
        )
        workflow.add_edge("optimize", "measure")
        
        return workflow.compile()
    
    def _analyze_node(self, state: AgentState) -> AgentState:
        """Node: Analyze code and detect branches using Lark + AST."""
        if self.verbose:
            self.logger.info("="*60)
            self.logger.info("STEP 1: CODE ANALYSIS")
            self.logger.info("="*60)
        
        try:
            branch_map_dict = self.code_analyzer.analyze(state.code)
            state.branch_map = BranchMap(**branch_map_dict)
            
            if self.verbose:
                total_branches = state.branch_map.total_branches_in_file
                self.logger.info(f"Analyzing: {len(state.branch_map.functions)} function(s), {total_branches} branch(es)")
        
        except SyntaxError as e:
            # Lark grammar validation failed
            error_msg = f"Grammar validation failed: {e}"
            if self.verbose:
                self.logger.error(error_msg)
            state.error = error_msg
            state.success = False
            raise SyntaxError(error_msg) from e
        
        except Exception as e:
            # AST analysis or other unexpected errors
            error_msg = f"Code analysis failed: {e}"
            if self.verbose:
                self.logger.error(error_msg)
            state.error = error_msg
            state.success = False
            raise RuntimeError(error_msg) from e
        
        return state
    
    def _generate_node(self, state: AgentState) -> AgentState:
        """Node: Generate initial test suite."""
        if self.verbose:
            self.logger.info("="*60)
            self.logger.info("STEP 2: INITIAL TEST GENERATION")
            self.logger.info("="*60)
        
        try:
            tests = self.test_generator.generate_tests(
                state.code,
                state.branch_map.model_dump(),
                state.module_name,
                verbose=self.verbose
            )
            state.tests = tests
            
            if self.verbose:
                test_count = tests.count("def test_")
                self.logger.info(f"Generated {test_count} test(s)")
        
        except Exception as e:
            # LLM generation or extraction errors
            error_msg = f"Test generation failed: {e}"
            if self.verbose:
                self.logger.error(error_msg)
            state.error = error_msg
            state.success = False
            raise RuntimeError(error_msg) from e
        
        return state
    
    def _measure_node(self, state: AgentState) -> AgentState:
        """Node: Measure coverage."""
        if self.verbose:
            self.logger.info("="*60)
            self.logger.info("STEP 3: COVERAGE MEASUREMENT")
            self.logger.info("="*60)
        
        try:
            coverage_result = self.coverage_calc.run_with_coverage(
                state.code,
                state.tests,
                state.module_name
            )
            
            # Convert to Pydantic model
            state.coverage_result = CoverageResult(
                success=coverage_result.success,
                total_coverage=coverage_result.total_coverage,
                branch_coverage=coverage_result.branch_coverage,
                uncovered_branches=coverage_result.uncovered_branches,
                tests_run=coverage_result.tests_run,
                tests_passed=coverage_result.tests_passed,
                output=coverage_result.output,
                error=coverage_result.error
            )
            
            # Check if target reached
            if state.coverage_result.branch_coverage >= state.target_coverage:
                state.success = True
            
            test_count = state.tests.count("def test_")
            if self.verbose:
                self.logger.info(f"Generated {test_count} test(s) -> Coverage: {state.coverage_result.branch_coverage:.1f}% (target: {state.target_coverage}%)")
        
        except Exception as e:
            # Coverage execution or parsing errors
            error_msg = f"Coverage measurement failed: {e}"
            if self.verbose:
                self.logger.error(error_msg)
            # Create minimal coverage result with error
            state.coverage_result = CoverageResult(
                success=False,
                total_coverage=0.0,
                branch_coverage=0.0,
                uncovered_branches=[],
                tests_run=0,
                tests_passed=0,
                output="",
                error=error_msg
            )
            state.error = error_msg
            state.success = False
            # Don't raise - allow workflow to end gracefully
        
        return state
    
    def _optimize_node(self, state: AgentState) -> AgentState:
        """Node: Optimize coverage by generating additional tests."""
        state.iteration += 1
        
        if self.verbose:
            self.logger.info("="*60)
            self.logger.info(f"OPTIMIZATION ITERATION {state.iteration}/{state.max_iterations}")
            self.logger.info("="*60)
            gap = state.target_coverage - state.coverage_result.branch_coverage
            self.logger.info(f"Gap: {gap:.1f}%")
        
        try:
            additional_tests = self.coverage_optimizer.optimize_coverage(
                code=state.code,
                current_tests=state.tests,
                coverage_result=state.coverage_result.model_dump(),
                branch_map=state.branch_map.model_dump(),
                module_name=state.module_name,
                verbose=self.verbose,
            )
            
            state.tests = state.tests + "\n\n" + additional_tests
            
            if self.verbose:
                new_tests = additional_tests.count("def test_")
                self.logger.info(f"Generated {new_tests} additional test(s)")
        
        except Exception as e:
            # Optimization failed, but don't crash - just log and continue
            error_msg = f"Optimization iteration {state.iteration} failed: {e}"
            if self.verbose:
                self.logger.warning(error_msg)
            # Set error but don't mark as complete failure - keep existing tests
            if not state.error:
                state.error = error_msg
        
        return state
    
    def _should_optimize(self, state: AgentState) -> Literal["optimize", "end"]:
        """Conditional edge: Determine if optimization is needed."""
        # Check if target reached
        if state.success:
            return "end"
        
        # Check iteration limit
        if state.iteration >= state.max_iterations:
            if self.verbose:
                self.logger.info(f"Max iterations ({state.max_iterations}) reached")
            return "end"
        
        # Stagnation detection: Track coverage history and detect lack of improvement
        if state.coverage_result:
            current_coverage = state.coverage_result.branch_coverage
            state.coverage_history.append(current_coverage)
            
            # Check for stagnation: no improvement in last 3 iterations
            if len(state.coverage_history) >= 3:
                last_3 = state.coverage_history[-3:]
                improvement = max(last_3) - min(last_3)
                
                # If less than 1% improvement over 3 iterations, consider stagnant
                if improvement < 1.0:
                    if self.verbose:
                        self.logger.warning(
                            f"Coverage stagnated at {current_coverage:.1f}% "
                            f"(improvement: {improvement:.2f}% over last 3 iterations). "
                            f"Stopping optimization."
                        )
                    return "end"
        
        return "optimize"
    
    def generate_tests(
        self,
        code: str,
        module_name: str = "code_to_test",
        target_coverage: float = None,
        file_path: str = None,
    ) -> dict:
        """Generate tests using LangGraph workflow.
        
        Args:
            code: Python source code to test
            module_name: Name of the module being tested
            target_coverage: Target branch coverage % (default from config)
            file_path: Optional absolute path to file (for repo scanning)
            
        Returns:
            Dictionary with test results and metadata
        """
        if target_coverage is None:
            target_coverage = config.TARGET_BRANCH_COVERAGE
        
        if self.verbose:
            self.logger.info(f"Starting test generation for module: {module_name}")
            self.logger.info(f"Target branch coverage: {target_coverage}%")
        
        # Create initial state
        initial_state = AgentState(
            code=code,
            module_name=module_name,
            target_coverage=target_coverage,
            max_iterations=config.MAX_OPTIMIZATION_ITERATIONS,
        )
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Calculate final results
        test_count = final_state["tests"].count("def test_")
        success = final_state["success"]
        
        if self.verbose:
            self.logger.info("=" * 60)
            self.logger.info("DETAILED RESULTS")
            self.logger.info("=" * 60)
            self.logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
            self.logger.info(f"Branch Coverage: {final_state['coverage_result'].branch_coverage:.1f}% "
                             f"(target: {target_coverage}%)")
            self.logger.info(f"Statement Coverage: {final_state['coverage_result'].total_coverage:.1f}%")
            self.logger.info(f"Tests Generated: {test_count}")
            self.logger.info(f"Optimization Iterations: {final_state['iteration']}")
            self.logger.info("=" * 60)
        
        # Return results
        return {
            "success": success,
            "tests": final_state["tests"],
            "branch_coverage": final_state["coverage_result"].branch_coverage,
            "total_coverage": final_state["coverage_result"].total_coverage,
            "tests_count": test_count,
            "iterations": final_state["iteration"],
            "branch_map": final_state["branch_map"].model_dump(),
            "coverage_output": final_state["coverage_result"].output,
        }
