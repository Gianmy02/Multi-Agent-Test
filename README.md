# Multi-Agent Test Generator

Sistema multi-agente per la generazione automatica di test Python con copertura garantita dell'80% tramite AI generativa e validazione formale della grammatica.

## 🎯 Caratteristiche Principali

- **Validazione Grammaticale Rigorosa**: Parser Lark che garantisce conformità al subset Python definito
- **Generazione Test Automatica**: LLM genera test pytest mirati per ogni branch del codice
- **Coverage Garantita**: Loop di ottimizzazione iterativo fino al raggiungimento dell'80% branch coverage
- **Architettura Multi-Agente**: Agenti specializzati per analisi, generazione, ottimizzazione e validazione
- **Modalità Mock**: Demo deterministiche con LLM simulato per presentazioni

## 🚀 Quick Start

### Installazione

```bash
pip install -r requirements.txt
```

### Esecuzione Demo

**Launcher Unificato** (consigliato):
```bash
python run_demos.py
```

Menu interattivo per scegliere quale demo eseguire (1-3):
- **Demo 1 - Simple**: Funzione base con branch (`add`)
- **Demo 2 - Auth**: Logica condizionale (password/login)
- **Demo 3 - Calculator**: Menu aritmetico completo (5 funzioni)

**Esecuzione Demo Singole**:
```bash
python demos/demo_simple.py      # Demo 1
python demos/demo_auth.py        # Demo 2
python demos/demo_calculator.py  # Demo 3
```

## 📊 Risultati Attesi

Tutte le demo raggiungono **100% Branch Coverage**:

| Demo | Funzioni | Branch | Test Generati | Coverage |
|------|----------|--------|---------------|----------|
| Simple | 1 | 1 | 3 | 100% |
| Auth | 2 | 3 | 4 | 100% |
| Calculator | 5 | 12 | 11 | 100% |

## 🏗️ Architettura

### Componenti Principali

```
test_generator/
├── orchestrator.py          # Coordinatore principale
├── agents.py                # Agenti specializzati
│   ├── CodeAnalyzerAgent    # Validazione Lark + analisi AST
│   ├── UnitTestGeneratorAgent
│   ├── CoverageOptimizerAgent
│   └── TestValidatorAgent
├── llm_client.py            # Abstraction LLM (Mock/Real)
├── coverage_calculator.py   # Calcolo coverage via pytest
├── python_subset.lark       # Grammatica formale
└── config.py                # Configurazione (target 80%)
```

### Subset Python Supportato

**Costrutti Permessi**:
- ✅ Definizioni funzione (`def`)
- ✅ If/Else (annidati)
- ✅ Operatori aritmetici (`+`, `-`, `*`, `/`)
- ✅ Comparazioni (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- ✅ Assegnamenti e return
- ✅ Commenti (`#`)

**NON Supportati**:
- ❌ Classi, decoratori, list comprehensions

## 🔬 Flusso di Esecuzione

1. **Validazione Lark**: Il codice deve passare il parser (Fail-Fast)
2. **Analisi Statica**: Estrazione funzioni, parametri, branch (AST)
3. **Generazione Test**: LLM genera test per ogni branch identificato
4. **Calcolo Coverage**: Esecuzione pytest con `--cov-branch`
5. **Ottimizzazione**: Loop iterativo per branch non coperti
6. **Validazione Qualità**: Quality score (0-10) basato su coverage + best practices

## 📁 Output

I test generati vengono salvati in:
```
output/
├── test_auth.py              # Test per demo_auth
├── test_calculator.py        # Test per demo_calculator
└── code_to_test.py          # Test per demo_simple
```

## 🎓 Documentazione Accademica

- `RELAZIONE_PROGETTO_FINALE.md`: Report strutturato 
- `RELAZIONE_SCELTE_PROGETTUALI.md`: Decisioni architetturali e alternative

## ⚙️ Configurazione

`config.py`:
```python
TARGET_BRANCH_COVERAGE = 80.0  # Coverage minima richiesta
USE_MOCK = True                # Mock LLM per demo deterministiche
```

## 🧪 Modalità di Test

### Mock Mode (Default)
```python
orchestrator = Orchestrator(use_mock=True)
```
Output deterministico, ideale per demo e presentazioni.

### Real LLM Mode
```python
orchestrator = Orchestrator(use_mock=False)
```
Connessione a API LLM reali (OpenAI/GitHub/Ollama).

## 📝 Licenza

MIT License - Progetto accademico per corso di Ingegneria dei Linguaggi di Programmazione.

## 👤 Autore

Sviluppato come progetto finale per il corso di Ingegneria dei Linguaggi di Programmazione da Gianmarco Riviello.
