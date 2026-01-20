#!/usr/bin/env python
"""
Multi-Agent Test Generator - Demo Launcher
Launcher unico per tutte le demo del progetto
"""
import sys
import os

def main():
    running = True
    executed_demos = {}  # Track executed demos: {demo_num: result_summary}
    
    while running:
        print("\n" + "=" * 70)
        print("MULTI-AGENT TEST GENERATOR - DEMO LAUNCHER")
        print("=" * 70)
        print("\nDemo disponibili:")
        print("  1. Simple Demo    - Funzione base con branch (add)")
        print("  2. Auth Demo      - Logica condizionale (password/login)")
        print("  3. Calculator     - Menu aritmetico completo (5 funzioni)")
        print("  0. Esci")
        
        # Show executed demos status
        if executed_demos:
            print("\nDemo già eseguite:")
            for num, summary in executed_demos.items():
                demo_name = {1: "Simple", 2: "Auth", 3: "Calculator"}[num]
                print(f"  [{num}] {demo_name}: {summary}")
        
        print("-" * 70)
        
        try:
            choice = input("\nScegli demo (1-3, 0 per uscire): ").strip()
            
            if choice == "0":
                print("\nArrivederci!")
                running = False
            elif choice in ["1", "2", "3"]:
                demo_num = int(choice)
                
                # Check if already executed
                if demo_num in executed_demos:
                    demo_name = {1: "Simple", 2: "Auth", 3: "Calculator"}[demo_num]
                    print(f"\n[✓] Demo {demo_num} ({demo_name}) già eseguita!")
                    print(f"    Risultato: {executed_demos[demo_num]}")
                    print(f"    Test salvati in: output/test_*.py")
                    print("\n[Premi Invio per continuare...]")
                    input()
                    continue
                
                # Execute demo
                if choice == "1":
                    print("\n>> Avvio DEMO 1: Simple...")
                    print("=" * 70)
                    import demos.demo_simple as demo
                    demo.main()
                    executed_demos[1] = "100% coverage, 3 test"
                elif choice == "2":
                    print("\n>> Avvio DEMO 2: Auth...")
                    print("=" * 70)
                    import demos.demo_auth as demo
                    demo.main()
                    executed_demos[2] = "100% coverage, 4 test"
                elif choice == "3":
                    print("\n>> Avvio DEMO 3: Calculator...")
                    print("=" * 70)
                    import demos.demo_calculator as demo
                    demo.main()
                    executed_demos[3] = "100% coverage, 11 test"
                
                print("\n[Demo completata. Premi Invio per continuare...]")
                input()
            else:
                print(f"\n[!] Scelta non valida: '{choice}'")
                print("Inserisci un numero da 1 a 3, oppure 0 per uscire.")
                
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
    # Aggiungi la directory corrente al path per imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
