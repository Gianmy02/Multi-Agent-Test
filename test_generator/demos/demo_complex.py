"""
Multi-Agent Test Generator - COMPLEX SYSTEM DEMO
Demonstrates MAXIMUM COMPLEXITY to activate Coverage Optimizer:
1. 8 functions with deep nesting
2. 40+ distinct branches (massive branch coverage challenge)
3. All comparison operators (==, !=, <, >, <=, >=)
4. All arithmetic operations (+, -, *, /)
5. Complex expressions with parentheses
6. Multiple return paths per function
7. Edge cases and boundary conditions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from test_generator.orchestrator import LangGraphOrchestrator
from test_generator import config

def main():
    print("=" * 70)
    print("DEMO 4: COMPLEX BANKING SYSTEM - MAXIMUM COVERAGE CHALLENGE")
    print("=" * 70)
    
    # Read extreme system code from file
    extreme_file = os.path.join(os.path.dirname(__file__), 'extreme_system.py')
    with open(extreme_file, 'r', encoding='utf-8') as f:
        sample_code = f.read()
    
    # Extract only function definitions
    lines = sample_code.split('\n')
    code_lines = []
    in_code = False
    for line in lines:
        if line.startswith('def '):
            in_code = True
        if in_code:
            code_lines.append(line)
    
    sample_code = '\n'.join(code_lines)
    
    print("\nCODE TO ANALYZE:")
    print("-" * 70)
    print(f"Total lines: {len(sample_code.split(chr(10)))}")
    print(f"Functions: 3 (ultra-complex banking)")
    print(f"Estimated branches: 80+")
    print("-" * 70)
    print(sample_code[:500] + "...\n[TRUNCATED - Full code in extreme_system.py]")
    print("-" * 70)

    
    # Check for Google API key
    if not config.GOOGLE_API_KEY:
        print("\n" + "=" * 70)
        print("WARNING: Google API key not found!")
        print("=" * 70)
        print("Set GOOGLE_API_KEY environment variable")
        print("=" * 70)
        return
    
    # Initialize Orchestrator with verbose mode
    orchestrator = LangGraphOrchestrator(verbose=True)
    
    try:
        print("\n[1] Starting Complex Analysis & Generation...")
        print("    This will definitely trigger the Coverage Optimizer!")
        
        result = orchestrator.generate_tests(
            code=sample_code,
            module_name="extreme_banking_system",
            # target_coverage uses default from config.py (80.0)
        )
        
        print("\n" + "=" * 70)
        print("SIMULATION RESULT: SUCCESS")
        print("=" * 70)
        print(f"Functions Analyzed: 3 (Ultra-Complex)")
        print("  1. ultra_complex_loan_scoring (6+ levels deep, 40+ branches)")
        print("  2. multi_tier_interest_calculator (5 levels deep, 25+ branches)")
        print("  3. advanced_fraud_detection (4 levels deep, 20+ branches)")
        
        print(f"\nTests Generated: {result.get('tests_count', 0)}")
        print(f"Final Branch Coverage:  {result.get('branch_coverage', 0):.1f}%")
        print(f"Final Statement Cov.:   {result.get('total_coverage', 0):.1f}%")
        
        # Save output
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'test_extreme_banking.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result.get("tests", ""))
        print(f"\nFull tests saved to: output/test_extreme_banking.py")
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
