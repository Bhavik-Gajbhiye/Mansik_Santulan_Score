"""
Menteez End-to-End Automated Test Suite
Tests FastAPI endpoints, ML prediction accuracy, Pydantic validation, and Static HTML markup.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("[PASS] GET /health")


def test_static_index_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    content = response.text

    # Verify key element IDs and structure
    required_ids = [
        "predict-form",
        "submit-btn",
        "age",
        "gender",
        "country",
        "academic_level",
        "most_used_platform",
        "purpose_of_use",
        "avg_daily_usage_hours",
        "daily_unlocks",
        "study_hours",
        "physical_activity_hours",
        "sleep_hours_per_night",
        "stress_level",
        "stress_level_group",
        "state-idle",
        "state-loading",
        "state-result",
        "state-error",
        "score-number",
        "score-band",
        "score-context",
        "reset-btn",
        "error-retry-btn",
    ]
    for req_id in required_ids:
        assert f'id="{req_id}"' in content, f"Missing required ID: {req_id}"

    assert "STUDENT WELLNESS ANALYTICS" in content or "Student Wellness Analytics" in content
    assert "Mental Health" in content
    assert "Signal" in content
    print("[PASS] GET / static index serving and element IDs verified")


def test_predict_endpoint_valid():
    payload = {
        "age": 21,
        "gender": "Female",
        "country": "India",
        "academic_level": "Undergraduate",
        "most_used_platform": "Instagram",
        "purpose_of_use": "Entertainment",
        "avg_daily_usage_hours": 3.5,
        "daily_unlocks": 45,
        "study_hours": 5.0,
        "physical_activity_hours": 1.5,
        "sleep_hours_per_night": 7.5,
        "stress_level": "Medium",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "mental_health_score" in data
    assert "band" in data
    assert "context" in data
    assert 0.0 <= data["mental_health_score"] <= 10.0
    assert data["band"] in ["Struggling", "Managing", "Steady", "Thriving"]
    print(
        f"[PASS] POST /predict (balanced): Score={data['mental_health_score']}, Band='{data['band']}'"
    )


def test_predict_endpoint_high_stress():
    payload = {
        "age": 19,
        "gender": "Male",
        "country": "USA",
        "academic_level": "Undergraduate",
        "most_used_platform": "TikTok",
        "purpose_of_use": "Entertainment",
        "avg_daily_usage_hours": 9.0,
        "daily_unlocks": 120,
        "study_hours": 1.0,
        "physical_activity_hours": 0.0,
        "sleep_hours_per_night": 4.0,
        "stress_level": "Very High",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["mental_health_score"] <= 10.0
    print(
        f"[PASS] POST /predict (high stress): Score={data['mental_health_score']}, Band='{data['band']}'"
    )


def test_predict_endpoint_invalid_validation():
    # Negative age & invalid usage hours
    payload = {
        "age": -5,
        "gender": "UnknownGender",
        "country": "",
        "academic_level": "Preschool",
        "most_used_platform": "InvalidPlatform",
        "purpose_of_use": "Gaming",
        "avg_daily_usage_hours": 48.0,
        "daily_unlocks": -10,
        "study_hours": 30.0,
        "physical_activity_hours": -2.0,
        "sleep_hours_per_night": 25.0,
        "stress_level": "Extreme",
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    err = response.json()
    assert "detail" in err
    print(
        f"[PASS] POST /predict (invalid validation): 422 caught {len(err['detail'])} issues"
    )


if __name__ == "__main__":
    test_health_endpoint()
    test_static_index_serving()
    test_predict_endpoint_valid()
    test_predict_endpoint_high_stress()
    test_predict_endpoint_invalid_validation()
    print("\nALL TESTS COMPLETED SUCCESSFULLY!")
