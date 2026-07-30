# Integration Testing Findings — SCOBY Watch

**Project:** SCOBY Watch  
**Flow:** Wokwi → MQTT → Node-RED → Flask → Hybrid Decision → Dashboard  
**Status:** End-to-end prototype integration manually verified  

---

## 1. Purpose

Integration testing verifies that all components can exchange data using a
consistent payload contract.

Components:

- Wokwi ESP32;
- MQTT broker;
- Node-RED;
- Flask API;
- model artifacts;
- Rule Model v1.1;
- Hybrid Decision Layer;
- dashboard.

---

## 2. Tested Architecture

```text
Wokwi ESP32
    ↓ MQTT JSON
broker.emqx.io
    ↓
Node-RED
    ↓ HTTP POST
Flask /predict
    ↓
Rule + ML + Hybrid
    ↓ JSON response
Node-RED dashboard
```

---

## 3. MQTT Configuration

| Field | Value |
|---|---|
| Broker | `broker.emqx.io` |
| Port | 1883 |
| Topic | `scobywatch/panji/sensor` |
| QoS | 0 |

A public broker is used for the prototype.

---

## 4. Payload

The payload includes:

```text
batch_id
recipe_id
tea_type
sugar_g_per_l
starter_ml
water_volume_l
day
room_temp_c
humidity_percent
ph
brix
```

Node-RED forwards the payload to:

```text
POST http://127.0.0.1:5000/predict
```

---

## 5. Node-RED Processing

The flow performs the following steps:

1. receives the MQTT payload;
2. parses JSON;
3. prepares the HTTP request;
4. sends the request to Flask;
5. receives the hybrid response;
6. separates response fields;
7. converts numeric and text fields;
8. sends values to the dashboard;
9. displays the raw response in a debug node.

A manual inject node is also available for testing without Wokwi.

---

## 6. Dashboard Output

### Sensors

- temperature gauge;
- humidity gauge;
- pH gauge;
- Brix gauge.

### Trends

- temperature chart;
- humidity chart;
- pH chart;
- Brix chart.

### Metadata

- batch ID;
- recipe;
- tea type;
- fermentation day.

### Decision

- rule status;
- ML status;
- ML confidence;
- final status;
- risk flag;
- triggered rule;
- decision reason;
- recommendation.

---

## 7. Flask Integration

Health check:

```text
GET /health
status = ok
model = GradientBoostingClassifier
```

Prediction smoke test:

```text
rule_status = balanced
ml_status = balanced
final_status = balanced
confidence ≈ 0.9998
```

The response contract is successfully received by Node-RED.

---

## 8. Verified Scenarios

- normal early fermentation;
- still-sweet condition;
- balanced condition;
- too-sour condition;
- high-temperature warning;
- low-temperature manual check;
- low-confidence fallback;
- ordinary disagreement;
- conflict involving `too_sour`;
- forced temperature override.

---

## 9. Evidence

Evidence is available under:

```text
supplementary/
```

The evidence includes:

- Wokwi simulation;
- MQTT configuration;
- Node-RED nodes;
- Flask health response;
- Flask prediction response;
- final flow;
- sensor dashboard;
- hybrid-output dashboard.

This evidence is implementation and simulation evidence.

It is not laboratory validation.

---

## 10. Findings

- The payload can be transmitted.
- Node-RED can receive and parse the payload.
- Flask can process the payload.
- Rule, ML, confidence, and hybrid outputs are available.
- The response can be routed to the dashboard.
- Manual inject supports deterministic testing.
- The dashboard can display sensor and decision fields.

---

## 11. Limitations

1. Public MQTT broker.
2. QoS 0.
3. No TLS.
4. No authentication.
5. No persistent messaging.
6. No database.
7. No delayed-message testing.
8. No duplicate-message testing.
9. No network-recovery testing.
10. No automated full-stack test.
11. Desktop-oriented dashboard.
12. Wokwi pH and Brix remain simulated.
13. Flask remains a local development service.

---

## 12. Conclusion

End-to-end integration is successful for the scope of the simulation-first
prototype.

The result shows that data can move from the simulator to the dashboard and
produce confidence-aware hybrid output.

The result does not demonstrate production reliability or physical-sensor
validity.
