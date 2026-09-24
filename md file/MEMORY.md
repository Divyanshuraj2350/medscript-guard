# MedScript Guard — Project Memory

This file records every important decision, bug, fix, and context
that future developers (or future you) need to understand this project.

---

## Why This Project Exists

Built as a portfolio project to demonstrate end-to-end ML pipeline
engineering skills for job applications. The goal was to show:

- Understanding of transformer/NLP pipeline architecture
- Ability to build production-style code with tests
- MLOps awareness (MLflow tracking)
- Real-world problem selection (not a toy dataset)

The medical domain was chosen because it has real public datasets
(i2b2, MIMIC-III), a clear problem (prescription errors cause deaths),
and growing industry demand (HealthTech hiring).

---

## Critical Bugs Encountered and Fixed

### Bug 1 — HuggingFace NER model failure on multi-drug input

**Symptom:** `blaze999/Medical-NER` only detected one DRUG and one DOSAGE
from "Patient age 68. Warfarin 5mg once daily with aspirin 100mg".
The 100mg (aspirin's dose) was incorrectly linked to warfarin, triggering
a false DOSAGE_ERROR.

**Root cause:** The transformer model merged subword tokens and failed
to detect aspirin and 5mg as separate entities in a multi-drug sentence.

**Fix:** Replaced HuggingFace pipeline with deterministic regex-based NER.
Drug names matched from a curated list. Dosages matched with pattern
`\d+\.?\d*\s*(mg|ml|mcg|g)`. Frequencies matched against known phrases.

**Lesson:** Transformer models for NER require fine-tuning on domain-specific
multi-entity examples. A general medical NER model is not reliable for
multi-drug prescriptions out of the box.

---

### Bug 2 — venv location confusion

**Symptom:** `source venv/bin/activate` failed with "no such file".

**Root cause:** Antigravity IDE created `.venv` (with dot prefix) not `venv`.

**Fix:** Always use `source .venv/bin/activate` in this project.

---

### Bug 3 — MLflow UI refused to start

**Symptom:** `mlflow ui --backend-store-uri ./mlflow_runs` threw error:
"filesystem tracking backend is in maintenance mode".

**Root cause:** Newer MLflow versions deprecated the file store backend
and require explicit opt-in.

**Fix:** Run with environment variable:
`MLFLOW_ALLOW_FILE_STORE=true mlflow ui --backend-store-uri ./mlflow_runs`

**Long-term fix:** Migrate to SQLite backend:
Change tracking URI to `sqlite:///mlflow.db` in mlflow_setup.py.

---

### Bug 4 — requirements.txt outside project folder

**Symptom:** `pip install -r requirements.txt` failed — file not found.

**Root cause:** IDE created requirements.txt at the parent directory level
(MEDISCRIPT_TRANSFORM/) instead of inside medscript-guard/.

**Fix:** `mv requirements.txt medscript-guard/` then `cd medscript-guard`.

---

## Known Gaps (Not Bugs, But Limitations)

### Gap 1 — Nimesulide age contraindication not implemented

Nimesulide is banned for children under 12 in India (CDSCO ruling).
The system currently returns LOW risk for "age 11, nimesulide" because:
- Nimesulide is not in the DRUG_NAMES list
- There is no age-based contraindication logic in the validator

**To fix:**
1. Add "nimesulide" to DRUG_NAMES in ner_model.py
2. Add AGE_CONTRAINDICATIONS dict to validator.py
3. Add age contraindication checking logic in validate()

### Gap 2 — Drug list is only 20 drugs

Real prescriptions contain thousands of drugs. The current hardcoded
list will miss any drug not in DRUG_NAMES.

**To fix:** Load drug list from DrugBank public dataset or RxNorm API.

### Gap 3 — Index-based linking breaks for single-drug + no-dosage cases

If prescription has two drugs but only one has a dosage, index linking
gives that dosage to the first drug regardless of text position.

---

## IDE Used

**Antigravity IDE** — an agentic coding IDE. During this project it
sometimes failed to save file changes when prompted. When Antigravity
doesn't save, the fix is to write the file directly via terminal using
`cat > filepath << 'EOF' ... EOF` pattern.

---

## Python Version Note

Project runs on Python 3.14. This caused one warning:
`torch.jit.script is not supported in Python 3.14+`

This warning is harmless for the current rule-based NER implementation
(which doesn't use torch at all). It would matter if the HuggingFace
model was still in use.

---

## Project Timeline

| Date | Milestone |
|---|---|
| Day 1 | Project setup, preprocessor, NER |
| Day 1 | Relation extractor, validator, scorer |
| Day 1 | FastAPI, MLflow, Streamlit dashboard |
| Day 1 | NER model swap (HuggingFace → regex) |
| Day 1 | All 20 tests passing, full pipeline working |

---

## Interview Talking Points

When asked about this project in an interview, lead with these:

1. **"I switched from a transformer model to rule-based NER mid-build."**
   Explain why — the model failed on multi-entity inputs, deterministic
   regex was more reliable for this scope. This shows engineering judgment,
   not just model calling.

2. **"The pipeline has 5 independent stages, each with its own tests."**
   This shows you understand separation of concerns and testability.

3. **"I caught a real clinical gap — nimesulide is banned for children
   under 12 in India, but the system didn't flag it."**
   This shows domain awareness and critical thinking about your own system.

4. **"I used MLflow to track every analysis run."**
   This shows MLOps awareness beyond just building models.

5. **"The hybrid validator uses both rules and regex — not pure ML."**
   Explain the tradeoff: rules are auditable and explainable, which matters
   in healthcare more than raw accuracy.