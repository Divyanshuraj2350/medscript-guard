from src.preprocessing.preprocessor import preprocess


def test_tylenol_returns_acetaminophen():
    result = preprocess("tylenol")
    assert "acetaminophen" in result


def test_bid_expansion():
    result = preprocess("Take BID with water")
    assert "twice daily" in result


def test_special_characters_stripped():
    result = preprocess("Hello!! World##")
    assert result == "hello world"


def test_aspirin_po_expansion():
    result = preprocess("aspirin 500mg PO")
    assert "by mouth" in result
    assert "aspirin" in result
