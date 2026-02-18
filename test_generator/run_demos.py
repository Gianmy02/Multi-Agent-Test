#!/usr/bin/env python
"""
Multi-Agent Test Generator - Demo Launcher
Launcher unico per tutte le demo del progetto
"""
import sys
import os

def main():
    running = True
    executed_demos = set()  # Track which demos have been executed
    
    while running:
        print("\n" + "=" * 70)
        print("MULTI-AGENT TEST GENERATOR - DEMO LAUNCHER")
        print("=" * 70)
        print("\nDemo disponibili:")
        print("  1. Simple Demo    - Funzione base con branch (add)")
        print("  2. Auth Demo      - Logica condizionale (password/login)")
        print("  3. Calculator     - Menu aritmetico completo (5 funzioni)")
        print("  4. Complex Demo   - Validazione complessa (14+ branch)")
        print("  0. Esci")
        
        # Show executed demos status
        if executed_demos:
            print("\nDemo già eseguite:")
            demo_names = {1: "Simple", 2: "Auth", 3: "Calculator", 4: "Complex"}
            for num in sorted(executed_demos):
                print(f"  ✓ [{num}] {demo_names[num]} - Risultati stampati dalla demo")
        
        print("-" * 70)
        
        try:
            choice = input("\nScegli demo (1-4, 0 per uscire): ").strip()
            
            if choice == "0":
                print("\nArrivederci!")
                running = False
            elif choice in ["1", "2", "3", "4"]:
                demo_num = int(choice)
                
                # Check if already executed
                if demo_num in executed_demos:
                    demo_name = {1: "Simple", 2: "Auth", 3: "Calculator", 4: "Complex"}[demo_num]
                    print(f"\n[ℹ] Demo {demo_num} ({demo_name}) già eseguita!")
                    print(f"    I test generati sono salvati in: output/test_*.py")
                    print("\n[Premi Invio per continuare...]")
                    input()
                    continue
                
                # Execute demo
                demo_names = {1: "Simple", 2: "Auth", 3: "Calculator", 4: "Complex"}
                print(f"\n>> Avvio DEMO {demo_num}: {demo_names[demo_num]}...")
                print("=" * 70)
                
                if choice == "1":
                    import demos.demo_simple as demo
                    demo.main()
                elif choice == "2":
                    import demos.demo_auth as demo
                    demo.main()
                elif choice == "3":
                    import demos.demo_calculator as demo
                    demo.main()
                elif choice == "4":
                    import demos.demo_complex as demo
                    demo.main()
                
                # Mark as executed (demo already printed all results above)
                executed_demos.add(demo_num)
                
                print("\n" + "=" * 70)
                print("[Demo completata. I risultati sono stampati sopra.]")
                print("Test salvati in: output/test_*.py")
                print("[Premi Invio per continuare...]")
                input()
            else:
                print(f"\n[!] Scelta non valida: '{choice}'")
                print("Inserisci un numero da 1 a 4, oppure 0 per uscire.")
                
        except KeyboardInterrupt:
            print("\n\nInterrotto dall'utente. Arrivederci!")
            running = False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            print("\n[Premi Invio per continuare...]")
            input()

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
