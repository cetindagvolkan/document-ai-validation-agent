import json
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# =====================================================================
# STEP 1: Pydantic Schema für strukturierte Dokumenten-Extraktion
# =====================================================================
class DocumentExtraction(BaseModel):
    document_id: str = Field(description="Eindeutige ID des Dokuments")
    document_type: str = Field(description="Klassifizierter Dokumententyp (z.B. Kreditanfrage, Gehaltsnachweis)")
    applicant_name: str = Field(description="Name des Kunden / Antragstellers")
    requested_amount: float = Field(description="Beantragter Summe/Betrag in EUR")
    monthly_income: Optional[float] = Field(default=None, description="Monatliches Nettoeinkommen in EUR")
    extraction_confidence: float = Field(description="Konfidenzscore der KI-Extraktion (0.0 - 1.0)")

# =====================================================================
# STEP 2: Document Validation Agent (Plausibilität & Quality Gate)
# =====================================================================
class DocumentValidationAgent:
    def __init__(self, min_confidence: float = 0.85, max_auto_amount: float = 50000.0):
        self.min_confidence = min_confidence
        self.max_auto_amount = max_auto_amount

    def process_document(self, data: DocumentExtraction) -> Dict[str, Any]:
        flags = []
        status = "APPROVED_AUTOMATED"

        # 1. Konfidenz-Prüfung (Quality Gate)
        if data.extraction_confidence < self.min_confidence:
            status = "NEEDS_HUMAN_REVIEW"
            flags.append(f"Geringer Konfidenzwert: {data.extraction_confidence:.2f} < Schwellenwert {self.min_confidence}")

        # 2. Betragsgrenze für automatische Freigabe
        if data.requested_amount > self.max_auto_amount:
            status = "NEEDS_HUMAN_REVIEW"
            flags.append(f"Kreditbetrag ({data.requested_amount:,.2f} €) übersteigt Auto-Freigabegrenze ({self.max_auto_amount:,.2f} €)")

        # 3. Finanzielle Plausibilitätsregel
        if data.monthly_income and data.monthly_income > 0:
            debt_to_income_ratio = (data.requested_amount / (data.monthly_income * 12))
            if debt_to_income_ratio > 3.0:
                flags.append(f"Warnung: Betrag entspricht {debt_to_income_ratio:.1f} Jahresgehältern (Erhöhtes Ausfallrisiko)")

        return {
            "document_id": data.document_id,
            "applicant": data.applicant_name,
            "document_type": data.document_type,
            "status": status,
            "review_flags": flags,
            "confidence": data.extraction_confidence
        }

# =====================================================================
# STEP 3: Evaluation Engine mit Golden Dataset (Referenzdaten)
# =====================================================================
class EvaluationEngine:
    """
    Evaluations-Modul zur Messung der Extraktionsgenauigkeit
    nicht-deterministischer LLM-Ausgaben gegen ein Golden Dataset.
    """
    def __init__(self, golden_dataset: List[Dict[str, Any]]):
        self.golden_dataset = {doc["document_id"]: doc for doc in golden_dataset}

    def evaluate_extractions(self, extractions: List[DocumentExtraction]) -> Dict[str, Any]:
        total_fields = 0
        correct_fields = 0
        field_errors = []

        fields_to_check = ["document_type", "applicant_name", "requested_amount", "monthly_income"]

        for ext in extractions:
            doc_id = ext.document_id
            if doc_id not in self.golden_dataset:
                continue

            expected = self.golden_dataset[doc_id]
            ext_dict = ext.model_dump()

            for field in fields_to_check:
                total_fields += 1
                exp_val = expected.get(field)
                act_val = ext_dict.get(field)

                # Toleranz für Floats
                if isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
                    match = abs(exp_val - act_val) < 0.01
                else:
                    match = str(exp_val).strip().lower() == str(act_val).strip().lower()

                if match:
                    correct_fields += 1
                else:
                    field_errors.append({
                        "document_id": doc_id,
                        "field": field,
                        "expected": exp_val,
                        "actual": act_val
                    })

        accuracy = (correct_fields / total_fields) * 100 if total_fields > 0 else 0.0
        return {
            "total_documents_evaluated": len(extractions),
            "total_fields_checked": total_fields,
            "correct_fields": correct_fields,
            "overall_accuracy_pct": round(accuracy, 2),
            "field_errors": field_errors
        }

# =====================================================================
# DEMO EXECUTION
# =====================================================================
if __name__ == "__main__":
    print("=== 1. GOLDEN DATASET (SOLL-DATEN) ===")
    golden_dataset = [
        {
            "document_id": "DOC-001",
            "document_type": "Kreditanfrage_Praxisuebernahme",
            "applicant_name": "Dr. med. Anna Musterfrau",
            "requested_amount": 75000.0,
            "monthly_income": 8500.0
        },
        {
            "document_id": "DOC-002",
            "document_type": "Gehaltsnachweis",
            "applicant_name": "Markus Weber",
            "requested_amount": 12000.0,
            "monthly_income": 4200.0
        }
    ]
    print(json.dumps(golden_dataset, indent=2, ensure_ascii=False))

    print("\n=== 2. SIMULIERTE LLM-EXTRAKTIONEN (IST-DATEN) ===")
    simulated_llm_outputs = [
        DocumentExtraction(
            document_id="DOC-001",
            document_type="Kreditanfrage_Praxisuebernahme",
            applicant_name="Dr. med. Anna Musterfrau",
            requested_amount=75000.0,
            monthly_income=8500.0,
            extraction_confidence=0.94
        ),
        DocumentExtraction(
            document_id="DOC-002",
            document_type="Gehaltsnachweis",
            applicant_name="Markus Weber",
            requested_amount=12000.0,
            monthly_income=4000.0,  # Leicht abweichender Extraktionsfehler!
            extraction_confidence=0.78  # Niedrige Konfidenz
        )
    ]

    print("\n=== 3. AGENTEN-PROZESSIERUNG (HUMAN-IN-THE-LOOP) ===")
    agent = DocumentValidationAgent()
    for doc in simulated_llm_outputs:
        res = agent.process_document(doc)
        print(f"Doc ID {doc.document_id} -> Status: {res['status']}")
        if res['review_flags']:
            print(f"   Flags: {res['review_flags']}")

    print("\n=== 4. EVALUATION DER LLM-GENAUIGKEIT (EVAL ENGINE) ===")
    eval_engine = EvaluationEngine(golden_dataset)
    metrics = eval_engine.evaluate_extractions(simulated_llm_outputs)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
