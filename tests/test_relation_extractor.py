from src.relation_extraction.relation_extractor import extract_relations


def test_single_drug_linked():
    entities = [
        {"entity": "DRUG", "value": "warfarin", "score": 0.95},
        {"entity": "DOSAGE", "value": "5mg", "score": 0.90},
        {"entity": "FREQUENCY", "value": "once daily", "score": 0.88}
    ]
    result = extract_relations(entities)
    assert result["drugs"][0]["name"] == "warfarin"
    assert result["drugs"][0]["dosage"] == "5mg"
    assert result["drugs"][0]["frequency"] == "once daily"


def test_two_drugs_both_present():
    entities = [
        {"entity": "DRUG", "value": "warfarin", "score": 0.95},
        {"entity": "DOSAGE", "value": "5mg", "score": 0.90},
        {"entity": "DRUG", "value": "aspirin", "score": 0.92},
        {"entity": "DOSAGE", "value": "100mg", "score": 0.88}
    ]
    result = extract_relations(entities)
    assert len(result["drugs"]) == 2
    assert result["drugs"][0]["name"] == "warfarin"
    assert result["drugs"][1]["name"] == "aspirin"


def test_missing_dosage_is_null():
    entities = [
        {"entity": "DRUG", "value": "metformin", "score": 0.93}
    ]
    result = extract_relations(entities)
    assert result["drugs"][0]["dosage"] is None
    assert result["drugs"][0]["frequency"] is None
