"""
LLM Client implementations for the test generator system.
Supports Mock, OpenAI, GitHub Models, and Ollama.
"""
from abc import ABC, abstractmethod
from typing import Optional
import json


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, model: str = "gpt-4o") -> str:
        pass


class MockLLMClient(LLMClient):
    """
    Returns hardcoded responses for testing the control flow.
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a hardcoded response based on prompt content."""
        prompt_lower = prompt.lower() if prompt else ""
        system_lower = system_prompt.lower() if system_prompt else ""
        
        if self.verbose:
            print(f"[MockLLM] Generating for prompt: {prompt[:100]}...")
        
        # Test Generator response
        if "generate" in prompt_lower and ("test" in prompt_lower or "pytest" in prompt_lower):
            

            # Calculator demo (check for calculator or calculator_menu)
            if "calculator" in prompt_lower or ("add" in prompt_lower and "subtract" in prompt_lower and "multiply" in prompt_lower):
                return """import pytest

def test_add():
    \"\"\"Test addition operation\"\"\"
    from calculator import add
    assert add(5, 3) == 8

def test_subtract():
    \"\"\"Test subtraction operation\"\"\"
    from calculator import subtract
    assert subtract(10, 4) == 6

def test_multiply():
    \"\"\"Test multiplication operation\"\"\"
    from calculator import multiply
    assert multiply(6, 7) == 42

def test_divide_normal():
    \"\"\"Test normal division\"\"\"
    from calculator import divide
    assert divide(10, 2) == 5

def test_divide_by_zero():
    \"\"\"Test division by zero returns error code\"\"\"
    from calculator import divide
    assert divide(10, 0) == -999999

def test_calculator_menu_add():
    \"\"\"Test calculator menu: addition (code=1)\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(1, 5, 3) == 8

def test_calculator_menu_subtract():
    \"\"\"Test calculator menu: subtraction (code=2)\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(2, 10, 4) == 6

def test_calculator_menu_multiply():
    \"\"\"Test calculator menu: multiplication (code=3)\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(3, 6, 7) == 42

def test_calculator_menu_divide():
    \"\"\"Test calculator menu: division (code=4)\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(4, 10, 2) == 5

def test_calculator_menu_invalid():
    \"\"\"Test calculator menu: invalid operation code\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(99, 5, 3) == 0

def test_calculator_menu_div_zero():
    \"\"\"Test division by zero via menu\"\"\"
    from calculator import calculator_menu
    assert calculator_menu(4, 10, 0) == -999999
"""
            
            # Auth Functions demo (check_password_strength)
            if "check_password_strength" in prompt_lower:
                return """import pytest

def test_password_strong():
    \"\"\"Test strong password logic (length > 5)\"\"\"
    from auth_functions import check_password_strength
    assert check_password_strength(8) == 100

def test_password_weak():
    \"\"\"Test weak password logic (length <= 5)\"\"\"
    from auth_functions import check_password_strength
    assert check_password_strength(3) == 0

def test_validate_login_ok():
    \"\"\"Test login valid (attempts <= max)\"\"\"
    from auth_functions import validate_login
    assert validate_login(1, 3) == 2

def test_validate_login_fail():
    \"\"\"Test login fail (attempts > max)\"\"\"
    from auth_functions import validate_login
    assert validate_login(5, 3) == 0
"""

            # Simple ADD demo
            if "add" in prompt_lower:
                return """import pytest

def test_add_positive():
    \"\"\"Test positive path (x >= 0)\"\"\"
    from code_to_test import add
    assert add(2, 3) == 5

def test_add_branch_negative():
    \"\"\"Test negative path (x < 0) - COVERS BRANCH\"\"\"
    from code_to_test import add
    assert add(-1, 5) == 0

def test_add_zero():
    \"\"\"Test boundary (x = 0)\"\"\"
    from code_to_test import add
    assert add(0, 5) == 5
"""
        
        # Coverage Optimizer response
        if "uncovered" in prompt_lower or "optimizer" in system_lower:
            # Calculator optimizer
            if "calculator" in prompt_lower:
                return """import pytest

def test_divide_negative():
    \"\"\"Test division with negative numbers\"\"\"
    from calculator import divide
    assert divide(-10, 2) == -5
"""
            # If Auth demo optimizer
            if "auth" in prompt_lower:
                 return """import pytest
from auth_functions import check_password_strength

def test_password_boundary():
    \"\"\"Edge case: password length exactly on limit (5).\"\"\"
    assert check_password_strength(5) == 0
"""
            # Default simple demo optimizer
            return """import pytest

def test_add_large_numbers():
    \"\"\"Test addition with large integers.\"\"\"
    from code_to_test import add
    assert add(1000000, 2000000) == 3000000
"""
        
        # Code Analyzer response
        if "analyzer" in system_lower:

            # Calculator analyzer
            if "calculator" in prompt_lower:
                return json.dumps({
                    "functions": [
                        {"name": "add", "args": [{"name": "a", "type": "Any"}, {"name": "b", "type": "Any"}], "return_type": "Any", "branches": [], "cyclomatic_complexity": 1, "total_branches": 0},
                        {"name": "subtract", "args": [{"name": "a", "type": "Any"}, {"name": "b", "type": "Any"}], "return_type": "Any", "branches": [], "cyclomatic_complexity": 1, "total_branches": 0},
                        {"name": "multiply", "args": [{"name": "a", "type": "Any"}, {"name": "b", "type": "Any"}], "return_type": "Any", "branches": [], "cyclomatic_complexity": 1, "total_branches": 0},
                        {"name": "divide", "args": [{"name": "a", "type": "Any"}, {"name": "b", "type": "Any"}], "return_type": "Any", "branches": [{"line": 35, "type": "if", "condition": "b == 0"}], "cyclomatic_complexity": 2, "total_branches": 1},
                        {"name": "calculator_menu", "args": [{"name": "operation_code", "type": "Any"}, {"name": "num1", "type": "Any"}, {"name": "num2", "type": "Any"}], "return_type": "Any", "branches": [{"line": 54, "type": "if"}, {"line": 57, "type": "if"}, {"line": 60, "type": "if"}, {"line": 63, "type": "if"}], "cyclomatic_complexity": 5, "total_branches": 4}
                    ],
                    "total_branches_in_file": 5
                })
            
            # Check for Auth
            if "check_password_strength" in prompt_lower:
                return json.dumps({
                    "functions": [
                        {
                            "name": "check_password_strength",
                            "args": [{"name": "length", "type": "Any"}],
                            "return_type": "int",
                            "branches": [
                                {"line": 24, "type": "if", "condition": "length > limit"},
                                {"line": 27, "type": "else", "condition": None}
                            ],
                            "cyclomatic_complexity": 2,
                            "total_branches": 2
                        },
                         {
                            "name": "validate_login",
                            "args": [{"name": "attempts", "type": "Any"}, {"name": "max_attempts", "type": "Any"}],
                            "return_type": "int",
                            "branches": [
                                {"line": 32, "type": "if", "condition": "attempts > max_attempts"}
                            ],
                            "cyclomatic_complexity": 2,
                            "total_branches": 1
                        }
                    ],
                    "total_branches_in_file": 3
                })
            
            # Simple ADD demo analyzer
            return json.dumps({
                "functions": [
                    {
                        "name": "add",
                        "args": [
                            {"name": "x", "type": "Any"},
                            {"name": "y", "type": "Any"}
                        ],
                        "return_type": "Any",
                        "branches": [
                            {"line": 23, "type": "if", "condition": "x < 0"}
                        ],
                        "cyclomatic_complexity": 2,
                        "total_branches": 1
                    }
                ],
                "total_branches_in_file": 1
            })
        
        if "quality" in prompt_lower or "validator" in system_lower:
            return json.dumps({
                "quality_score": 9.0,
                "issues": [],
                "suggestions": [
                    "Tests cover all known branches.", 
                    "Good usage of assertions."
                ],
                "passed_quality_gate": True
            })
        
        # Default
        return "# Mock response"


class RealLLMClient(LLMClient):
    """
    Real LLM client using OpenAI's API.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    def generate(self, prompt: str, system_prompt: str = None, model: str = "gpt-4o") -> str:
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=4000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"[RealLLMClient] Error calling OpenAI API: {e}")
            raise


class GitHubModelsClient(LLMClient):
    """
    LLM client using GitHub Models API.
    """
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.base_url = "https://models.github.ai"
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package not installed. Run: pip install requests")

    def generate(self, prompt: str, system_prompt: str = None, model: str = "gpt-4o") -> str:
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 4000
            }
            
            response = self.requests.post(
                f"{self.base_url}/inference/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"GitHub Models API error {response.status_code}: {response.text}"
                print(f"[GitHubModelsClient] {error_msg}")
                raise Exception(error_msg)
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            print(f"[GitHubModelsClient] Error calling GitHub Models API: {e}")
            raise


class OllamaClient(LLMClient):
    """
    LLM client using Ollama (local models).
    """
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests package not installed. Run: pip install requests")

    def generate(self, prompt: str, system_prompt: str = None, model: str = None) -> str:
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model or self.model,
                "messages": messages,
                "stream": False
            }
            
            response = self.requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error {response.status_code}: {response.text}"
                print(f"[OllamaClient] {error_msg}")
                raise Exception(error_msg)
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except Exception as e:
            print(f"[OllamaClient] Error calling Ollama API: {e}")
            raise
