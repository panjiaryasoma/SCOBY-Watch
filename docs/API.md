# Flask API Documentation — SCOBY Watch

## 1. Summary

The Flask API provides the inference layer for:

- Rule Model v1.1;
- the machine-learning baseline;
- the Hybrid Decision Layer;
- recommendation generation.

Implementation location:

```text
api/app.py
```

Local address:

```text
http://127.0.0.1:5000
```

The current API is a local development service, not a production API.

---

## 2. Running the API

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run from the repository root:

```powershell
python api/app.py
```

Expected output:

```text
Model loaded successfully.
Running on http://127.0.0.1:5000
```

---

## 3. Loaded Artifacts

The API loads:

```text
models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
└── scoby_watch_feature_columns.pkl
```

Paths should be resolved from the location of `app.py`, not from the current
terminal working directory.

Recommended pattern:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
```

---

## 4. Endpoints

### 4.1 `GET /`

Purpose:

- verify that the service is active;
- provide a short service identifier.

Response:

```json
{
  "message": "SCOBY Watch ML Hybrid API is running."
}
```

Status:

```text
200 OK
```

---

### 4.2 `GET /health`

Purpose:

- verify that the model was loaded;
- report the active model type.

Response:

```json
{
  "status": "ok",
  "model": "GradientBoostingClassifier"
}
```

Status:

```text
200 OK
```

---

### 4.3 `POST /predict`

Purpose:

- run rule inference;
- run ML inference;
- compute confidence;
- run hybrid decision logic;
- generate a recommendation.

#### Request Fields

| Field | Type | Required | Example |
|---|---|---:|---|
| `batch_id` | string | yes | `KB-TEST-001` |
| `recipe_id` | string | yes | `R1` |
| `tea_type` | string | yes | `black_tea` |
| `sugar_g_per_l` | number | yes | `80` |
| `starter_ml` | number | yes | `150` |
| `water_volume_l` | number | yes | `1.0` |
| `day` | integer | yes | `7` |
| `room_temp_c` | number | yes | `24.4` |
| `humidity_percent` | number | yes | `68.0` |
| `ph` | number | yes | `3.56` |
| `brix` | number | yes | `7.71` |

Example request:

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

#### Response Fields

| Field | Description |
|---|---|
| `batch_id` | Batch identifier from the request |
| `recipe_id` | Recipe identifier |
| `tea_type` | Tea category |
| `day` | Fermentation day |
| `room_temp_c` | Temperature |
| `humidity_percent` | Humidity |
| `ph` | pH value |
| `brix` | Brix value |
| `rule_status` | Rule-engine output |
| `ml_status` | ML output |
| `ml_confidence` | ML confidence |
| `final_status` | Hybrid output |
| `decision_reason` | Explanation of the hybrid decision |
| `rule_triggered` | Active rule |
| `risk_flag` | Risk category |
| `recommendation` | Final recommendation |

Example response:

```json
{
  "batch_id": "KB-TEST-001",
  "recipe_id": "R1",
  "tea_type": "black_tea",
  "day": 7,
  "room_temp_c": 24.4,
  "humidity_percent": 68.0,
  "ph": 3.56,
  "brix": 7.71,
  "rule_status": "balanced",
  "ml_status": "balanced",
  "ml_confidence": 0.9998,
  "final_status": "balanced",
  "decision_reason": "Rule-based and ML model agree on the same fermentation status.",
  "rule_triggered": "R10_balanced_ready_window",
  "risk_flag": "normal",
  "recommendation": "Start taste testing and consider bottling if the flavor matches preference."
}
```

---

## 5. Error Behavior

### 5.1 Body Is Not a JSON Object

Request:

```text
Content-Type: text/plain
Body: not-json
```

Response:

```json
{
  "error": "Request body must contain a valid JSON object."
}
```

Status:

```text
400 Bad Request
```

### 5.2 Missing Required Field

Example: the `ph` field is missing.

Response:

```json
{
  "error": "Missing required fields",
  "missing_fields": ["ph"]
}
```

Status:

```text
400 Bad Request
```

### 5.3 Invalid Category or Value

The current implementation does not yet provide complete schema validation
for:

- recipe enums;
- tea-type enums;
- numeric ranges;
- valid day ranges;
- unknown encoder categories.

Unhandled categories or malformed values can reach the generic error handler
and produce HTTP 500.

Before deployment, the following improvements are required:

- explicit enum validation;
- numeric-range validation;
- structured 4xx errors;
- schema validation;
- input sanitization.

---

## 6. Manual PowerShell Testing

### Health Check

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/health" `
  -Method Get
```

### Prediction

```powershell
$body = @{
    batch_id           = "KB-TEST-001"
    recipe_id          = "R1"
    tea_type           = "black_tea"
    sugar_g_per_l      = 80
    starter_ml         = 150
    water_volume_l     = 1.0
    day                = 7
    room_temp_c        = 24.4
    humidity_percent   = 68.0
    ph                 = 3.56
    brix               = 7.71
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/predict" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

---

## 7. Automated Testing

```powershell
python -m pytest tests/test_api.py -v
```

Current result:

```text
5 passed, 6 warnings
```

The test suite covers:

- root endpoint;
- health endpoint;
- valid prediction;
- missing required field;
- invalid JSON.

---

## 8. Development Mode

`debug=True` enables:

- automatic reload;
- detailed tracebacks;
- the interactive debugger.

This mode is acceptable for local development on:

```text
127.0.0.1
```

It must not be used on a public server.

The repository version should use:

```python
app.run(
    host="127.0.0.1",
    port=5000,
    debug=False,
)
```

or control debug behavior through an environment variable.

---

## 9. Production Boundary

The current API:

- uses the Flask development server;
- has no authentication;
- has no rate limiting;
- has no production logging;
- has no persistent storage;
- enables CORS;
- has not been tested under high concurrency;
- has not been tested on a public deployment;
- does not use a production WSGI server.

Therefore, it must not be described as production-ready.

---

## 10. Pickle Security

The model is loaded through joblib/pickle.

Rules:

- load artifacts only from the official repository;
- never load pickle files from untrusted sources;
- pin dependencies;
- retrain the model if compatibility cannot be guaranteed.

---

## 11. Claim Boundary

The API response is readiness-oriented decision support.

It is not:

- a food-safety certification;
- a microbial-safety result;
- a laboratory conclusion;
- medical advice;
- a guarantee that a batch is safe to consume.
