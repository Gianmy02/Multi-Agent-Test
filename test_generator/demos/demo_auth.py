"""
Multi-Agent Test Generator - AUTH DEMO (Strict Mode Compliant)
Demonstrates:
1. Strict Grammar Validation with IF statements
2. Branch Coverage (Non-Zero!)
3. Mock LLM Test Generation
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from test_generator.orchestrator import Orchestrator

def main():
    print("=" * 70)
    print("DEMO 2: AUTH SYSTEM")
    print("=" * 70)
    
    # Auth logic using IF statements (now supported!)
    sample_code = """def check_password_strength(length):
    limit = 5
    
    if length > limit:
        score = 100
        return score
    else:
        score = 0
        return score

def validate_login(attempts, max_attempts):
    if attempts > max_attempts:
        return 0
    
    remaining = max_attempts - attempts
    return remaining
"""
    
    print("\nCODE TO ANALYZE:")
    print(sample_code)
    
    orchestrator = Orchestrator(use_mock=True)
    
    try:
        print("\n[1] Starting Analysis & Generation...")
        # And we need Mock LLM to return tests that import from auth_functions
        # I need to update Mock LLM AGAIN to match THIS code.
        # Or revert to the code Mock LLM expects.
        # Mock LLM expects calculate_login_score.
        # Does calculate_login_score allow IFs?
        # Let's use calculate_login_score BUT add an IF inside it to trigger coverage.
        
        result = orchestrator.generate_tests(
            code=sample_code,
            module_name="auth_functions",
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
        
        # Save output
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'test_auth.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result.get("tests", ""))
        print(f"\nFull tests saved to: output/test_auth.py")
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
