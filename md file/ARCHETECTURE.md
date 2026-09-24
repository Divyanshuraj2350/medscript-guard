# MedScript Guard — Architecture Document

## System Overview

MedScript Guard is a 5-stage NLP pipeline wrapped in a FastAPI backend
with a Streamlit frontend and MLflow experiment tracking.

```
Raw Prescription Text (user input)
           │
           ▼
┌─────────────────────┐
│   1. Preprocessor   │  Normalizes drug aliases, expands abbreviations,
│  preprocessor.py    │  strips special characters, lowercases text
└─────────┬───────────┘
           │ cleaned text string
           ▼
┌─────────────────────┐
│   2. NER Engine     │  Rule-based extraction using regex patterns.
│   ner_model.py      │  Extracts: DRUG, DOSAGE, FREQUENCY, PATIENT_AGE
└─────────┬───────────┘
           │ list of entity dicts
           ▼
┌──────────────────────────┐
│  3. Relation Extractor   │  Links each drug to its dosage and frequency
│  relation_extractor.py   │  by index order. Extracts patient age.
└─────────┬────────────────┘
           │ prescription object (structured dict)
           ▼
┌─────────────────────┐
│   4. Validator      │  Hybrid: rule engine checks drug pairs against
│   validator.py      │  interaction dict. Regex checks dosage vs safe range.
└─────────┬───────────┘
           │ list of flag dicts
           ▼
┌─────────────────────┐
│   5. Scorer         │  Determines overall risk level from flag severities.
│   scorer.py         │  Generates human-readable summary string.
└─────────┬───────────┘
           │ risk report dict
           ▼
┌─────────────────────┐
│   FastAPI /analyze  │  Orchestrates all 5 stages. Input validation.
│   api/main.py       │  Returns risk report as JSON.
└─────────┬───────────┘
           │ JSON response
           ▼
┌─────────────────────┐
│ Streamlit Dashboard │  Calls API, renders risk badge, flag table,
│ dashboard/app.py    │  color-coded severity display.
└─────────────────────┘

MLflow logs metrics at stages 2 and 5 (entities extracted, flags count,
inference time, overall risk tag).
```

---

## Directory Structure

```
medscript-guard/
├── src/
│   ├── preprocessing/
│   │   └── preprocessor.py       # Stage 1
│   ├── ner/
│   │   └── ner_model.py          # Stage 2
│   ├── relation_extraction/
│   │   └── relation_extractor.py # Stage 3
│   ├── validation/
│   │   └── validator.py          # Stage 4
│   └── scoring/
│       └── scorer.py             # Stage 5
├── api/
│   └── main.py                   # FastAPI app
├── dashboard/
│   └── app.py                    # Streamlit UI
├── tests/
│   ├── test_preprocessor.py
│   ├── test_ner.py
│   ├── test_relation_extractor.py
│   ├── test_validator.py
│   ├── test_scorer.py
│   └── test_api.py
├── mlflow_runs/                  # MLflow tracking store
├── data/
│   ├── raw/
│   └── processed/
└── requirements.txt
```

---

## Data Contracts Between Stages

### Stage 1 → Stage 2
```
Input:  str  (raw prescription text)
Output: str  (cleaned text)
```

### Stage 2 → Stage 3
```
Input:  str
Output: list[dict]
        {"entity": "DRUG"|"DOSAGE"|"FREQUENCY"|"PATIENT_AGE",
         "value": str,
         "score": float}
```

### Stage 3 → Stage 4
```
Input:  list[dict]
Output: dict
        {
          "drugs": [{"name": str, "dosage": str|None, "frequency": str|None}],
          "patient_age": int|None
        }
```

### Stage 4 → Stage 5
```
Input:  dict (prescription object)
Output: list[dict]
        {"type": "INTERACTION"|"DOSAGE_ERROR"|"AGE_CONTRAINDICATION",
         "drugs_involved": list[str],
         "message": str,
         "severity": "LOW"|"MEDIUM"|"HIGH"|"CRITICAL"}
```

### Stage 5 → API
```
Input:  list[dict] (flags)
Output: dict
        {"overall_risk": str, "flags": list, "summary": str}
```

---

## Key Design Decisions

### Why rule-based NER instead of a transformer model?

The original implementation used `blaze999/Medical-NER` from HuggingFace.
During testing it failed to extract multiple drugs from a single prescription
and incorrectly merged dosage tokens. A regex-based approach with a curated
drug list gives deterministic, testable, and faster results for the current
scope. A transformer model becomes valuable when the drug list needs to scale
to thousands of drugs dynamically.

### Why hybrid validation (rules + regex)?

Pure ML models for drug interaction detection require large labeled datasets
and can produce false negatives on rare drug pairs. Rule-based interaction
dictionaries are 100% auditable and explainable — a critical requirement
in healthcare. The hybrid approach uses rules for known interactions and
regex for dosage range checking.

### Why MLflow?

MLflow tracks every analysis run with input length, entity count, flag count,
inference time, and risk level. This creates an audit trail and makes it
possible to monitor pipeline performance over time without changing
production code.