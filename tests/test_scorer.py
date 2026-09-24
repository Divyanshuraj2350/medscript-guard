from src.scoring.scorer import score


def test_high_flag_produces_high_risk():
    flags = [
        {
            "type": "INTERACTION",
            "drugs_involved": ["warfarin", "aspirin"],
            "message": "High bleeding risk",
            "severity": "HIGH"
        }
    ]
    result = score(flags)
    assert result["overall_risk"] == "HIGH"
    assert "1" in result["summary"]


def test_empty_flags_produces_low_risk():
    result = score([])
    assert result["overall_risk"] == "LOW"
    assert result["summary"] == "No issues detected. Safe to dispense."
    assert result["flags"] == []


def test_summary_contains_flag_count():
    flags = [
        {"type": "INTERACTION", "drugs_involved": ["a", "b"],
         "message": "test", "severity": "MEDIUM"},
        {"type": "DOSAGE_ERROR", "drugs_involved": ["c"],
         "message": "test", "severity": "MEDIUM"}
    ]
    result = score(flags)
    assert "2" in result["summary"]
