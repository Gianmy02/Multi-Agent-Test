"""
Multi-Agent Test Generator - SIMPLE DEMO (Strict Mode Compliant)
Demonstrates:
1. Strict Grammar Validation (PASS)
2. Mock LLM Test Generation
3. Coverage Calculation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from test_generator.orchestrator import Orchestrator

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
    
    # Initialize Orchestrator with Mock LLM
    orchestrator = Orchestrator(use_mock=True)
    
    try:
        print("\n[1] Starting Analysis & Generation...")
        result = orchestrator.generate_tests(
            code=sample_code,
            module_name="code_to_test",
            target_coverage=80.0
        )
        
        print("\n" + "=" * 70)
        print("SIMULATION RESULT: SUCCESS")
        print("=" * 70)
        print(f"Tests Generated: {result.get('tests_count', 0)}")
        print(f"Final Branch Coverage:  {result.get('branch_coverage', 0):.1f}%")
        print(f"Final Statement Cov.:   {result.get('total_coverage', 0):.1f}%")
        print(f"Quality Score:   {result.get('quality_score', 0)}/10")
        
        print("\nGENERATED TESTS PREVIEW:")
        print("-" * 20)
        print(result.get("tests", "")[:300] + "...\n(truncated)")
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
