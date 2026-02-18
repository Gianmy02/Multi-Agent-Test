"""
Multi-Agent Test Generator - SIMPLE DEMO (Strict Mode Compliant)
Demonstrates:
1. Strict Grammar Validation (PASS)
2. LLM Test Generation (LangChain)
3. Coverage Calculation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from test_generator.orchestrator import LangGraphOrchestrator
from test_generator import config

def main():
    print("=" * 70)
    print("DEMO 1: SIMPLE FUNCTION (Strict Mode Compliant)")
    print("=" * 70)
    
    # Simple addition function
    # Complies with python_subset.lark (def, return, assignment, math)
    sample_code = """def add(x, y):
    # Add a check to demonstrate Branch Coverage
    if x < 0:
        return 0
    
    result = x + y
    return result
"""
    
    print("\nCODE TO ANALYZE:")
    print(sample_code)
    
    # Check for Google API key
    if not config.GOOGLE_API_KEY:
        print("\n" + "=" * 70)
        print("WARNING: Google API key not found!")
        print("=" * 70)
        print("Set GOOGLE_API_KEY environment variable")
        print("Example (Windows): $env:GOOGLE_API_KEY='your-key-here'")
        print("Example (Linux/Mac): export GOOGLE_API_KEY='your-key-here'")
        print("=" * 70)
        return
    
    # Initialize Orchestrator with LangChain LLM
    orchestrator = LangGraphOrchestrator(verbose=True)
    
    try:
        print("\n[1] Starting Analysis & Generation...")
        result = orchestrator.generate_tests(
            code=sample_code,
            module_name="simple_math",
            # target_coverage uses default from config.py (80.0)
        )
        
        print("\n" + "=" * 70)
        print("SIMULATION RESULT: SUCCESS")
        print("=" * 70)
        print(f"Tests Generated: {result.get('tests_count', 0)}")
        print(f"Final Branch Coverage:  {result.get('branch_coverage', 0):.1f}%")
        print(f"Final Statement Cov.:   {result.get('total_coverage', 0):.1f}%")
        
        print("\nGENERATED TESTS PREVIEW:")
        print("-" * 20)
        print(result.get("tests", "")[:300] + "...\n(truncated)")
        
        # Save output
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'test_simple.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.get("tests", ""))
        print(f"\nFull tests saved to: output/test_simple.py")
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
