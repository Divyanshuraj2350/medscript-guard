"""
Real-world Indian prescription test cases.
Tests cover: drug interactions, age contraindications,
dosage errors, and safe prescriptions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.preprocessor import preprocess
from src.ner.ner_model import extract_entities
from src.relation_extraction.relation_extractor import extract_relations
from src.validation.validator import validate
from src.scoring.scorer import score


def run_pipeline(text):
    cleaned = preprocess(text)
    entities = extract_entities(cleaned)
    prescription = extract_relations(entities)
    flags = validate(prescription)
    result = score(flags)
    return result, flags, prescription


# ─── INTERACTION TESTS ───────────────────────────────────────────────

def test_warfarin_aspirin_interaction():
    """Warfarin + Aspirin — most common dangerous pair in India"""
    result, flags, _ = run_pipeline(
        "Patient age 65. Warfarin 5mg OD with Ecosprin 75mg OD"
    )
    assert result["overall_risk"] in ["HIGH", "CRITICAL"]
    assert any(f["type"] == "INTERACTION" for f in flags)


def test_metformin_alcohol_interaction():
    """Metformin + Alcohol — common in diabetic patients"""
    result, flags, _ = run_pipeline(
        "Patient age 52. Glycomet 500mg BD. Patient consumes alcohol daily."
    )
    assert result["overall_risk"] in ["HIGH", "CRITICAL"]
    assert any(f["type"] == "INTERACTION" for f in flags)


def test_ssri_tramadol_critical():
    """Escitalopram + Tramadol — serotonin syndrome risk"""
    result, flags, _ = run_pipeline(
        "Patient age 38. Escitalopram 10mg OD with Tramadol 50mg BD"
    )
    assert result["overall_risk"] == "CRITICAL"
    assert any(f["severity"] == "CRITICAL" for f in flags)


def test_two_nsaids_together():
    """Ibuprofen + Diclofenac — two NSAIDs prescribed together"""
    result, flags, _ = run_pipeline(
        "Patient age 45. Ibuprofen 400mg TDS with Diclofenac 50mg BD"
    )
    assert result["overall_risk"] in ["HIGH", "CRITICAL"]
    assert any(f["type"] == "INTERACTION" for f in flags)


def test_clopidogrel_omeprazole():
    """Clopidogrel + Omeprazole — reduces clopidogrel effectiveness"""
    result, flags, _ = run_pipeline(
        "Patient age 60. Clopidogrel 75mg OD with Omeprazole 20mg OD"
    )
    assert any(f["type"] == "INTERACTION" for f in flags)


def test_ace_inhibitor_potassium():
    """Lisinopril + Potassium — hyperkalemia risk"""
    result, flags, _ = run_pipeline(
        "Patient age 58. Lisinopril 10mg OD with Potassium 20meq BD"
    )
    assert any(f["type"] == "INTERACTION" for f in flags)


# ─── AGE CONTRAINDICATION TESTS ──────────────────────────────────────

def test_nimesulide_child_under_12():
    """Nimesulide banned under 12 in India — CDSCO ruling"""
    result, flags, _ = run_pipeline(
        "Patient age 8. Nimesulide 100mg BD for fever"
    )
    assert result["overall_risk"] in ["HIGH", "CRITICAL"]
    assert any(f["type"] == "AGE_CONTRAINDICATION" for f in flags)


def test_disprin_child_reye_syndrome():
    """Disprin (aspirin) under age 16 — Reye syndrome risk"""
    result, flags, _ = run_pipeline(
        "Patient age 10. Disprin 100mg OD for headache"
    )
    assert any(f["type"] == "AGE_CONTRAINDICATION" for f in flags)


def test_ecosprin_teenager():
    """Ecosprin (aspirin) for 14-year-old — should flag"""
    result, flags, _ = run_pipeline(
        "Patient age 14. Ecosprin 75mg OD"
    )
    assert any(f["type"] == "AGE_CONTRAINDICATION" for f in flags)


def test_dolo_child_safe():
    """Dolo (paracetamol) for child — should be safe"""
    result, flags, _ = run_pipeline(
        "Patient age 6. Dolo 250mg TDS for fever"
    )
    assert not any(f["type"] == "AGE_CONTRAINDICATION" for f in flags)


def test_nimesulide_adult_safe_age():
    """Nimesulide for adult — age contraindication should not fire"""
    result, flags, _ = run_pipeline(
        "Patient age 30. Nimesulide 100mg BD"
    )
    assert not any(f["type"] == "AGE_CONTRAINDICATION" for f in flags)


# ─── DOSAGE ERROR TESTS ──────────────────────────────────────────────

def test_aspirin_overdose():
    """Aspirin 500mg — above safe limit of 325mg"""
    result, flags, _ = run_pipeline(
        "Patient age 55. Aspirin 500mg OD"
    )
    assert any(f["type"] == "DOSAGE_ERROR" for f in flags)


def test_paracetamol_overdose():
    """Paracetamol 1200mg — above safe limit of 1000mg"""
    result, flags, _ = run_pipeline(
        "Patient age 40. Paracetamol 1200mg TDS"
    )
    assert any(f["type"] == "DOSAGE_ERROR" for f in flags)


def test_ibuprofen_within_range():
    """Ibuprofen 400mg — within safe range"""
    result, flags, _ = run_pipeline(
        "Patient age 35. Ibuprofen 400mg BD"
    )
    assert not any(f["type"] == "DOSAGE_ERROR" for f in flags)


def test_warfarin_high_dose():
    """Warfarin 15mg — above safe limit of 10mg"""
    result, flags, _ = run_pipeline(
        "Patient age 70. Warfarin 15mg OD"
    )
    assert any(f["type"] == "DOSAGE_ERROR" for f in flags)


# ─── SAFE PRESCRIPTION TESTS ─────────────────────────────────────────

def test_amoxicillin_safe():
    """Amoxicillin alone — no flags expected"""
    result, flags, _ = run_pipeline(
        "Patient age 30. Amoxicillin 500mg TDS for 5 days"
    )
    assert result["overall_risk"] == "LOW"
    assert flags == []


def test_metformin_alone_safe():
    """Metformin alone without alcohol — safe"""
    result, flags, _ = run_pipeline(
        "Patient age 50. Metformin 500mg BD with meals"
    )
    assert result["overall_risk"] == "LOW"


def test_crocin_adult_safe():
    """Crocin (paracetamol) for adult fever — safe"""
    result, flags, _ = run_pipeline(
        "Patient age 25. Crocin 650mg TDS for fever"
    )
    assert result["overall_risk"] == "LOW"


# ─── BRAND NAME MAPPING TESTS ────────────────────────────────────────

def test_brand_names_mapped_correctly():
    """Dolo and Disprin should map to paracetamol and aspirin"""
    _, _, prescription = run_pipeline(
        "Patient age 30. Dolo 500mg OD with Disprin 75mg OD"
    )
    drug_names = [d["name"] for d in prescription["drugs"]]
    assert "paracetamol" in drug_names or "aspirin" in drug_names


def test_indian_frequency_shorthand():
    """OD, BD, TDS shorthand should be parsed correctly"""
    cleaned = preprocess("Warfarin 5mg OD Aspirin 100mg BD Metformin 500mg TDS")
    entities = extract_entities(cleaned)
    freq_values = [e["value"] for e in entities if e["entity"] == "FREQUENCY"]
    assert len(freq_values) >= 1
