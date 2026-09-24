from src.ner.ner_model import extract_entities


def test_drug_entity_found():
    input_text = "Patient takes warfarin 5mg once daily"
    result = extract_entities(input_text)
    assert isinstance(result, list)
    assert any(item.get("entity") == "DRUG" for item in result)


def test_output_schema():
    input_text = "Take aspirin 100mg twice daily"
    result = extract_entities(input_text)
    if result:
        for item in result:
            assert set(item.keys()) == {"entity", "value", "score"}


def test_empty_input_does_not_crash():
    input_text = ""
    result = extract_entities(input_text)
    assert isinstance(result, list)
