"""
Multi-Agent Test Generator - CALCULATOR DEMO
Demonstrates:
1. Complete language feature coverage
2. Multiple functions (5)
3. Menu-driven logic (via operation codes)
4. Error handling (division by zero)
5. Complex if/else branching
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from test_generator.orchestrator import Orchestrator

def main():
    print("=" * 70)
    print("DEMO 3: CALCULATOR")
    print("=" * 70)
    
    # Read calculator code from file
    calculator_file = os.path.join(os.path.dirname(__file__), 'calculator.py')
    with open(calculator_file, 'r', encoding='utf-8') as f:
        sample_code = f.read()
    
    # Extract only function definitions (remove docstring header)
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
    print(sample_code[:400] + "...\n")
    print("-" * 70)
    
    orchestrator = Orchestrator(use_mock=True)
    
    try:
        print("\n[1] Starting Analysis & Generation...")
        result = orchestrator.generate_tests(
            code=sample_code,
            module_name="calculator",
            target_coverage=80.0
        )
        
        print("\n" + "=" * 70)
        print("SIMULATION RESULT: SUCCESS")
        print("=" * 70)
        print(f"Functions Analyzed: 5 (add, subtract, multiply, divide, calculator)")
        print(f"Tests Generated: {result.get('tests_count', 0)}")
        print(f"Final Branch Coverage:  {result.get('branch_coverage', 0):.1f}%")
        print(f"Final Statement Cov.:   {result.get('total_coverage', 0):.1f}%")
        print(f"Quality Score:   {result.get('quality_score', 0)}/10")
        
        print("\nLANGUAGE FEATURES DEMONSTRATED:")
        print("  + Multiple function definitions (5)")
        print("  + Arithmetic operations (+, -, *, /)")
        print("  + Nested if/else statements (menu logic)")
        print("  + Error handling (division by zero)")
        print("  + Return statements")
        print("  + Comparisons (==, !=)")
        
        # Save output
        output_path = os.path.join(os.path.dirname(__file__), '..', 'output', 'test_calculator.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(result.get("tests", ""))
        print(f"\nFull tests saved to: output/test_calculator.py")
        
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
