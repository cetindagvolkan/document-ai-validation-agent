# Document AI & Validation Agent for Financial Audit

Ein leichtgewichtiger **Proof of Concept (PoC)** zur Demonstration intelligenter Dokumentenverarbeitung, Schema-Validierung, Konfidenzmessung und systematischer LLM-Evaluierung im Bankenumfeld.

---

## 🏗 Architecture & Pipeline Overview

```
[ Unstrukturierte Dokumente (PDF / Text) ]
                   │
                   ▼
  [ LLM Extraction via Azure OpenAI / LangChain ]
     (Schema-Enforcement via Pydantic)
                   │
                   ▼
    [ Document Validation Agent ]
   ├── Konfidenz-Threshold Check (< 85% ?)
   ├── Risikogrenze / Betragsprüfung (> 50.000 € ?)
   └── Financial Debt-to-Income Plausibilität
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
[ APPROVED_AUTOMATED ]   [ NEEDS_HUMAN_REVIEW ]
                         (Human-in-the-Loop)
                   │
                   ▼
       [ Evaluation Engine ]
 (Vergleich gegen Golden Dataset / Accuracy Metric)
```

---

## 🚀 Key Features

1. **Strukturierte Extraktion (Schema Enforcement):**
   Verwendung von Pydantic-Schemata zur Vermeidung unstrukturierter LLM-Freitexte und Garanzierung von typsicheren JSON-Ausgaben für Backend-Microservices.

2. **Quality Gate & Human-in-the-Loop:**
   Automatische Zuweisung von `NEEDS_HUMAN_REVIEW` bei geringen Konfidenzscores (< 0.85) oder Beträgen oberhalb definierter Freigabegrenzen.

3. **Systematische Evaluierung (Golden Dataset):**
   Feld-genaue Messung der Extraktionsgenauigkeit (*Field-Level Accuracy / Precision*) gegen ein händisch verifiziertes Referenz-Set zur Qualitätssicherung nicht-deterministischer Modelle.
