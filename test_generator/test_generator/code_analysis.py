"""
Code analysis module for detecting branches and extracting function signatures.
Uses Python's ast module for static analysis.
"""

import ast
from typing import List, Dict, Any
from .models import BranchInfo, FunctionInfo


class CodeAnalyzer:
    """
    Analyzes Python code to extract functions and detect branch points.
    """

    @staticmethod
    def analyze_file(code: str) -> Dict[str, Any]:
        """
        Analyze Python code and extract function information with branch detection.

        Args:
            code: Python source code as string

        Returns:
            Dictionary with functions list and total branch count
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"error": str(e), "functions": [], "total_branches_in_file": 0}

        functions = []
        total_branches = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = CodeAnalyzer._analyze_function(node)
                functions.append(func_info)
                total_branches += func_info.total_branches

        return {
            "functions": [CodeAnalyzer._function_to_dict(f) for f in functions],
            "total_branches_in_file": total_branches,
        }

    @staticmethod
    def _analyze_function(node: ast.FunctionDef) -> FunctionInfo:
        """Analyze a single function node."""
        name = node.name

        # Extract arguments
        args = []
        for arg in node.args.args:
            arg_type = CodeAnalyzer._get_annotation(arg.annotation)
            args.append({"name": arg.arg, "type": arg_type})

        # Extract return type
        return_type = CodeAnalyzer._get_annotation(node.returns)

        # Detect branches
        branches = CodeAnalyzer._detect_branches(node)

        # Calculate cyclomatic complexity (simplified)
        # Complexity = 1 + number of decision points (only if supported by grammar)
        complexity = 1 + len([b for b in branches if b.type == "if"])

        # Total branches includes if/else (only constructs in grammar)
        total_branches = len(branches) if branches else 0

        return FunctionInfo(
            name=name,
            args=args,
            return_type=return_type,
            branches=branches,
            cyclomatic_complexity=complexity,
            total_branches=total_branches,
            lineno=node.lineno,
        )

    @staticmethod
    def _detect_branches(node: ast.AST) -> List[BranchInfo]:
        """Detect all branch points in a function (only if/else per grammar)."""
        branches = []

        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # If statement
                condition = ast.unparse(child.test) if hasattr(ast, "unparse") else "condition"
                branches.append(BranchInfo(line=child.lineno, type="if", condition=condition))

                # Check for else (grammar only supports if/else, not elif)
                if child.orelse and not isinstance(child.orelse[0], ast.If):
                    # This is else
                    branches.append(
                        BranchInfo(
                            line=child.orelse[0].lineno if child.orelse else child.lineno, type="else", condition=None
                        )
                    )

        return branches

    @staticmethod
    def _get_annotation(node) -> str:
        """Extract type annotation from node."""
        if node is None:
            return "Any"
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        if hasattr(ast, "unparse"):
            return ast.unparse(node)
        return "Any"

    @staticmethod
    def _function_to_dict(func: FunctionInfo) -> Dict[str, Any]:
        """Convert FunctionInfo to dictionary."""
        return func.model_dump()
