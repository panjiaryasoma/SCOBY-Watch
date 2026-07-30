from __future__ import annotations


EXPECTED_RESPONSE_FIELDS = {
    "batch_id",
    "recipe_id",
    "tea_type",
    "day",
    "room_temp_c",
    "humidity_percent",
    "ph",
    "brix",
    "rule_status",
    "ml_status",
    "ml_confidence",
    "final_status",
    "decision_reason",
    "rule_triggered",
    "risk_flag",
    "recommendation",
}


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "SCOBY Watch ML Hybrid API is running."
    }


def test_health_endpoint_reports_loaded_model(client):
    response = client.get("/health")
    body = response.get_json()

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["model"] == "GradientBoostingClassifier"


def test_predict_endpoint_returns_complete_hybrid_response(
    client,
    valid_payload,
):
    response = client.post("/predict", json=valid_payload)
    body = response.get_json()

    assert response.status_code == 200
    assert EXPECTED_RESPONSE_FIELDS.issubset(body)
    assert body["batch_id"] == valid_payload["batch_id"]
    assert body["rule_status"] == "balanced"
    assert body["ml_status"] == "balanced"
    assert body["final_status"] == "balanced"
    assert 0.0 <= body["ml_confidence"] <= 1.0
    assert body["rule_triggered"] == "R10_balanced_ready_window"
    assert body["risk_flag"] == "normal"


def test_predict_rejects_missing_required_fields(client, valid_payload):
    invalid_payload = dict(valid_payload)
    invalid_payload.pop("ph")

    response = client.post("/predict", json=invalid_payload)
    body = response.get_json()

    assert response.status_code == 400
    assert body["error"] == "Missing required fields"
    assert "ph" in body["missing_fields"]


def test_predict_rejects_non_json_body(client):
    response = client.post(
        "/predict",
        data="not-json",
        content_type="text/plain",
    )
    body = response.get_json()

    assert response.status_code == 400
    assert body["error"] == "Request body must contain a valid JSON object."
