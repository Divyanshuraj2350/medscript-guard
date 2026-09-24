from src.validation.validator import validate


def test_known_interaction_flagged():
    prescription = {
        "drugs": [
            {"name": "warfarin", "dosage": "5mg", "frequency": "once daily"},
            {"name": "aspirin", "dosage": "100mg", "frequency": "twice daily"}
        ],
        "patient_age": 68
    }
    result = validate(prescription)
    assert len(result) >= 1
    assert any(f["type"] == "INTERACTION" for f in result)


def test_safe_pair_no_flags():
    prescription = {
        "drugs": [
            {"name": "amoxicillin", "dosage": "500mg", "frequency": "twice daily"}
        ],
        "patient_age": 30
    }
    result = validate(prescription)
    assert result == []


def test_overdose_flagged():
    prescription = {
        "drugs": [
            {"name": "aspirin", "dosage": "500mg", "frequency": "once daily"}
        ],
        "patient_age": 45
    }
    result = validate(prescription)
    assert any(f["type"] == "DOSAGE_ERROR" for f in result)


def test_dose_within_range_no_flag():
    prescription = {
        "drugs": [
            {"name": "aspirin", "dosage": "100mg", "frequency": "once daily"}
        ],
        "patient_age": 45
    }
    result = validate(prescription)
    assert not any(f["type"] == "DOSAGE_ERROR" for f in result)
