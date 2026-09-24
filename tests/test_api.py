from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_valid_prescription():
    response = client.post(
        "/analyze",
        json={"prescription_text": "Patient takes warfarin 5mg once daily"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "overall_risk" in data
    assert "flags" in data
    assert "summary" in data


def test_analyze_empty_string_returns_422():
    response = client.post("/analyze", json={"prescription_text": ""})
    assert response.status_code == 422
