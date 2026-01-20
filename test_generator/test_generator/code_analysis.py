"""
Code analysis module for detecting branches and extracting function signatures.
Uses Python's ast module for static analysis.
"""
import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class BranchInfo:
    """Information about a code branch."""
    line: int
    type: str  # 'if', 'elif', 'else', 'for', 'while', 'try', 'except', etc.
    condition: Optional[str] = None


@dataclass
class FunctionInfo:
    """Information about a function."""
    name: str
    args: List[Dict[str, str]]
    return_type: str
    branches: List[BranchInfo] = field(default_factory=list)
    cyclomatic_complexity: int = 1
    total_branches: int = 0
    lineno: int = 0


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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = CodeAnalyzer._analyze_function(node)
                functions.append(func_info)
                total_branches += func_info.total_branches
        
        return {
            "functions": [CodeAnalyzer._function_to_dict(f) for f in functions],
            "total_branches_in_file": total_branches
        }
    
    @staticmethod
    def _analyze_function(node: ast.FunctionDef) -> FunctionInfo:
        """Analyze a single function node."""
        # Extract function name
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
        # Complexity = 1 + number of decision points
        complexity = 1 + len([b for b in branches if b.type in ['if', 'elif', 'for', 'while', 'try']])
        
        # Total branches includes if/elif/else, each loop iteration path, try/except paths
        total_branches = len(branches) if branches else 0
        
        return FunctionInfo(
            name=name,
            args=args,
            return_type=return_type,
            branches=branches,
            cyclomatic_complexity=complexity,
            total_branches=total_branches,
            lineno=node.lineno
        )
    
    @staticmethod
    def _detect_branches(node: ast.AST) -> List[BranchInfo]:
        """Detect all branch points in a function."""
        branches = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # If statement
                condition = ast.unparse(child.test) if hasattr(ast, 'unparse') else "condition"
                branches.append(BranchInfo(line=child.lineno, type="if", condition=condition))
                
                # Check for elif/else
                if child.orelse:
                    if isinstance(child.orelse[0], ast.If):
                        # This is elif
                        elif_cond = ast.unparse(child.orelse[0].test) if hasattr(ast, 'unparse') else "condition"
                        branches.append(BranchInfo(
                            line=child.orelse[0].lineno,
                            type="elif",
                            condition=elif_cond
                        ))
                    else:
                        # This is else
                        branches.append(BranchInfo(
                            line=child.orelse[0].lineno if child.orelse else child.lineno,
                            type="else",
                            condition=None
                        ))
            
            elif isinstance(child, (ast.For, ast.AsyncFor)):
                target = ast.unparse(child.target) if hasattr(ast, 'unparse') else "item"
                iter_val = ast.unparse(child.iter) if hasattr(ast, 'unparse') else "iterable"
                branches.append(BranchInfo(
                    line=child.lineno,
                    type="for",
                    condition=f"{target} in {iter_val}"
                ))
            
            elif isinstance(child, ast.While):
                condition = ast.unparse(child.test) if hasattr(ast, 'unparse') else "condition"
                branches.append(BranchInfo(line=child.lineno, type="while", condition=condition))
            
            elif isinstance(child, ast.Try):
                branches.append(BranchInfo(line=child.lineno, type="try", condition=None))
                for handler in child.handlers:
                    exc_type = ast.unparse(handler.type) if handler.type and hasattr(ast, 'unparse') else "Exception"
                    branches.append(BranchInfo(
                        line=handler.lineno,
                        type="except",
                        condition=exc_type
                    ))
            
            elif isinstance(child, ast.Match):  # Python 3.10+
                branches.append(BranchInfo(line=child.lineno, type="match", condition=None))
                for case in child.cases:
                    branches.append(BranchInfo(line=case.lineno, type="case", condition="pattern"))
        
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
        if hasattr(ast, 'unparse'):
            return ast.unparse(node)
        return "Any"
    
    @staticmethod
    def _function_to_dict(func: FunctionInfo) -> Dict[str, Any]:
        """Convert FunctionInfo to dictionary."""
        return {
            "name": func.name,
            "args": func.args,
            "return_type": func.return_type,
            "branches": [
                {
                    "line": b.line,
                    "type": b.type,
                    "condition": b.condition
                } for b in func.branches
            ],
            "cyclomatic_complexity": func.cyclomatic_complexity,
            "total_branches": func.total_branches,
            "lineno": func.lineno
        }


if __name__ == "__main__":
    # Test the analyzer
    sample_code = """
def calculate_discount(price: float, customer_type: str) -> float:
    discount = 0.0
    if price > 100:
        discount = 0.05
    
    if customer_type == 'vip':
        discount += 0.20
    elif customer_type == 'member':
        discount += 0.10
    else:
        discount += 0.0
    
    return price * (1 - discount)
"""
    
    result = CodeAnalyzer.analyze_file(sample_code)
    import json
    print(json.dumps(result, indent=2))
