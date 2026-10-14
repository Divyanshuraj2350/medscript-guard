import re
import json
import os
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# ── Model path ──────────────────────────────────────────────────────
_MODEL_PATH = "Divyanshu2350/medscript-ner-model"

# ── Load fine-tuned model once at module level ───────────────────────
print(f"Loading NER model from HuggingFace: {_MODEL_PATH}...")
_tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH)
_model = AutoModelForTokenClassification.from_pretrained(_MODEL_PATH)
_ner_pipeline = pipeline(
    "token-classification",
    model=_model,
    tokenizer=_tokenizer,
    aggregation_strategy="simple",
    device=-1  # CPU — change to 0 if GPU available
)
print("NER model loaded.")

# ── Brand name mapping ───────────────────────────────────────────────
BRAND_TO_GENERIC = {
    "dolo": "paracetamol", "crocin": "paracetamol",
    "combiflam": "ibuprofen", "brufen": "ibuprofen",
    "disprin": "aspirin", "ecosprin": "aspirin",
    "pan": "pantoprazole", "glycomet": "metformin",
    "glucophage": "metformin", "coumadin": "warfarin",
    "tylenol": "acetaminophen", "advil": "ibuprofen",
    "augmentin": "amoxicillin", "zithromax": "azithromycin",
    "cipro": "ciprofloxacin", "flagyl": "metronidazole",
    "lasix": "furosemide", "tenormin": "atenolol",
    "ventolin": "salbutamol", "zyrtec": "cetirizine",
    "nexium": "esomeprazole", "prilosec": "omeprazole"
}

# ── Label mapping from model output ─────────────────────────────────
ENTITY_MAP = {
    "DRUG": "DRUG", "B-DRUG": "DRUG", "I-DRUG": "DRUG",
    "DOSE": "DOSAGE", "B-DOSE": "DOSAGE", "I-DOSE": "DOSAGE",
    "FREQ": "FREQUENCY", "B-FREQ": "FREQUENCY", "I-FREQ": "FREQUENCY",
    "AGE": "PATIENT_AGE", "B-AGE": "PATIENT_AGE", "I-AGE": "PATIENT_AGE",
}


def extract_entities(text: str) -> list:
    if not text:
        return []
    try:
        # Apply brand name mapping first
        text_mapped = text
        for brand, generic in BRAND_TO_GENERIC.items():
            pattern = re.compile(r'\b' + re.escape(brand) + r'\b', re.IGNORECASE)
            text_mapped = pattern.sub(generic, text_mapped)

        # Run fine-tuned model
        raw_results = _ner_pipeline(text_mapped)

        result = []
        seen_values = set()

        for r in raw_results:
            entity_group = r.get("entity_group", r.get("entity", ""))
            mapped = ENTITY_MAP.get(entity_group)
            if not mapped:
                continue
            if r["score"] < 0.5 or len(r["word"].strip()) <= 1:
                continue

            value = r["word"].strip().lower()
            # Skip duplicates
            key = f"{mapped}:{value}"
            if key in seen_values:
                continue
            seen_values.add(key)

            result.append({
                "entity": mapped,
                "value": value,
                "score": round(r["score"], 4)
            })

        return result

    except Exception as e:
        print(f"NER error: {e}")
        return []


# Regex fallback for age — model sometimes misses it
import re as _re
_AGE_PATTERN = _re.compile(
    r'\b(?:age|aged)?\s*(\d{1,3})\s*(?:years?(?:\s*old)?|y/?o|yr)?\b',
    _re.IGNORECASE
)

_ALCOHOL_PATTERN = _re.compile(r'\balcohol\b', _re.IGNORECASE)


def extract_entities_hybrid(text: str) -> list:
    """Model-based NER with regex fallback for age and alcohol."""
    if not text:
        return []

    results = extract_entities(text)

    # Check if age was detected
    has_age = any(e["entity"] == "PATIENT_AGE" for e in results)
    if not has_age:
        for match in _AGE_PATTERN.finditer(text):
            age_val = int(match.group(1))
            if 1 <= age_val <= 120:
                results.append({
                    "entity": "PATIENT_AGE",
                    "value": str(age_val),
                    "score": 1.0
                })
                break

    # Check if alcohol was detected as drug
    has_alcohol = any(
        e["entity"] == "DRUG" and "alcohol" in e["value"]
        for e in results
    )
    if not has_alcohol and _ALCOHOL_PATTERN.search(text):
        results.append({
            "entity": "DRUG",
            "value": "alcohol",
            "score": 1.0
        })

    return results
