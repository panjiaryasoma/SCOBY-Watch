# System Architecture — SCOBY Watch

## 1. Summary

SCOBY Watch uses a simulation-first architecture to validate the IoT and
decision-support workflow before physical sensors are available.

Main flow:

```text
Wokwi ESP32
→ MQTT broker
→ Node-RED
→ Flask API
→ Rule Model + ML Baseline
→ Hybrid Decision Layer
→ Node-RED Dashboard
```

---

## 2. System Layers

### 2.1 Simulation Layer

Components:

```text
wokwi/
├── sketch.ino
├── diagram.json
├── libraries.txt
└── wokwi-project.txt or wokwi.toml
```

Responsibilities:

- simulate an ESP32;
- read DHT22 input;
- receive analog pH input;
- receive analog Brix input;
- construct a JSON payload;
- publish the payload through MQTT.

The Wokwi pH and Brix values are simulated analog values, not calibrated
physical-sensor measurements.

---

### 2.2 Messaging Layer

Prototype configuration:

| Field | Value |
|---|---|
| Broker | `broker.emqx.io` |
| Port | `1883` |
| Topic | `scobywatch/panji/sensor` |
| QoS | `0` |

Responsibilities:

- receive Wokwi payloads;
- forward them to Node-RED.

The public broker is used for demonstration. No guarantees are provided for
authentication, encryption, retention, availability, or isolation.

---

### 2.3 Middleware Layer

Component:

```text
node-red/
└── SCOBY Watch Flask Hybrid.json
```

Responsibilities:

1. receive the MQTT payload;
2. parse JSON;
3. prepare a Flask request;
4. send an HTTP POST request to `/predict`;
5. receive the hybrid response;
6. separate the response fields;
7. route values to the dashboard;
8. provide manual inject nodes for testing.

---

### 2.4 Decision Service

Component:

```text
api/app.py
```

Logical subcomponents:

```text
Rule Model v1.1
ML input preparation
Gradient Boosting inference
ML confidence
Hybrid Decision Layer
Recommendation mapping
```

Endpoints:

```text
GET /
GET /health
POST /predict
```

---

### 2.5 Model Artifact Layer

Components:

```text
models/
├── scoby_watch_best_group_split_model.pkl
├── scoby_watch_label_encoders.pkl
├── scoby_watch_feature_columns.pkl
└── metadata.json
```

The artifacts are loaded once when the API module is initialized.

---

### 2.6 Visualization Layer

The Node-RED dashboard displays:

#### Sensors

- temperature;
- humidity;
- pH;
- Brix.

#### Metadata

- batch ID;
- recipe;
- tea type;
- day.

#### Decision

- rule status;
- ML status;
- ML confidence;
- final status;
- risk flag;
- triggered rule;
- decision reason;
- recommendation.

---

## 3. Payload Contract

Main payload:

```json
{
  "batch_id": "KB-WOKWI-001",
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

This contract is used between:

```text
Wokwi
Node-RED
Flask API
```

---

## 4. Decision Flow

```text
Input payload
    ↓
Rule Model v1.1
    ↓
rule_status, rule_triggered, risk_flag
    ↓
Feature encoding
    ↓
Gradient Boosting
    ↓
ml_status, ml_confidence
    ↓
Hybrid Decision Layer
    ↓
final_status, decision_reason, recommendation
```

---

## 5. Hybrid Priority

Decision order:

1. `temperature_warning` from the rule engine has priority.
2. `ml_confidence < 0.70` produces `manual_check`.
3. If the rule and ML agree, the shared status is preserved.
4. A conflict involving `too_sour` produces `manual_check`.
5. Any other conflict produces `manual_check`.

The hybrid layer is not a majority-voting mechanism.

---

## 6. Repository Mapping

| Architecture component | Directory |
|---|---|
| dataset and generator | `data/`, `src/` |
| model artifacts | `models/` |
| experiments | `experiments/` |
| Flask service | `api/` |
| Node-RED | `node-red/` |
| Wokwi | `wokwi/` |
| automated tests | `tests/` |
| findings | `reports/` |
| technical documentation | `docs/` |
| evidence | `supplementary/` |

---

## 7. Failure Behavior

### API Unavailable

Node-RED cannot obtain the hybrid response.

### MQTT Unavailable

The live Wokwi payload does not reach Node-RED.

### Invalid JSON

The API returns HTTP 400 when the body is not a JSON object.

### Missing Field

The API returns HTTP 400 and a list of missing fields.

### Low ML Confidence

The Hybrid Decision Layer returns `manual_check`.

### Rule and ML Conflict

The Hybrid Decision Layer returns `manual_check`.

### Temperature Warning

The rule warning is preserved even when ML produces another status.

---

## 8. Current Limitations

- no database;
- no message persistence;
- no authentication;
- unencrypted MQTT;
- development-oriented Flask service;
- desktop-oriented dashboard;
- no automated end-to-end test that launches Wokwi, MQTT, Node-RED, and Flask together;
- no physical-sensor validation;
- no production monitoring.

---

## 9. Future Architecture

A future version may add:

```text
physical sensors
→ calibrated acquisition layer
→ secure MQTT
→ persistent time-series storage
→ production inference service
→ authenticated dashboard
→ empirical model
→ drift monitoring
```

Those components must not be described as available in the current
repository version.
