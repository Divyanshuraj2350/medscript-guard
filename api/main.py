from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.preprocessing.preprocessor import preprocess
from src.ner.ner_model import extract_entities
from src.relation_extraction.relation_extractor import extract_relations
from src.validation.validator import validate
from src.scoring.scorer import score

import os
import mlflow
import mlflow_setup
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
mlflow.set_tracking_uri("./mlflow_runs")
mlflow.set_experiment("medscript-guard")

app = FastAPI(title="MedScript Guard API")


class PrescriptionRequest(BaseModel):
    prescription_text: str


class RiskReport(BaseModel):
    overall_risk: str
    flags: list
    summary: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=RiskReport)
def analyze(request: PrescriptionRequest):
    text = request.prescription_text
    if not text or len(text.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="Prescription text cannot be empty"
        )

    try:
        cleaned = preprocess(text)
        entities = extract_entities(cleaned)
        prescription = extract_relations(entities)
        flags = validate(prescription)
        result = score(flags)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Please try again."
        )
