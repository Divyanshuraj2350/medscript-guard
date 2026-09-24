# MedScript Guard — Task Tracker

## Completed Tasks

| Task | Module | Tests | Status |
|---|---|---|---|
| 1 | Project scaffold, venv, requirements | pip install clean | ✅ Done |
| 2 | Preprocessor — normalization, abbreviation expansion | 4/4 passed | ✅ Done |
| 3 | NER engine — entity extraction | 3/3 passed | ✅ Done |
| 4 | Relation extractor — drug-dosage linking | 3/3 passed | ✅ Done |
| 5 | Validator — interaction rules + dosage ranges | 4/4 passed | ✅ Done |
| 6 | Scorer — risk level + summary | 3/3 passed | ✅ Done |
| 7 | FastAPI backend — /analyze + /health endpoints | 3/3 passed | ✅ Done |
| 8 | MLflow experiment tracking | Runs visible in UI | ✅ Done |
| 9 | Streamlit dashboard | Manual UI test passed | ✅ Done |

**Total: 20/20 tests passing**

---

## Known Issues (To Fix)

| Priority | Issue | Location | Fix |
|---|---|---|---|
| HIGH | Nimesulide not in drug list | ner_model.py | Add to DRUG_NAMES |
| HIGH | Age-based contraindications not implemented | validator.py | Add AGE_CONTRAINDICATIONS dict and logic |
| MEDIUM | Drug list limited to 20 drugs | ner_model.py | Integrate RxNorm or DrugBank drug list |
| MEDIUM | MLflow UI requires MLFLOW_ALLOW_FILE_STORE=true flag | mlflow_runs | Migrate to SQLite backend |
| LOW | Index-based drug-dosage linking fails if drug has no dosage | relation_extractor.py | Add proximity-based fallback |
| LOW | Dosage range checker fails on merged "5mg once daily" tokens | relation_extractor.py | Already fixed with regex extraction |

---

## Planned Enhancements

### Phase 2 — Rule Expansion
- [ ] Add nimesulide to drug list with age < 12 contraindication
- [ ] Add aspirin age < 16 contraindication (Reye's syndrome)
- [ ] Add 10 more drug interaction pairs from DrugBank
- [ ] Add 10 more drugs to dosage range checker
- [ ] Implement AGE_CONTRAINDICATIONS validation in validator.py

### Phase 3 — NLP Upgrade
- [ ] Fine-tune ClinicalBERT on i2b2 2010 NER dataset
- [ ] Replace regex NER with fine-tuned model
- [ ] Add confidence threshold UI in dashboard
- [ ] Add entity highlighting in input text

### Phase 4 — Production Readiness
- [ ] Migrate MLflow to SQLite backend
- [ ] Dockerize the application
- [ ] Add JWT authentication to API
- [ ] Add rate limiting to /analyze endpoint
- [ ] Add request logging middleware
- [ ] Deploy to cloud (AWS/GCP/Railway)

### Phase 5 — Data & Integration
- [ ] Apply for MIMIC-III access for real clinical note testing
- [ ] Integrate DrugBank public API for live interaction checking
- [ ] Add RxNorm drug normalization API
- [ ] Build admin panel to add/edit rules without code changes

---

## How to Run the Project

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run all tests
pytest tests/ -v

# 3. Start API server
uvicorn api.main:app --reload --port 8000

# 4. Start dashboard (new terminal)
streamlit run dashboard/app.py

# 5. View MLflow runs (new terminal)
MLFLOW_ALLOW_FILE_STORE=true mlflow ui --backend-store-uri ./mlflow_runs
```
