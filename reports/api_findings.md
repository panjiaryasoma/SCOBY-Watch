# API Findings — SCOBY Watch Flask API

**Project:** SCOBY Watch  
**Framework:** Flask  
**Implementation:** `api/app.py`  
**Status:** Endpoints active and automated testing completed  

---

## 1. Purpose

The API provides the inference layer for:

- the rule engine;
- the machine-learning model;
- confidence reporting;
- hybrid decision logic;
- recommendation generation.

The API is used by Node-RED through HTTP POST requests.

---

## 2. Environment

| Component | Value |
|---|---|
| Python | 3.12.7 |
| scikit-learn | 1.6.1 |
| Flask | 3.1.3 |
| flask-cors | 6.0.2 |
| Host | 127.0.0.1 |
| Port | 5000 |

---

## 3. Artifact Loading

The API loads:

```text
models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
└── scoby_watch_feature_columns.pkl
```

The model is loaded when the module is initialized.

Observed output:

```text
Model loaded successfully.
Features: [10 feature names]
```

---

## 4. Endpoints

### `GET /`

Response:

```json
{
  "message": "SCOBY Watch ML Hybrid API is running."
}
```

### `GET /health`

Response:

```json
{
  "status": "ok",
  "model": "GradientBoostingClassifier"
}
```

### `POST /predict`

Accepts a fermentation payload and returns rule, ML, confidence, hybrid status,
reason, risk, and recommendation fields.

---

## 5. Manual Smoke Test

Reference payload:

```json
{
  "batch_id": "KB-TEST-001",
  "recipe_id": "R1",
  "tea_type": "black_tea",
  "sugar_g_per_l": 80,
  "starter_ml": 150,
  "water_volume_l": 1.0,
  "day": 7,
  "room_temp_c": 24.4,
  "humidity_percent": 68.0,
  "ph": 3.56,
  "brix": 7.71
}
```

Result:

```text
rule_status = balanced
ml_status = balanced
ml_confidence = 0.9998
final_status = balanced
rule_triggered = R10_balanced_ready_window
risk_flag = normal
```

---

## 6. Invalid Requests

### Invalid JSON

Result:

```text
HTTP 400
Request body must contain a valid JSON object.
```

### Missing field

Example:

```text
ph is missing
```

Result:

```text
HTTP 400
error = Missing required fields
missing_fields contains ph
```

---

## 7. Automated Test

Command:

```powershell
python -m pytest tests/test_api.py -v
```

Result:

```text
5 passed, 6 warnings in 1.96s
```

Tests:

```text
test_root_endpoint
test_health_endpoint_reports_loaded_model
test_predict_endpoint_returns_complete_hybrid_response
test_predict_rejects_missing_required_fields
test_predict_rejects_non_json_body
```

---

## 8. Debug Mode

The previous development configuration used:

```python
debug=True
```

This causes:

- automatic reload;
- model loading by the reloader;
- interactive debugger activation;
- debugger PIN output.

For a public repository, `debug=False` is safer as the default.

---

## 9. Findings

- The model loads successfully.
- The root endpoint is active.
- The health endpoint reports the model.
- The prediction endpoint returns a complete hybrid response.
- Invalid JSON is rejected.
- Missing fields are rejected.
- Feature order remains consistent.
- The reference payload produces the expected output.

---

## 10. Limitations

1. Flask development server only.
2. No authentication.
3. No rate limiting.
4. CORS is enabled.
5. Full numeric-range validation is not implemented.
6. Full enum validation is not implemented.
7. Unknown categories can produce a generic HTTP 500 response.
8. No production WSGI server is configured.
9. No structured production logging is available.
10. No load testing has been performed.

---

## 11. Conclusion

The Flask API successfully provides an inference contract that can be used by
Node-RED and Flask's test client.

The API satisfies the local-prototype objective but is not production-ready.
