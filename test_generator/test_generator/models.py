"""
Pydantic models for type-safe data structures.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

BranchMapDict = Dict[str, Any]  # Branch map dictionary structure


class BranchInfo(BaseModel):
    """Information about a code branch."""
    line: int = Field(..., description="Line number where branch occurs")
    type: str = Field(..., description="Branch type: 'if' or 'else'")
    condition: Optional[str] = Field(None, description="Branch condition expression")


class FunctionInfo(BaseModel):
    """Information about a function."""
    name: str = Field(..., description="Function name")
    args: List[dict] = Field(default_factory=list, description="Function arguments")
    return_type: str = Field(default="Any", description="Return type annotation")
    branches: List[BranchInfo] = Field(default_factory=list)
    cyclomatic_complexity: int = Field(default=1, ge=1)
    total_branches: int = Field(default=0, ge=0)
    lineno: int = Field(default=0, ge=0, description="Starting line number")


class BranchMap(BaseModel):
    """Analysis result with branch information."""
    functions: List[FunctionInfo] = Field(..., description="List of analyzed functions")
    total_branches_in_file: int = Field(..., ge=0)


class CoverageResult(BaseModel):
    """Result of coverage analysis."""
    success: bool = Field(..., description="Whether tests executed successfully")
    total_coverage: float = Field(..., ge=0.0, le=100.0, description="Statement coverage %")
    branch_coverage: float = Field(..., ge=0.0, le=100.0, description="Branch coverage %")
    uncovered_branches: List[dict] = Field(default_factory=list)
    tests_run: int = Field(default=0, ge=0)
    tests_passed: int = Field(default=0, ge=0)
    output: str = Field(default="")
    error: Optional[str] = None


class AgentState(BaseModel):
    """State object for LangGraph workflow."""
    code: str = Field(..., description="Source code to test")
    module_name: str = Field(..., description="Module name")
    target_coverage: float = Field(default=80.0, ge=0.0, le=100.0)
    
    # Intermediate results
    branch_map: Optional[BranchMap] = None
    tests: str = Field(default="")
    coverage_result: Optional[CoverageResult] = None
    
    # Iteration tracking
    iteration: int = Field(default=0, ge=0)
    max_iterations: int = Field(default=5, ge=1)
    coverage_history: List[float] = Field(default_factory=list, description="Track coverage % per iteration for stagnation detection")
    
    # Final results
    success: bool = Field(default=False)
    final_test_count: int = Field(default=0, ge=0)
    error: Optional[str] = None  # Track errors during execution
